"""Validate the delivered GLB by inspecting it and reimporting into Blender.

Run after export, preferably in a fresh Blender process:
  blender --background --factory-startup --python-exit-code 1 \
    --python Tools/Blender/validate_paladin_elite.py

Optional positional argument after ``--`` overrides the input GLB. The report
always lands beside the asset's validation_elite.json, as validation_export.json.
No model, texture or source scene is changed. Validation does not claim that the
static, layered presentation model is watertight, rigged or production ready.
"""

from __future__ import annotations

import json
import math
import struct
import sys
from pathlib import Path

import bpy
import numpy as np
from mathutils import Vector


ROOT = Path(__file__).resolve().parents[2]
ASSET = ROOT / 'Assets/Characters/Enemies/PaladinElite'
DEFAULT_GLB = ASSET / 'Exports/PaladinElite.glb'
REPORT = ASSET / 'validation_export.json'
EXPECTED_MATERIALS = {'Elite.steel', 'Elite.dark_steel', 'Elite.gold',
                      'Elite.black', 'Elite.leather'}


def inspect_container(path: Path, errors: list, warnings: list) -> dict:
    raw = path.read_bytes()
    if len(raw) < 20:
        raise ValueError('GLB is too short to contain a valid header')
    magic, version, length = struct.unpack_from('<4sII', raw, 0)
    if magic != b'glTF' or version != 2 or length != len(raw):
        raise ValueError('Invalid GLB 2.0 header or declared file length')
    cursor, document, binary, chunks = 12, None, None, []
    while cursor < len(raw):
        if cursor + 8 > len(raw):
            raise ValueError('Truncated GLB chunk header')
        size, kind = struct.unpack_from('<II', raw, cursor)
        start = cursor + 8
        end = start + size
        if end > len(raw) or size % 4:
            raise ValueError('Truncated or unaligned GLB chunk')
        chunk = raw[start:end]
        chunks.append({'type': kind, 'bytes': size})
        if kind == 0x4E4F534A:
            document = json.loads(chunk.decode('utf-8').rstrip('\x00 \r\n\t'))
        elif kind == 0x004E4942:
            binary = chunk
        cursor = end
    if document is None or binary is None:
        raise ValueError('GLB must contain JSON and embedded binary chunks')

    external = []
    for category in ('buffers', 'images'):
        for item in document.get(category, []):
            uri = item.get('uri')
            if uri and not uri.startswith('data:'):
                external.append({'type': category, 'uri': uri})
    if external:
        errors.append('GLB references external images or buffers')
    for buffer in document.get('buffers', []):
        if not buffer.get('uri') and buffer.get('byteLength', 0) > len(binary):
            errors.append('Embedded buffer declares more bytes than its BIN chunk')
    views = document.get('bufferViews', [])
    for view in views:
        if not document.get('buffers', [])[view.get('buffer', 0)].get('uri'):
            if view.get('byteOffset', 0) + view['byteLength'] > len(binary):
                errors.append('A bufferView extends beyond the embedded BIN chunk')
    image_info = []
    for im in document.get('images', []):
        embedded = 'bufferView' in im or im.get('uri', '').startswith('data:')
        info = {'name': im.get('name', ''), 'mime_type': im.get('mimeType'),
                'embedded': embedded}
        if 'bufferView' in im:
            view = views[im['bufferView']]
            data = binary[view.get('byteOffset', 0):view.get('byteOffset', 0)+view['byteLength']]
            info['bytes'] = len(data)
            if not data:
                errors.append('An embedded texture has no data')
            if im.get('mimeType') == 'image/png' and not data.startswith(b'\x89PNG\r\n\x1a\n'):
                errors.append('An embedded PNG texture has an invalid signature')
            if im.get('mimeType') == 'image/jpeg' and not data.startswith(b'\xff\xd8'):
                errors.append('An embedded JPEG texture has an invalid signature')
        if not embedded:
            errors.append('Image is missing embedded image content')
        image_info.append(info)

    materials = document.get('materials', [])
    names = {m.get('name', '') for m in materials}
    for name in EXPECTED_MATERIALS:
        if name not in names:
            errors.append('Missing elite material: ' + name)
    material_info = []
    for mat in materials:
        pbr = mat.get('pbrMetallicRoughness', {})
        info = {'name': mat.get('name', ''),
                'base_color_texture': 'baseColorTexture' in pbr,
                'metallic_roughness_texture': 'metallicRoughnessTexture' in pbr,
                'normal_texture': 'normalTexture' in mat,
                'metallic_factor': pbr.get('metallicFactor', 1.0),
                'roughness_factor': pbr.get('roughnessFactor', 1.0)}
        if mat.get('name') in EXPECTED_MATERIALS:
            if not all(info[k] for k in ('base_color_texture', 'metallic_roughness_texture', 'normal_texture')):
                errors.append('PBR texture channel lost in export: ' + mat['name'])
        material_info.append(info)
    if not document.get('meshes'):
        errors.append('GLB contains no meshes')
    if document.get('cameras') or 'KHR_lights_punctual' in document.get('extensions', {}):
        errors.append('GLB contains studio cameras or lights')
    for node in document.get('nodes', []):
        if 'studio' in node.get('name', '').lower():
            errors.append('Studio object included in GLB: ' + node['name'])
    return {'file_bytes': len(raw), 'chunks': chunks,
            'embedded_images': image_info, 'external_references': external,
            'materials': material_info, 'mesh_count': len(document.get('meshes', [])),
            'animation_count': len(document.get('animations', [])),
            'skin_count': len(document.get('skins', []))}


def inspect_reimport(path: Path, errors: list, warnings: list) -> dict:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(path))
    meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    if not meshes:
        raise ValueError('GLB import produced no mesh objects')
    unexpected = [o.name for o in bpy.context.scene.objects if o.type in {'CURVE', 'LIGHT', 'CAMERA'}]
    if unexpected:
        errors.append('Unexpected imported object types: ' + ', '.join(unexpected))
    points = [o.matrix_world @ Vector(c) for o in meshes for c in o.bound_box]
    minimum = [min(c[i] for c in points) for i in range(3)]
    maximum = [max(c[i] for c in points) for i in range(3)]
    dimensions = [maximum[i]-minimum[i] for i in range(3)]
    if not all(math.isfinite(x) for x in minimum+maximum):
        errors.append('Imported model bounds contain non-finite values')
    if not 2.00 <= dimensions[2] <= 2.35:
        errors.append('Imported character height is outside expected 2.00–2.35 metres')
    if not 0.70 <= dimensions[0] <= 1.75 or not .30 <= dimensions[1] <= 1.35:
        warnings.append('Character width/depth is outside the expected presentation envelope')
    if abs(minimum[2]) > .05:
        warnings.append('Feet or fabric extend more than 5 cm from the ground plane')

    triangles = vertices = polygons = 0
    missing_uv, missing_material, invalid_geometry = [], [], []
    used_materials = set()
    for obj in meshes:
        mesh = obj.data
        if obj.name.startswith('Elite_Cape'):
            corners = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
            extent = [max(p[i] for p in corners)-min(p[i] for p in corners) for i in range(3)]
            if extent[0] > 1.05 or extent[1] > .55:
                errors.append('Cape has an unexpected long spike or thickness extrusion: ' + obj.name)
        vertices += len(mesh.vertices)
        polygons += len(mesh.polygons)
        mesh.calc_loop_triangles()
        triangles += len(mesh.loop_triangles)
        co = np.empty(len(mesh.vertices)*3, dtype=np.float32)
        mesh.vertices.foreach_get('co', co)
        if not np.isfinite(co).all() or not len(mesh.polygons):
            invalid_geometry.append(obj.name)
        if not mesh.uv_layers:
            missing_uv.append(obj.name)
        if not obj.material_slots or not any(s.material for s in obj.material_slots):
            missing_material.append(obj.name)
        for slot in obj.material_slots:
            if slot.material:
                used_materials.add(slot.material)
    if invalid_geometry:
        errors.append('Empty or non-finite geometry in ' + ', '.join(invalid_geometry[:12]))
    if missing_uv:
        errors.append('Missing UV layers in ' + ', '.join(missing_uv[:12]))
    if missing_material:
        errors.append('Missing material assignments in ' + ', '.join(missing_material[:12]))
    if triangles < 100000:
        errors.append('Unexpectedly little geometry: detailed body or ornament may be missing')
    used_images = set()
    for mat in used_materials:
        if mat.use_nodes:
            for node in mat.node_tree.nodes:
                if node.type == 'TEX_IMAGE' and node.image:
                    used_images.add(node.image)
    loaded_images = []
    for im in sorted(used_images, key=lambda x: x.name):
        # The importer defers pixel decoding until a texture is actually read.
        # Exercise that load, rather than mistaking a lazy packed image for loss.
        try:
            first_pixel = tuple(im.pixels[:4])
        except Exception as exc:
            errors.append('Texture pixels cannot be decoded: ' + im.name + ': ' + str(exc))
            first_pixel = ()
        has_data = bool(im.has_data and im.size[0] > 0 and im.size[1] > 0)
        packed = bool(im.packed_file)
        loaded_images.append({'name': im.name, 'size': list(im.size),
                              'has_data': has_data, 'packed': packed})
        if not has_data:
            errors.append('Texture did not load after GLB import: ' + im.name)
        if not packed and im.source == 'FILE' and not Path(bpy.path.abspath(im.filepath)).is_file():
            errors.append('Imported material depends on a missing texture file: ' + im.name)
    if not loaded_images:
        errors.append('No image textures survived GLB import')
    return {'mesh_objects': len(meshes), 'vertices': vertices, 'polygons': polygons,
            'triangles': triangles, 'materials': sorted(m.name for m in used_materials),
            'images': loaded_images, 'missing_uv_objects': missing_uv,
            'missing_material_objects': missing_material,
            'bounds_m': {'minimum': minimum, 'maximum': maximum, 'dimensions': dimensions}}


def main():
    args = sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
    source = Path(args[0]).resolve() if args else DEFAULT_GLB
    errors, warnings = [], []
    report = {'asset': 'PaladinElite', 'input': str(source),
              'validation': 'GLB binary inspection and clean Blender reimport',
              'errors': errors, 'warnings': warnings,
              'scope': ['Static presentation geometry', 'No rig or animation validation',
                        'Visual correspondence, cloth tears and layered intersections require visual review']}
    try:
        report['container'] = inspect_container(source, errors, warnings)
        report['reimport'] = inspect_reimport(source, errors, warnings)
    except Exception as exc:
        errors.append(f'{type(exc).__name__}: {exc}')
    report['status'] = 'failed' if errors else 'passed'
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    print('ELITE_EXPORT_VALIDATION=' + json.dumps(report, ensure_ascii=False), flush=True)
    if errors:
        raise RuntimeError('PaladinElite GLB validation failed; see ' + str(REPORT))


if __name__ == '__main__':
    main()

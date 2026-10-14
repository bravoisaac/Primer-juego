"""V3: closed visor, overlapping arm plates and less uniform draped cloth.

Local Blender geometry. Preserve every earlier version in its own directory.
"""
import sys
import math
from pathlib import Path
import bpy
from mathutils import Vector

sys.path.insert(0,str(Path(__file__).parent))
import refine_paladin_elite_base as v2
base=v2.base
shapes=base.shapes
panel=v2.panel
PI=math.pi
TAU=math.tau
OUT=base.OUT.parent/'V3'
build_v2_armor=v2.primary_armor
build_v2_cloth=v2.cloth
build_v2_body=v2.body_and_boots


def remove_generated(tokens):
    for obj in list(shapes.C['armor'].objects):
        if any(token in obj.name for token in tokens):
            bpy.data.objects.remove(obj,do_unlink=True)


def armor():
    build_v2_armor()
    remove_generated(('V2_Hombrera','V2_Brazo_lama','V2_Rodillera'))
    for side in (-1,1):
        tag='L' if side>0 else 'R'
        def shoulder(u,v,side=side):
            a=u*TAU;t=v*(1.55+.12*math.cos(a));r=math.sin(t)
            x=side*(.314+.202*r*math.cos(a))
            depth=.173-.013*math.sin(a)
            y=.009+depth*r*math.sin(a)
            z=1.672+.153*math.cos(t)-.031*r*max(0,math.cos(a))
            # A wide front dome sweeps down over the outer arm.
            z+=.015*math.sin(PI*v)*math.cos(a*2)
            return Vector((x,y,z))
        panel(tag+'_V3_Hombrera_boveda',shoulder,64,28,.006,closed=True,flip=side>0)
        def shoulder_lip(u,v):
            p=shoulder(u,.944+.056*v)
            normal=Vector((p.x-side*.314,p.y-.009,.04)).normalized()
            return p+normal*(.001+.002*math.sin(PI*v))
        panel(tag+'_V3_Hombrera_borde_doblado',shoulder_lip,64,6,.003,closed=True,flip=side>0)
        # All four plates share one axis and one taper, preventing the diagonal
        # intersections produced by independent cylinders in the earlier pass.
        top=Vector((side*.329,.014,1.710));bottom=Vector((side*.425,-.014,1.343))
        axis=(top-bottom).normalized()
        lateral=Vector((1,0,0));lateral=(lateral-axis*lateral.dot(axis)).normalized()
        front=axis.cross(lateral)
        if front.y>0:front=-front
        for j in range(4):
            def lame(u,v,j=j):
                a=(u-.5)*TAU;t=.17+j*.175+.224*(1-v)
                if j==0:t-=.085*v**4
                rx=.147-.056*t+.003*(3-j)
                ry=.140-.050*t+.003*(3-j)
                p=top.lerp(bottom,t)+lateral*(rx*math.sin(a))+front*(ry*math.cos(a))
                p.z+=.004*math.cos(a)*(1-v)**4
                return p
            panel(tag+f'_V3_Brazo_lama_{j+1}',lame,48,16,.004,closed=True)
        def knee(u,v,side=side):
            q=2*u-1;w=.082+.018*math.sin(PI*v)
            lo=.534+.045*abs(q)**1.4;hi=.742-.029*abs(q)**1.3
            y=-.110-.047*(1-q*q)*math.sin(PI*v)**.65
            y-=.007*(1-abs(q))*math.sin(PI*v)
            return Vector((side*.181+q*w,y,lo+(hi-lo)*v))
        panel(tag+'_V3_Rodillera_placa_convexa',knee,40,32,.005)
        # A modest turned hem is part of the plate construction, not engraving.
        panel(tag+'_V3_Rodillera_borde_inferior',lambda u,v:knee(u,.045*v)+Vector((0,-.002,0)),40,4,.002)
    # Functional waist buckle: four plain bars, with no crest or ornament.
    for name,loc,size in [
        ('Superior',(0,-.195,1.236),(.060,.009,.006)),
        ('Inferior',(0,-.195,1.195),(.060,.009,.006)),
        ('Izquierda',(-.027,-.195,1.216),(.006,.009,.045)),
        ('Derecha',(.027,-.195,1.216),(.006,.009,.045)),
        ('Aguja',(0,-.200,1.216),(.004,.004,.032)),
    ]:
        bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
        obj=shapes.put(bpy.context.object,'V3_Hebilla_'+name,base.ARMOR)
        obj.scale=size;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
        bevel=obj.modifiers.new('Aristas de hebilla','BEVEL');bevel.width=.002;bevel.segments=3


def helmet():
    # Sixteen broad forging facets meet at a restrained pointed crown.
    rings=[(1.817,.104,.117),(1.889,.127,.141),(1.989,.145,.153),
           (2.043,.141,.151),(2.097,.110,.123),(2.145,.056,.067),(2.186,.0,.0)]
    n=16;verts=[];faces=[];uv=[]
    for j,(z,rx,ry) in enumerate(rings[:-1]):
        for i in range(n):
            a=i*TAU/n
            verts.append((rx*math.sin(a),-ry*math.cos(a),z));uv.append((i/n,j/(len(rings)-1)))
    for j in range(len(rings)-2):
        for i in range(n):
            a=j*n+i;b=j*n+(i+1)%n;faces.append((a,b,b+n,a+n))
    apex=len(verts);verts.append((0,0,rings[-1][0]));uv.append((.5,1))
    for i in range(n):faces.append(((len(rings)-2)*n+i,(len(rings)-2)*n+(i+1)%n,apex))
    skull=shapes.mesh('V3_Casco_calota_facetada',verts,faces,base.ARMOR,uv=uv)
    # Smooth the forging between the crown stations without displaying a
    # network of bevels across what should be one continuous metal shell.
    smooth=skull.modifiers.new('Curvatura continua de la calota','SUBSURF')
    smooth.levels=2;smooth.render_levels=2
    s=skull.modifiers.new('Grosor del casco','SOLIDIFY');s.thickness=.005;s.offset=-1
    def mask(u,v):
        q=2*u-1;a=q*1.25
        lo=1.822+.052*abs(q)**1.25;hi=2.000+.005*(1-abs(q))
        x=(.111+.033*v)*math.sin(a)
        y=-(.132+.023*v)*math.cos(a)-(.035-.010*v)*(1-abs(q))
        y-=.010*math.sin(PI*v)*(1-q*q)
        return Vector((x,y,lo+(hi-lo)*v))
    # Actual holes in the visor, with a recessed dark liner underneath.
    nu=64;nv=40;vs=[];uv=[];fs=[]
    vent_columns=set()
    for start in (7,13,19,43,49,55):vent_columns.update(range(start,start+2))
    for j in range(nv+1):
        for i in range(nu+1):
            vs.append(mask(i/nu,j/nv));uv.append((i/nu,j/nv))
    for j in range(nv):
        for i in range(nu):
            if i in vent_columns and 14<=j<20:continue
            k=j*(nu+1)+i;fs.append((k,k+1,k+nu+2,k+nu+1))
    obj=shapes.mesh('V3_Casco_visor_perforado',vs,fs,base.ARMOR,uv=uv)
    s=obj.modifiers.new('Grosor alrededor de respiraderos','SOLIDIFY');s.thickness=.004;s.offset=-1
    panel('V3_Casco_interior_oscuro',lambda u,v:mask(u,v)+Vector((0,.009,0)),48,28,.001,base.DARK)
    def brow(u,v):
        q=2*u-1;a=q*1.34
        lo=2.013+.006*(1-abs(q));hi=2.057+.048*max(0,1-abs(q)*1.6)
        y=-(.175-.041*v)*math.cos(a)-.013*(1-abs(q))
        return Vector(((.151-.026*v)*math.sin(a),y,lo+(hi-lo)*v))
    panel('V3_Casco_ceja_en_punta',brow,48,24,.005)
    panel('V3_Casco_ranura_ocular',lambda u,v:Vector((.143*math.sin((u-.5)*2.5),
            -.170*math.cos((u-.5)*2.5)-.006,2.003+.015*v)),48,4,.001,base.DARK)
    # Plain functional hinge caps locate the visor at the temples.
    for side in (-1,1):
        bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=.014,depth=.005,
                                           location=(side*.142,-.012,2.005),rotation=(0,PI/2,0))
        obj=shapes.put(bpy.context.object,('L' if side>0 else 'R')+'_V3_Casco_pivote',base.ARMOR)
        b=obj.modifiers.new('Canto del pivote','BEVEL');b.width=.0015;b.segments=2


def textiles():
    build_v2_cloth()
    remove_generated(('Tela_Cuello_base','V2_Capa','Tela_Faldon_base'))
    def cowl(u,v):
        a=u*TAU;front=max(0,math.cos(a))
        phase=TAU*2.3*v+.7*math.sin(a)+.4*math.sin(2*a+.8)
        fold=.014*math.sin(phase)*math.sin(PI*v)**.5
        rx=.136+.086*v+fold;ry=.132+.092*v+fold
        z=1.856-.132*v-.052*front**2*v+.014*math.sin(a+.5)*math.sin(PI*v)
        z+=.007*math.sin(a*3+v*5)*math.sin(PI*v)
        return Vector((rx*math.sin(a),.008-ry*math.cos(a),z))
    panel('V3_Tela_cuello_drapeado',cowl,96,56,.002,base.CLOTH,closed=True,flip=True)
    def cape(u,v):
        q=2*u-1;w=.247+.171*v**.65
        phase=q*PI*(3.5+.3*v)+.35*math.sin(v*4+q)
        wave=math.cos(phase)+.33*math.cos(phase*1.71+.9)
        amp=.007+.025*math.sin(PI*v*.85)
        z=1.762-1.449*v-.042*abs(q)**1.5*(1-v)**3
        z+=(.024*math.sin(q*7+.7)+.012*math.sin(q*14))*(v**6)
        x=q*w+.014*math.sin(v*4+q*2)*v**2
        y=.172+.172*v+amp*wave-.036*abs(q)**4*(1-v)**3
        return Vector((x,y,z))
    panel('V3_Tela_capa_caida_irregular',cape,72,88,.002,base.CLOTH)
    for side in (-1,1):
        def tabard(u,v,side=side):
            q=2*u-1;length=.72 if side<0 else .62
            x=side*.072+q*(.065-.010*v)+side*.008*math.sin(v*5)
            z=1.172-length*v+(.014*q+.012*math.sin(q*3+side))*v**6
            y=-.202-.038*v+.015*math.sin(v*5+.3*side)+.008*math.cos(q*4+v*3)*math.sin(PI*v)
            return Vector((x,y,z))
        panel(('L' if side>0 else 'R')+'_V3_Tela_faldon',tabard,32,48,.002,base.CLOTH,flip=True)


def body_and_boots():
    build_v2_body()
    for side in (-1,1):
        # A continuous sole gives the sabaton weight and a flat ground contact.
        outline=[(0,-.255),(.054,-.244),(.082,-.197),(.086,-.088),(.082,.040),(.071,.124),
                 (.036,.145),(-.036,.145),(-.071,.124),(-.082,.040),(-.086,-.088),(-.082,-.197),(-.054,-.244)]
        verts=[];faces=[];n=len(outline)
        for z in (.014,.030):
            verts.extend((side*.210+x,y,z) for x,y in outline)
        for i in range(n):faces.append((i,(i+1)%n,(i+1)%n+n,i+n))
        faces.append(tuple(reversed(range(n))));faces.append(tuple(n+i for i in range(n)))
        obj=shapes.mesh(('L' if side>0 else 'R')+'_V3_Bota_suela',verts,faces,base.DARK)
        bevel=obj.modifiers.new('Suela redondeada','BEVEL');bevel.width=.003;bevel.segments=3


def main():
    # Reuse the validated V2 studio and export pipeline, with explicitly
    # replaced construction stages and a different output directory.
    base.OUT=OUT
    v2.primary_armor=armor;v2.helmet=helmet;v2.cloth=textiles;v2.body_and_boots=body_and_boots
    v2.main()
    scene=bpy.context.scene;camera=scene.camera
    camera.location=(2.2,-5,2.6);shapes.look_at(camera,(0,-.015,1.85))
    camera.data.ortho_scale=.90
    scene.render.filepath=str(OUT/'PaladinElite_Base_Detalle.png')
    bpy.ops.render.render(write_still=True)
    print('BASE_V3_COMPLETE',flush=True)


if __name__=='__main__':main()

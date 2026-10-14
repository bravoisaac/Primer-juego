"""Refine the saved V3 asset into V4 without replacing earlier files.

Editable armor construction, draped cloth and hand protection; local only.
"""
import sys
import math
from pathlib import Path
import bpy
from mathutils import Vector

sys.path.insert(0,str(Path(__file__).parent))
import refine_paladin_elite_base as forms
base=forms.base
shapes=base.shapes
panel=forms.panel
PI=math.pi
TAU=math.tau
ROOT=Path(__file__).resolve().parents[2]
PREVIOUS=ROOT/'Assets/Characters/Enemies/PaladinElite/Base/V3/PaladinElite_Base.blend'
OUT=PREVIOUS.parent.parent/'V4'


def remove_piece(name):
    obj=bpy.data.objects.get(name)
    if obj and shapes.C['armor'] in obj.users_collection:
        bpy.data.objects.remove(obj,do_unlink=True)


def set_color(mat,color):
    mat.diffuse_color=(*color,1)
    for node in mat.node_tree.nodes:
        if node.type=='BSDF_PRINCIPLED':node.inputs['Base Color'].default_value=(*color,1)


def cuirass():
    def breast(u,v):
        a=(u-.5)*2.72
        w=forms.interpolate([(0,.223),(.28,.252),(.65,.278),(1,.253)],v)[0]
        d=forms.interpolate([(0,.166),(.25,.197),(.60,.220),(1,.165)],v)[0]
        keel=.024*max(0,1-abs(a)/.60)*math.sin(PI*(.15+.7*v))
        lo=1.265-.060*math.cos(a)**6
        hi=1.754-.110*abs(math.sin(a))**2-.033*math.exp(-a*a*5)
        return Vector((w*math.sin(a),-d*math.cos(a)-keel,lo+(hi-lo)*v))
    def plackart(u,v):
        a=(u-.5)*2.72
        end=.285+.255*max(0,math.cos(a))**5
        p=breast(u,.055+(end-.055)*v)
        # The breastplate above and the lower plate share their base curvature.
        p.x+=.004*math.sin(a)
        p.y-=.010*math.cos(a)
        return p
    panel('V4_Peto_placa_abdominal',plackart,64,32,.005)
    panel('V4_Peto_labio_superior',lambda u,v:plackart(u,.975+.025*v)+Vector((0,-.0015,0)),64,4,.002)
    # Keep the belt in front of the lower forging; move its matching buckle.
    for obj in shapes.C['armor'].objects:
        if 'Belt_Leather' in obj.name or 'V3_Hebilla' in obj.name:obj.location.y-=.012
    for side in (-1,1):
        tag='L' if side>0 else 'R'
        # A plain side strap secures the front and back cuirass under the arm.
        def strap(u,v,side=side):
            a=side*(.92+.64*u)
            return Vector((.267*math.sin(a),-.178*math.cos(a),1.453+.027*v-.010*u))
        panel(tag+'_V4_Peto_correa_lateral',strap,24,6,.003,base.DARK,flip=side<0)


def arms_and_hands():
    for side in (-1,1):
        tag='L' if side>0 else 'R'
        remove_piece(tag+'_V2_Codera')
        remove_piece(tag+'_Gauntlet_MetacarpalPlate')
        # Recess the soft finger joints below the steel shells.
        for obj in list(shapes.C['armor'].objects):
            if not obj.name.startswith(tag+'_'):continue
            if '_Knuckle_' in obj.name:
                remove_piece(obj.name)
            elif any(token in obj.name for token in ('_FingerJoint_','_ThumbJoint_')):
                center=sum((v.co for v in obj.data.vertices),Vector())/len(obj.data.vertices)
                for vertex in obj.data.vertices:vertex.co=center+.83*(vertex.co-center)
        vambrace=bpy.data.objects.get(tag+'_V2_Brazal_ajustado')
        for vertex in vambrace.data.vertices:
            p=vertex.co;t=max(0,min(1,(p.z-1.20)/.10));factor=1-.07*t
            cx=side*(.460-(.460-.435)*max(0,min(1,(p.z-1.062)/.227)))
            p.x=cx+(p.x-cx)*factor;p.y=-.026+(p.y+.026)*factor
        def elbow(u,v,side=side):
            a=(u-.5)*3.55
            radius=.090+.011*math.sin(PI*v)
            wing=.025*max(0,side*math.sin(a))**6*math.sin(PI*v)
            x=side*.428+radius*math.sin(a)+side*wing
            y=-.015-(.105+.018*math.sin(PI*v))*math.cos(a)
            z=1.317+.071*(2*v-1)*(.77+.23*math.cos(a))
            return Vector((x,y,z))
        panel(tag+'_V4_Codera_envuelta',elbow,48,28,.005)
        for edge in (0,1):
            def lip(u,v,edge=edge):
                p=elbow(u,.035*v if edge==0 else .965+.035*v)
                p.y-=.0015*math.cos((u-.5)*3.55)
                return p
            panel(tag+f'_V4_Codera_borde_{edge}',lip,48,4,.002)
        # Flared wrist cuff and overlapping metacarpal plates leave the
        # individual fingers of the previous model intact.
        forms.fitted_sleeve(tag+'_V4_Guantelete_puno',side,(.460,-.044,1.101),(.461,-.050,1.035),
                            [(0,.066,.070),(.40,.074,.079),(1,.085,.085)],arc=5.6,lip=.005)
        def backhand(u,v,side=side):
            q=2*u-1
            x=side*.4608+.047*q
            y=-.084-.024*(1-q*q)-.002*math.cos(q*PI*4)*math.sin(PI*v)
            digit=max(0,min(3,side*q*.047/.0207+1.5))
            offset=forms.interpolate([(0,.005),(1,-.004),(2,0),(3,.018)],digit)[0]
            lo=.996+offset
            z=lo+(1.066-lo)*v
            return Vector((x,y,z))
        panel(tag+'_V4_Guantelete_dorso_bajo',lambda u,v:backhand(u,.60*v),40,16,.0025)
        panel(tag+'_V4_Guantelete_dorso_alto',lambda u,v:backhand(u,.54+.46*v)+Vector((0,-.003,0)),40,16,.0025)
        for digit in range(4):
            cx=side*(.512+(digit-1.5)*.023)*.90
            # Thin caps follow each knuckle without merging the finger joints.
            def knuckle(u,v,cx=cx,digit=digit):
                a=(u-.5)*PI
                return Vector((cx+.014*math.sin(a),-.085-.018*math.cos(a),
                               .986+(.005,-.004,0,.018)[digit]+.016*v))
            panel(tag+f'_V4_Guantelete_nudillo_{digit}',knuckle,16,6,.0015)


def cloth():
    remove_piece('V3_Tela_cuello_drapeado')
    def cowl(u,v):
        a=u*TAU;front=max(0,math.cos(a));envelope=math.sin(PI*v)
        phase=TAU*2.05*v+1.05*math.sin(a)+.45*math.sin(2*a+.8)
        broad=.012*math.sin(phase)*envelope**.5
        small=(.0028*math.sin(a*11+v*9)+.002*math.sin(a*5-v*13))*envelope
        rx=.136+.086*v+broad+small;ry=.132+.092*v+broad+small
        z=1.856-.132*v-.052*front**2*v+.016*math.sin(a+.5)*envelope
        z+=.006*math.sin(a*5+v*12)*envelope
        return Vector((rx*math.sin(a),.008-ry*math.cos(a),z))
    panel('V4_Tela_cuello_pliegues_compuestos',cowl,128,72,.002,base.CLOTH,closed=True,flip=True)
    cape=bpy.data.objects.get('V3_Tela_capa_caida_irregular')
    if cape:
        cape.name='V4_Tela_capa'
        for vertex in cape.data.vertices:
            p=vertex.co;t=max(0,min(1,(1.762-p.z)/1.45))
            q=p.x/(.247+.171*t**.65)
            p.y+=.004*math.sin(q*17+t*25)*math.exp(-t*7)
    set_color(base.CLOTH,(.072,.077,.084))
    # Cloth is matte; neutral color separates it from the gray metal study.
    for node in base.CLOTH.node_tree.nodes:
        if node.type=='BSDF_PRINCIPLED':node.inputs['Roughness'].default_value=.96


def heels():
    for side in (-1,1):
        def heel(u,v,side=side):
            a=PI/2+u*PI
            rx=.075-.006*v;ry=.106-.020*v
            z=.035+.120*v+.005*math.cos(a)
            return Vector((side*.210+rx*math.sin(a),.039-ry*math.cos(a),z))
        panel(('L' if side>0 else 'R')+'_V4_Bota_talonera',heel,40,24,.003)


def configure_view():
    bpy.ops.object.select_all(action='DESELECT')
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type=='VIEW_3D':
                s=area.spaces.active;s.shading.type='SOLID';s.shading.color_type='MATERIAL'
                s.shading.show_cavity=True;s.shading.show_shadows=False
                s.overlay.show_overlays=False;s.region_3d.view_perspective='CAMERA'
                s.region_3d.view_camera_zoom=0


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.open_mainfile(filepath=str(PREVIOUS))
    base.OUT=OUT;base.SOURCE=PREVIOUS
    shapes.C['armor']=bpy.data.collections['01_Placas_base_editables']
    shapes.C['studio']=bpy.data.collections['90_Estudio']
    base.ARMOR=bpy.data.materials['Base_Armadura_gris']
    base.CLOTH=bpy.data.materials['Base_Tela_neutra']
    base.DARK=bpy.data.materials['Base_Articulaciones']
    shapes.M.update(steel=base.ARMOR,dark_steel=base.DARK,black=base.DARK,leather=base.DARK,gold=base.ARMOR)
    cuirass();arms_and_hands();cloth();heels()
    shapes.configure_source_view=configure_view
    base.export_and_validate()
    scene=bpy.context.scene;camera=scene.camera
    for title,loc,target,scale in [
        ('TresCuartos',(2.6,-5,2.4),(0,0,1.08),2.47),
        ('Frente',(0,-6,1.22),(0,0,1.08),2.47),
        ('Espalda',(-2.6,5,2.4),(0,0,1.08),2.47),
        ('Detalle',(2.2,-5,2.6),(0,-.015,1.72),1.14),
        ('Guantelete',(2,-5,2),(.45,-.05,1.17),.49),
    ]:
        camera.location=loc;shapes.look_at(camera,target);camera.data.ortho_scale=scale
        scene.render.filepath=str(OUT/f'PaladinElite_Base_{title}.png')
        bpy.ops.render.render(write_still=True)
    print('BASE_V4_COMPLETE',flush=True)


if __name__=='__main__':main()

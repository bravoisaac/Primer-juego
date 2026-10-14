"""Second local form pass. Preserve Base v1 and the ornamented source.

Outputs Base/V2; uses editable solidified surfaces, no remote generation.
"""
import sys
import math
from pathlib import Path
import bpy
from mathutils import Vector

sys.path.insert(0,str(Path(__file__).parent))
import create_paladin_elite_base as base
shapes=base.shapes
PI=math.pi
TAU=math.tau
base.OUT=base.OUT/'V2'


def panel(name,fn,nu=40,nv=24,thickness=.004,mat=None,closed=False,flip=False):
    obj=base.panel(name,fn,mat or base.ARMOR,nu,nv,thickness,flip)
    if closed:
        weld=obj.modifiers.new('Unir costura de la superficie','WELD')
        weld.merge_threshold=.000015
        bpy.context.view_layer.objects.active=obj
        bpy.ops.object.modifier_move_up(modifier=weld.name)
    return obj


def interpolate(stations,t):
    for index,(a,b) in enumerate(zip(stations,stations[1:])):
        if t<=b[0]:
            f=max(0,(t-a[0])/(b[0]-a[0]))
            span=b[0]-a[0]
            values=[]
            for k in range(1,len(a)):
                slope=(b[k]-a[k])/span
                prev=stations[max(0,index-1)];nxt=stations[min(len(stations)-1,index+2)]
                left=(a[k]-prev[k])/(a[0]-prev[0]) if index else slope
                right=(nxt[k]-b[k])/(nxt[0]-b[0]) if index+2<len(stations) else slope
                m0=2*left*slope/(left+slope) if left*slope>0 else 0
                m1=2*right*slope/(right+slope) if right*slope>0 else 0
                values.append((2*f**3-3*f*f+1)*a[k]+(f**3-2*f*f+f)*span*m0
                              +(-2*f**3+3*f*f)*b[k]+(f**3-f*f)*span*m1)
            return tuple(values)
    return stations[-1][1:]


def fitted_sleeve(name,side,top,bottom,radii,arc=TAU,lip=0):
    top=Vector((side*top[0],top[1],top[2]))
    bottom=Vector((side*bottom[0],bottom[1],bottom[2]))
    axis=(top-bottom).normalized()
    lateral=Vector((1,0,0));lateral=(lateral-axis*lateral.dot(axis)).normalized()
    front=axis.cross(lateral)
    if front.y>0:front=-front
    def fn(u,v):
        a=(u-.5)*arc
        rx,ry=interpolate(radii,v)
        p=bottom.lerp(top,v)+lateral*rx*math.sin(a)+front*ry*math.cos(a)
        # Subtle forged ridge and anatomical, scalloped ends.
        p+=front*(.008*(1-abs(math.sin(a)))**8*max(0,math.cos(a))*math.sin(PI*v))
        p.z+=lip*math.cos(a)*v**5
        return p
    return panel(name,fn,48,28,closed=arc==TAU)


def shield(name,side,cx,cz,w,h,edge_y,depth):
    # A convex shield with broad planes, rather than a spherical knee cap.
    outline=[(0,1),(.58,.58),(1,.05),(.70,-.52),(0,-1),(-.70,-.52),(-1,.05),(-.58,.58)]
    verts=[(side*cx,edge_y-depth,cz)];uv=[(.5,.5)];faces=[]
    for r in (.38,.78,1):
        for x,z in outline:
            verts.append((side*cx+x*w*r,edge_y-depth*(1-r*r)+.008*abs(x),cz+z*h*r))
            uv.append((.5+x*r/2,.5+z*r/2))
    for i in range(8):faces.append((0,1+(i+1)%8,1+i))
    for j in range(2):
        for i in range(8):
            a=1+j*8+i;b=1+j*8+(i+1)%8
            faces.append((a,b,b+8,a+8))
    # Face winding points outward toward -Y.
    o=shapes.mesh(name,verts,faces,base.ARMOR,uv=uv)
    for p in o.data.polygons:p.use_smooth=True
    s=o.modifiers.new('Grosor forjado','SOLIDIFY');s.thickness=.005;s.offset=-1
    b=o.modifiers.new('Suavizar aristas de placas','BEVEL');b.width=.003;b.segments=3
    return o


def primary_armor():
    base.simplify_source_armor()
    replace=('Cuirass','Pauldron','UpperArm','Elbow_Couter','Vambrace','Knee_Gothic','Greave','Thigh_Lame','Ankle_Lame','Tasset')
    for o in list(shapes.C['armor'].objects):
        if any(s in o.name for s in replace):bpy.data.objects.remove(o,do_unlink=True)
    def chest(u,v):
        a=(u-.5)*2.72
        width=interpolate([(0,.223),(.28,.252),(.65,.278),(1,.253)],v)[0]
        depth=interpolate([(0,.166),(.25,.197),(.60,.220),(1,.165)],v)[0]
        keel=.024*max(0,1-abs(a)/.60)*math.sin(PI*(.15+.7*v))
        lo=1.265-.060*math.cos(a)**6
        hi=1.754-.110*abs(math.sin(a))**2-.033*math.exp(-a*a*5)
        return Vector((width*math.sin(a),-depth*math.cos(a)-keel,lo+(hi-lo)*v))
    panel('V2_Peto_con_quilla_y_sisas',chest,64,40,.006)
    for side in (-1,1):
        tag='L' if side>0 else 'R'
        def shoulder(u,v,side=side):
            a=u*TAU
            t=v*(1.52+.12*math.cos(a))
            radial=math.sin(t)
            x=side*(.322+.187*radial*math.cos(a))
            y=.006+.180*radial*math.sin(a)
            z=1.670+.150*math.cos(t)-.038*radial*max(0,math.cos(a))
            z+=.011*abs(math.cos(a))*math.sin(PI*v)
            return Vector((x,y,z))
        panel(tag+'_V2_Hombrera_perfil_inclinado',shoulder,64,28,.006,closed=True,flip=side>0)
        for j in range(3):
            fitted_sleeve(tag+f'_V2_Brazo_lama_{j+1}',side,
                (.340+.025*j,.012,1.685-.088*j),(.370+.025*j,.002,1.522-.077*j),
                [(0,.126-j*.014,.125-j*.012),(.75,.142-j*.016,.137-j*.014),(1,.136-j*.014,.131-j*.014)],lip=.009)
        fitted_sleeve(tag+'_V2_Brazo_inferior',side,(.410,-.006,1.424),(.422,-.015,1.337),
                       [(0,.080,.083),(1,.089,.090)])
        shield(tag+'_V2_Codera',side,.428,1.317,.088,.081,-.094,.044)
        fitted_sleeve(tag+'_V2_Brazal_ajustado',side,(.435,-.024,1.289),(.460,-.041,1.062),
                       [(0,.068,.068),(.15,.064,.068),(.64,.081,.089),(1,.089,.092)],lip=.018)
        # Front thigh shells are behind the hanging tassets.
        fitted_sleeve(tag+'_V2_Muslera',side,(.174,.020,.992),(.180,.023,.711),
                       [(0,.094,.108),(.65,.114,.129),(1,.117,.133)],arc=4.5,lip=-.014)
        def tasset(u,v,side=side):
            q=2*u-1
            w=.105-.024*v
            x=side*(.179+.028*(1-v))+q*w
            y=-.179-.052*math.sin(PI*v*.8)-.041*(1-v)+.032*q*q-.009*(1-abs(q))
            lo=.823+.052*abs(q)**1.5
            z=lo+(1.155-lo)*v+.012*q*side
            return Vector((x,y,z))
        panel(tag+'_V2_Escarcel_con_punta',tasset,40,32,.005)
        for j in range(2):
            panel(tag+f'_V2_Escarcel_union_{j}',lambda u,v,j=j:tasset(u,.80+.083*j+.075*v)+Vector((0,-.006,0)),40,6,.003)
        shield(tag+'_V2_Rodillera_facetada',side,.181,.638,.101,.107,-.106,.052)
        for j,z in enumerate((.735,.543)):
            fitted_sleeve(tag+f'_V2_Rodilla_lama_{j}',side,(.181,.027,z+.025),(.183,.028,z-.025),
                           [(0,.091,.111),(1,.098,.121)],arc=3.4)
        fitted_sleeve(tag+'_V2_Greba_con_arista',side,(.184,.041,.551),(.207,.042,.159),
                       [(0,.070,.077),(.15,.067,.075),(.52,.087,.111),(.80,.101,.115),(1,.091,.099)],lip=.013)
        for j in range(2):
            fitted_sleeve(tag+f'_V2_Tobillo_lama_{j}',side,(.209,.031,.196+j*.039),(.210,.022,.138+j*.039),
                           [(0,.080,.100),(1,.078,.092)],arc=3.6)


def helmet():
    profile=[(0,1.824,.108,.120),(.23,1.905,.132,.145),(.53,2.008,.143,.155),
             (.70,2.070,.125,.142),(.86,2.119,.086,.102),(1,2.159,0,0)]
    def skull(u,v):
        z,rx,ry=interpolate(profile,v);a=u*TAU
        # A broad cranium with a shallow forged sagittal ridge.
        y=-ry*math.cos(a)-.009*max(0,math.cos(a))**14*math.sin(PI*v)
        return Vector((rx*math.sin(a),y,z))
    panel('V2_Casco_calota_cerrada',skull,64,48,.006,closed=True)
    def face(u,v):
        q=2*u-1;a=q*1.25
        x=(.115+.029*v)*math.sin(a)
        lo=1.823+.052*abs(q)**1.3
        z=lo+(1.999-lo)*v
        y=-(.134+.021*v)*math.cos(a)-(.038-.014*v)*max(0,1-abs(q))
        # Cheek planes meet the keel; no ornamental raised lines.
        y-=.005*math.sin(PI*v)
        return Vector((x,y,z))
    panel('V2_Casco_visor_con_planos',face,48,24,.006)
    def brow(u,v):
        q=2*u-1;a=q*1.36
        y=-(.173-.022*v)*math.cos(a)-.011*(1-abs(q))
        z=2.013+.047*v-.012*abs(q)+.006*v*math.cos(a)
        return Vector(((.150-.014*v)*math.sin(a),y,z))
    panel('V2_Casco_ceja_inclinada',brow,48,12,.005)
    panel('V2_Casco_hendidura_ocular',lambda u,v:Vector((.142*math.sin((u-.5)*2.5),
            -.163*math.cos((u-.5)*2.5)-.010,1.998+.015*v)),48,4,.001,base.DARK)


def body_and_boots():
    base.padded_body()
    # Narrow the upper mannequin to stay within the breastplate arm openings.
    body=bpy.data.objects.get('Base_Cuerpo_bajo_armadura')
    for vertex in body.data.vertices:
        p=vertex.co
        if p.z>1.42:p.x*=1-.15*min(1,(p.z-1.42)/.25)
    for side in (-1,1):
        tag='L' if side>0 else 'R'
        support=bpy.data.objects.get(tag+'_Base_Pantorrilla')
        for vertex in support.data.vertices:
            p=vertex.co;t=max(0,min(1,(p.z-.137)/(.646-.137)))
            cx=side*(.206*(1-t)+.180*t);cy=.048*(1-t)+.041*t
            p.x=cx+.90*(p.x-cx);p.y=cy+.90*(p.y-cy)
        old=bpy.data.objects.get(tag+'_Bota_Cubierta_base')
        bpy.data.objects.remove(old,do_unlink=True)
        sections=[(-.246,.046,.052),(-.230,.075,.066),(-.18,.086,.086),(-.085,.086,.126),(.01,.081,.168),(.03,.081,.165)]
        for j,(start,end) in enumerate(((-.246,-.139),(-.151,-.071),(-.083,.024))):
            def boot(u,v,start=start,end=end,j=j,side=side):
                a=(u-.5)*PI;y=start+(end-start)*v
                w,top=interpolate(sections,y)
                return Vector((side*.21+(w+.003)*math.sin(a),y,.020+(top-.014)*(.5+.5*math.cos(a))+.003+.004*j))
            panel(tag+f'_V2_Escarpe_placa_{j}',boot,32,16,.003)


def cloth():
    base.cloth()
    cape=bpy.data.objects.get('Tela_Capa_base_sin_bordado')
    bpy.data.objects.remove(cape,do_unlink=True)
    def cape(u,v):
        q=2*u-1
        width=.237+.174*v**.65
        z=1.772-(1.772-.330)*v-.052*abs(q)**1.7*(1-v)**3+.014*math.sin(u*TAU*2+.8)*v**4
        # Folds radiate from the shoulder attachments and soften at the hem.
        amplitude=.007+.026*math.sin(PI*v*.85)
        phase=q*PI*4.4+.28*math.sin(v*5)
        y=.165+.183*v+amplitude*math.cos(phase)-.039*abs(q)**4*(1-v)**3
        return Vector((q*width,y,z))
    panel('V2_Capa_pliegues_desde_hombros',cape,64,72,.002,base.CLOTH)
    for tag in ('L','R'):
        o=bpy.data.objects.get(tag+'_Tela_Faldon_base')
        for vertex in o.data.vertices:
            p=vertex.co;t=max(0,min(1,(1.18-p.z)/.78))
            p.y+=.018*math.sin(t*PI*1.25)+.005*math.sin(p.x*65+t*6)*t
            p.x+=.010*math.sin(t*PI*1.4)*t*(1 if tag=='L' else -1)


def main():
    base.OUT.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    base.ARMOR=base.material('Base_Armadura_gris',(.23,.245,.26),.58)
    base.DARK=base.material('Base_Articulaciones',(.08,.09,.10),.82)
    base.CLOTH=base.material('Base_Tela_neutra',(.15,.157,.17),.90)
    shapes.M.update(steel=base.ARMOR,dark_steel=base.DARK,black=base.DARK,leather=base.DARK,gold=base.ARMOR)
    shapes.C['detail']=shapes.collection('02_Sin_adornos')
    shapes.C['studio']=shapes.collection('90_Estudio')
    primary_armor();body_and_boots();helmet();cloth()
    camera=base.studio()
    scene=bpy.context.scene
    # Neutral studio views expose the plate contours for this form study.
    scene.render.engine='BLENDER_WORKBENCH'
    shading=scene.display.shading
    shading.light='STUDIO';shading.studiolight_rotate_z=.25
    shading.color_type='MATERIAL';shading.show_shadows=False
    shading.show_cavity=True;shading.cavity_type='BOTH'
    shading.curvature_ridge_factor=1.3;shading.curvature_valley_factor=1.0
    shading.cavity_ridge_factor=1.1;shading.cavity_valley_factor=1.1
    shading.background_type='WORLD';scene.world.color=(.045,.055,.068)
    scene.view_settings.exposure=1.25
    scene.render.resolution_x=1100;scene.render.resolution_y=1400
    def configure_form_view():
        bpy.ops.object.select_all(action='DESELECT')
        for screen in bpy.data.screens:
            for area in screen.areas:
                if area.type=='VIEW_3D':
                    space=area.spaces.active;space.shading.type='SOLID'
                    space.shading.color_type='MATERIAL';space.shading.show_cavity=True
                    space.shading.show_shadows=False
                    space.overlay.show_overlays=False
                    space.region_3d.view_perspective='CAMERA';space.region_3d.view_camera_zoom=0
    shapes.configure_source_view=configure_form_view
    base.export_and_validate()
    for title,loc in [('TresCuartos',(2.6,-5,2.4)),('Frente',(0,-6,1.22)),('Espalda',(-2.6,5,2.4))]:
        camera.location=loc;shapes.look_at(camera,(0,0,1.08))
        bpy.context.scene.render.filepath=str(base.OUT/f'PaladinElite_Base_{title}.png')
        bpy.ops.render.render(write_still=True)
    print('BASE_V2_COMPLETE',flush=True)


if __name__=='__main__':main()

##\file
# the building builder file
#
# should act as a reference for other builders files.
#
# builders ui can use existing methods (operators, buttons, panels..)

import bpy
import mathutils
from mathutils import *
from blended_cities.bin.class_main import *
from blended_cities.utils.meshes_io import *

## building builder class
#
# should act as a reference for other builders class.
#
# builders ui can use existing methods (operators, buttons, panels..)
class BC_buildings(BC_elements,bpy.types.PropertyGroup) :
    #name = bpy.props.StringProperty()
    attached = bpy.props.StringProperty()   # the perimeter object
    inherit = bpy.props.BoolProperty(default=False,update=updateBuild)
    floorNumber = bpy.props.IntProperty(
        default = 3,
        min=1,
        max=30,
        update=updateBuild
        )
    floorHeight = bpy.props.FloatProperty(
        default = 2.4,
        min=2.2,
        max=5.0,
        update=updateBuild
        )
    firstFloorHeight = bpy.props.FloatProperty(
        default = 3,
        min=2.2,
        max=5,
        update=updateBuild
        )
    firstFloor = bpy.props.BoolProperty(update=updateBuild)
    interFloorHeight = bpy.props.FloatProperty(
        default = 0.3,
        min=0.1,
        max=1.0,
        update=updateBuild
        )
    roofHeight = bpy.props.FloatProperty(
        default = 0.5,
        min=0.1,
        max=1.0,
        update=updateBuild
        )
    materialslots = ['floor','inter']
    materials = ['floor','inter']

    def build(self,refreshData=True) :
        return buildBox(self,refreshData)

    def heights(self,offset=0) :
        city = bpy.context.scene.city
        this = self
        while this.inherit == True :
            print(this.name,this.inherit)
            otl = this.peer()
            otl = city.outlines[otl.parent]
            this = otl.peer()
        zs = [] # list of z coords of floors and ceilings
        for i in range( self.floorNumber ) :
            if i == 0 :
                zf = offset
                if self.firstFloor :
                    zc = offset + self.firstFloorHeight
                else :
                    zc = offset + this.floorHeight
            else :
                zf = zc + this.interFloorHeight
                zc = zf + this.floorHeight
            zs.append(zf)
            zs.append(zc)
        zs.append(zc + this.roofHeight) # roof

        return zs
 
    def height(self,offset=0) :
        return self.heights(offset)[-1]


def buildBox(self,refreshData=True) :
    city = bpy.context.scene.city
    otl = self.peer()
    print('build box %s (outline %s)'%(self.name,otl.name))

    matslots = ['floor','inter'] 
    mat_floor = 0
    mat_inter = 1

    if refreshData :
        print('refresh data')
        print(otl.dataRead())
    perimeter = otl.dataGet()['perimeters']
    zlist = zcoords(perimeter)
    print('perim %s'%(perimeter))
    print('max height %s'%max(zlist))
    

    verts = []
    faces = []
    mats  = []

    fof = 0 # 'floor' vertex id offset

    for id in range(len(perimeter)) :

        fpf = len(perimeter[id]) # nb of faces per floor

        # non planar outlines : add simple fundation. todo : should be part of floors
        if max(zlist) - min(zlist) > 0.000001 :
            verts.extend( perimeter[id] )
            faces.extend( facesLoop(fof,fpf) )
            mats.extend( mat_floor for i in range(fpf) )
            fof += fpf

        zs = self.heights(max(zlist))#bounds[2][0])
        for zi,z in enumerate(zs) :
            for c in perimeter[id] :
                verts.append( Vector(( c[0],c[1],z )) )
            
            # while roof not reached, its a floor so add faces and mats
            if z != zs[-1] : 
                faces.extend( facesLoop(fof,fpf) )
                mat_id = zi%2
                mats.extend( mat_id for i in range(fpf) )
            fof += fpf
    
    obname = self.objectName()
    if obname == False :
        obname = self.name
    #    print('created %s'%obname)
    #else : print('found object %s'%obname)

    ob = createMeshObject(obname, verts, [], faces, matslots, mats)
    
    city.elements[self.name].pointer = str(ob.as_pointer())
    
    height = self.height() + max(zlist)
    
    updateChildHeight(otl,height)


def register() :
    bpy.utils.register_class(BC_buildings)


def unregister() :
    bpy.utils.unregister_class(BC_buildings)

    
#if __name__ == '__main__' :
#    register()
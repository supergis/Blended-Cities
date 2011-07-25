##\file
# class_import.py
# provide functions to link existing
# builders classes to
# bpy.context.scene.city.builders, as for .buildings
# classes are appended from the builders folder

import bpy
import sys
import os
from blended_cities.bin.class_main import *

## seek the builders folders for existing builders classes (and their gui)
def buildersRegister() :
    '''seek the builders folders for existing builders classes (and their gui)'''
    # seek and register
    mod = sys.modules['blended_cities']
    builders_dir = mod.__path__[0] + '/builders'
    builders_list  = []
    print('. builders :')
    for file in os.listdir(builders_dir) :
        if file[-9:] == '_class.py' :
            classname = 'BC_'+file[0:-9]
            exec('from blended_cities.builders.%s import *'%file[0:-3],globals())
            if file[0:-8] + 'ui.py' in os.listdir(builders_dir) :
                exec('from blended_cities.builders.%s import *'%(file[0:-8] + 'ui'),globals())
                exec('bpy.utils.register_class(%s)'%(classname + '_panel'),globals())
            builders_list.append(classname)
            print('  imported %s'%classname)
    print()

    # write the builders class with pointers
    builders_class = 'class BC_builders(bpy.types.PropertyGroup) :\n'
    for cl in builders_list :
        exec('bpy.utils.register_class(%s)'%cl)
        builders_class += '    %s = bpy.props.CollectionProperty(type=%s)\n'%(cl[3:],cl)

    exec(builders_class,globals())

    # update dropdown in the main tagging ui
    class_selector = []
    class_default  = 'buildings'
    for cl in builders_list :
        class_selector.append( (cl[3:],cl[3:],'') )
    bpy.types.WindowManager.city_builders_dropdown  = bpy.props.EnumProperty( items = class_selector, default = class_default, name = "Builders",  description = "" )

buildersRegister()
bpy.utils.register_class(BC_builders)
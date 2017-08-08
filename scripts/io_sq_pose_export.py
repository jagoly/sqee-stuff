import bpy
from bpy_extras.io_utils import ExportHelper
from mathutils import Vector

#==============================================================================#

bl_info = {
    "name": "SQEE Pose Exporter",
    "author": "James Gangur",
    "version": (17, 1),
    "blender": (2, 78, 0),
    "location": "File > Export > SQEE Pose (.txt)",
    "description": "Export current pose in the SQEE format",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Import-Export"
}

#==============================================================================#

class SqeeBone():
    def __init__(self):
        self.position = None
        self.rotation = None
        self.scale = None

#==============================================================================#

def round_vector(vec, precision):
    return Vector(vec.to_tuple(precision)).freeze()

def tidy_value(val, precision):
    result = ("%%.%df" % precision % val).rstrip("0")
    if result.endswith("."): result += "0"
    if result == "-0.0": result = "0.0"
    return result

def tidy_vector(vec, precision):
    return tuple(tidy_value(v, precision) for v in vec)

#==============================================================================#

class SqExportPose_operator(bpy.types.Operator, ExportHelper):
    """Export a pose in the SQEE format"""

    bl_idname = "sq.export_pose_operator"
    bl_label = "Export SQEE Pose"

    filename_ext = ".txt"
    filter_glob = bpy.props.StringProperty(default="*.txt", options={'HIDDEN'})

    #----------------------------------------------------------#

    def execute(self, context):

        obj = bpy.context.active_object

        boneList = sorted ( obj.pose.bones, key = lambda bone: (len(bone.parent_recursive), bone.name) )
        boneList = [ bone for bone in boneList if bone.name[0] != '.' ]

        #----------------------------------------------------------#

        with open(self.filepath, 'w', encoding='utf-8') as o:

            for bone in boneList:

                mat = bone.matrix
                if bone.parent is not None:
                    mat = bone.parent.matrix.inverted() * mat

                o.write("{0} {1} {2} ".format(*tidy_vector(mat.to_translation(), 5)))
                o.write("{1} {2} {3} {0} ".format(*tidy_vector(mat.to_quaternion(), 6)))
                o.write("{0} {1} {2}\n".format(*tidy_vector(mat.to_scale(), 5)))

        #----------------------------------------------------------#

        return {'FINISHED'}

#==============================================================================#

def menu_func(self, context):
    self.layout.operator(SqExportPose_operator.bl_idname, text="SQEE Pose (.txt)")

def register():
    bpy.utils.register_class(SqExportPose_operator)
    bpy.types.INFO_MT_file_export.append(menu_func)

def unregister():
    bpy.utils.unregister_class(SqExportPose_operator)
    bpy.types.INFO_MT_file_export.remove(menu_func)

#==============================================================================#

if __name__ == "__main__":
    register()
    bpy.ops.sq.export_pose_operator('INVOKE_DEFAULT')

import bpy
from bpy_extras.io_utils import ExportHelper
from mathutils import Vector

#==============================================================================#

bl_info = {
    "name": "SQEE Animation Exporter",
    "author": "James Gangur",
    "version": (17, 1),
    "blender": (2, 78, 0),
    "location": "File > Export > SQEE Animation (.txt)",
    "description": "Export an animation in the SQEE format",
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

class SqeeAnim():
    def __init__(self):
        self.boneCount = 0
        self.poseCount = 0
        self.totalTime = 0
        self.times = []
        self.poses = []

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

class SqExportAnim_operator(bpy.types.Operator, ExportHelper):
    """Export an animation in the SQEE format"""

    bl_idname = "sq.export_anim_operator"
    bl_label = "Export SQEE Animation"

    filename_ext = ".txt"
    filter_glob = bpy.props.StringProperty(default="*.txt", options={'HIDDEN'})

    finalTime = bpy.props.IntProperty(name="Final Keyframe Time", default=0)
    
    #----------------------------------------------------------#

    def execute(self, context):

        scene = bpy.context.scene
        obj = bpy.context.active_object

        anim = SqeeAnim()

        bpy.ops.screen.frame_jump()
        scene.frame_set(scene.frame_current)
        
        #----------------------------------------------------------#

        while True:

            boneList = sorted ( obj.pose.bones, key = lambda bone: (len(bone.parent_recursive), bone.name) )
            boneList = [ bone for bone in boneList if bone.name[0] != '.' ]

            begin = scene.frame_current

            anim.poses.append([])

            for bone in boneList:

                anim.poses[-1].append(SqeeBone())
                sqb = anim.poses[-1][-1]

                mat = bone.matrix
                if bone.parent is not None:
                    mat = bone.parent.matrix.inverted() * mat

                sqb.position = mat.to_translation()
                sqb.rotation = mat.to_quaternion()
                sqb.scale = mat.to_scale()

            bpy.ops.screen.keyframe_jump()
            scene.frame_set(scene.frame_current)
            end = scene.frame_current

            if begin == end: break

            anim.times.append(end - begin)

        anim.times.append(self.finalTime)
        
        #----------------------------------------------------------#

        anim.boneCount = sum(bone.name[0] != '.' for bone in obj.pose.bones)
        anim.poseCount = len(anim.poses)
        anim.totalTime = sum(anim.times)

        #----------------------------------------------------------#

        with open(self.filepath, 'w', encoding='utf-8') as o:

            o.write("# SQEE Animation Format\n")

            o.write("\n\n################################################################################\n")

            o.write("\nSECTION Header\n")

            o.write("\nBoneCount %d" % anim.boneCount)
            o.write("\nPoseCount %d" % anim.poseCount)
            o.write("\nTotalTime %d" % anim.totalTime)

            o.write("\n\nTimes %s\n" % " ".join(map(str, anim.times)))

            o.write("\n\n################################################################################\n")

            o.write("\nSECTION Poses\n")

            for index, pose in enumerate(anim.poses):

                poseLine = "##### Pose: %d " % index
                o.write("\n\n{:#<60}\n\n".format(poseLine))

                for bone in pose:

                    o.write("{0} {1} {2} ".format(*tidy_vector(bone.position, 5)))
                    o.write("{0} ".format(tidy_value(bone.scale.y, 5)))
                    o.write("{1} {2} {3} {0}\n".format(*tidy_vector(bone.rotation, 6)))

        #----------------------------------------------------------#

        cleanLines = []

        with open(self.filepath, 'r', encoding='utf-8') as rf:
            cleanLines = [line.rstrip() for line in rf.readlines()]

        with open(self.filepath, 'w', encoding='utf-8') as wf:
            wf.writelines('\n'.join(cleanLines))

        #----------------------------------------------------------#

        return {'FINISHED'}

#==============================================================================#

def menu_func(self, context):
    self.layout.operator(SqExportAnim_operator.bl_idname, text="SQEE Animation (.txt)")

def register():
    bpy.utils.register_class(SqExportAnim_operator)
    bpy.types.INFO_MT_file_export.append(menu_func)

def unregister():
    bpy.utils.unregister_class(SqExportAnim_operator)
    bpy.types.INFO_MT_file_export.remove(menu_func)

#==============================================================================#

if __name__ == "__main__":
    register()
    bpy.ops.sq.export_anim_operator('INVOKE_DEFAULT')


import bpy
from collections import defaultdict
from bpy_extras.io_utils import ExportHelper
from mathutils import Vector, Quaternion

#==============================================================================#

bl_info = {
    "name": "SQEE Animation Exporter",
    "author": "James Gangur",
    "version": (21, 5),
    "blender": (2, 92, 0),
    "location": "File > Export > SQEE Animation (.sqa)",
    "description": "Export an animation in the SQEE format",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Import-Export"
}

#==============================================================================#

class SqeeAnim():
    def __init__(self):
        self.boneCount = 0
        self.frameCount = 0
        self.baseTracks = defaultdict(dict)
        self.extraTracks = defaultdict(dict)

def tidy_value(precision, value):
    result = ("%%.%df" % precision % value).rstrip("0")
    if result.endswith("."): result += "0"
    if result == "-0.0": result = "0.0"
    return result

def tidy_values(precision, *values):
    return tuple(tidy_value(precision, val) for val in values)

#==============================================================================#

class SqeeExportAnimation_operator(bpy.types.Operator, ExportHelper):
    """Export an animation in the SQEE format"""

    bl_idname = "sqee.export_animation_operator"
    bl_label = "Export SQEE Animation"

    filename_ext = ".sqa"

    filter_glob: bpy.props.StringProperty(default="*.sqa", options={'HIDDEN'})

    precision:       bpy.props.IntProperty (name="Number of Decimal Places", default=5, min=3, max=7)
    swapYZ:          bpy.props.BoolProperty(name="Swap Y and Z Axis",        default=False)
    exportCustom:    bpy.props.BoolProperty(name="Export Custom Properties", default=False)
    ignoreLastFrame: bpy.props.BoolProperty(name="Don't Export Last Frame",  default=False)

    def invoke(self, context, event):
        self.filepath = bpy.context.active_object.animation_data.action.name
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    #----------------------------------------------------------#

    def execute(self, context):

        scene = bpy.context.scene
        obj = bpy.context.active_object
        action = obj.animation_data.action

        anim = SqeeAnim()
        
        poseBoneList = sorted ( obj.pose.bones, key = lambda pb: (len(pb.parent_recursive), pb.name) )
        poseBoneList = [ pb for pb in poseBoneList if pb.name[0] != '.' ]

        anim.boneCount = len(poseBoneList)
        anim.frameCount = int(action.frame_range[1]) + 1 - int(self.ignoreLastFrame)

        #----------------------------------------------------------#

        for frame in range(0, anim.frameCount):
            scene.frame_set(frame)
            
            for pb in poseBoneList:

                mat = pb.matrix
                if pb.parent and pb.parent.name[0] != '.':
                    mat = pb.parent.matrix.inverted() @ mat

                track = anim.baseTracks[pb.name + " offset"]
                v = mat.to_translation()
                if self.swapYZ: track[frame] = ( v.x, v.z, v.y )
                else: track[frame] = ( v.x, v.y, v.z )

                track = anim.baseTracks[pb.name + " rotation"]
                q = mat.to_quaternion()
                if self.swapYZ: track[frame] = ( -q.x, -q.z, -q.y, q.w )
                else: track[frame] = ( q.x, q.y, q.z, q.w )

                track = anim.baseTracks[pb.name + " scale"]
                v = mat.to_scale()
                if self.swapYZ: track[frame] = ( v.x, v.z, v.y )
                else: track[frame] = ( v.x, v.y, v.z )
                    
                if self.exportCustom:
                    for key, value in pb.items():
                        if key[0] not in "._":
                            if len(value) == 4 and type(value[0]) == float:
                                track = anim.extraTracks["%s %s Vec4F" % (pb.name, key)]
                            else:
                                assert False, "unsupported property type"
                            track[frame] = tuple(value)

        #----------------------------------------------------------#

        for trackName, trackDict in anim.baseTracks.items():
            first = Vector(trackDict[0])
            if all((first - Vector(value)).length < 0.0001 for value in trackDict.values()):
                anim.baseTracks[trackName] = first

        for trackName, trackDict in anim.extraTracks.items():
            first = Vector(trackDict[0])
            if all((first - Vector(value)).length < 0.0001 for value in trackDict.values()):
                anim.extraTracks[trackName] = first

        #----------------------------------------------------------#

        with open(self.filepath, 'w', encoding='utf-8') as o:
            
            frameFmtStr = "\n %{}d".format(len(str(anim.frameCount - 1)))

            o.write("# SQEE Animation Format\n")

            o.write("\n\n################################################################################\n")

            o.write("\nSECTION Header\n")

            o.write("\nBoneCount %d" % anim.boneCount)
            o.write("\nFrameCount %d\n" % anim.frameCount)

            o.write("\n\n################################################################################\n")

            o.write("\nSECTION BaseTracks\n")

            for trackName, trackData in anim.baseTracks.items():
                o.write("\nTRACK %s" % trackName)
                if type(trackData) is not dict:
                    for val in tidy_values(self.precision, *trackData):
                        o.write(" %s" % val)
                else:
                    for frame, frameData in trackData.items():
                        o.write(frameFmtStr % frame)
                        for val in tidy_values(self.precision, *frameData):
                            o.write(" %s" % val)
                o.write("\n")
            
            if self.exportCustom:

                o.write("\n\n################################################################################\n")

                o.write("\nSECTION ExtraTracks\n")

                for trackName, trackData in anim.extraTracks.items():
                    o.write("\nTRACK %s" % trackName)
                    if type(trackData) is not dict:
                        for val in tidy_values(self.precision, *trackData):
                            o.write(" %s" % val)
                    else:
                        for frame, frameData in trackData.items():
                            o.write(frameFmtStr % frame)
                            for val in tidy_values(self.precision, *frameData):
                                o.write(" %s" % val)
                    o.write("\n")

        #----------------------------------------------------------#

        return {'FINISHED'}

#==============================================================================#

def menu_func(self, context):
    self.layout.operator(SqeeExportAnimation_operator.bl_idname, text="SQEE Animation (.sqa)")

def register():
    bpy.utils.register_class(SqeeExportAnimation_operator)
    bpy.types.TOPBAR_MT_file_export.append(menu_func)

def unregister():
    bpy.utils.unregister_class(SqeeExportAnimation_operator)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func)

#==============================================================================#

if __name__ == "__main__":
    register()
    bpy.ops.sq.export_animation_operator('INVOKE_DEFAULT')


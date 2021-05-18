import bpy
from collections import defaultdict
from math import radians
from mathutils import Vector, Euler, Matrix

bl_info = {
    "name": "BrawlCrate .anim Importer",
    "author": "James Gangur",
    "version": (21, 1),
    "blender": (2, 91, 0),
    "location": "File > Import > BrawlCrate Animation (.anim)",
    "description": "Import an animation exported by BrawlCrate",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Import-Export"
}

#==============================================================================#

class BrawlCrateBone():
    def __init__(self):
        self.translateX = {}
        self.translateY = {}
        self.translateZ = {}
        self.rotateX = {}
        self.rotateY = {}
        self.rotateZ = {}
        self.scaleX = {}
        self.scaleY = {}
        self.scaleZ = {}
    
    def assert_constant(self, boneName):
        assert len(self.translateX) <= 1, boneName
        assert len(self.translateY) <= 1, boneName
        assert len(self.translateZ) <= 1, boneName
        assert len(self.rotateX) <= 1, boneName
        assert len(self.rotateY) <= 1, boneName
        assert len(self.rotateZ) <= 1, boneName
        
#==============================================================================#
        
def mat_offset(pose_bone):
    bone = pose_bone.bone
    mat = bone.matrix.to_4x4()
    mat.translation = bone.head
    if pose_bone.parent:
        mat.translation.y += bone.parent.length
    return mat

def get_interpolated_value(frame, data, default):

    # todo: we have some tangent data too, need to use it to get intended results
    
    if not data: return default
    if frame in data: return data[frame]
    
    lessValues = list((k,v) for k,v in data.items() if k < frame)
    moreValues = list((k,v) for k,v in data.items() if k > frame)
    
    if not lessValues: return moreValues[0][1]
    if not moreValues: return lessValues[-1][1]

    more, less = moreValues[0], lessValues[-1]
    factor = (frame - less[0]) / (more[0] - less[0])

    return less[1] * (1.0 - factor) + more[1] * factor

#==============================================================================#

def read_brawlcrate_anim(context, actionName, inFile):

    assert inFile.readline() == "animVersion 1.1;\n"
    assert inFile.readline() == "mayaVersion 2015;\n"
    assert inFile.readline() == "timeUnit ntscf;\n"
    assert inFile.readline() == "linearUnit cm;\n"
    assert inFile.readline() == "angularUnit deg;\n"
    assert inFile.readline() == "startTime 0;\n"
    
    line = inFile.readline().split()
    print(line)
    endTime = int(line[1][:-1])

    arm = bpy.context.active_object

    # Get armature animation data
    bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

    context.view_layer.update()

    arm.animation_data_create()
    action = bpy.data.actions.new(name=actionName)
    arm.animation_data.action = action
    
    bones = defaultdict(BrawlCrateBone)
    
    currentTrack = None
    trackType = None
    
    expected = "anim"
    
    for line in inFile.read().splitlines():
        tokens = line.split()
        #print(line)

        if expected == "anim":
            assert tokens[0] == "anim"
            if tokens[1].startswith("translate"):
                currentTrack = getattr(bones[tokens[3]], tokens[2])
                trackType = 'translate'
                expected = "animData"
            elif tokens[1].startswith("rotate"):
                currentTrack = getattr(bones[tokens[3]], tokens[2])
                trackType = 'rotate'
                expected = "animData"
            elif tokens[1].startswith("scale"):
                currentTrack = getattr(bones[tokens[3]], tokens[2])
                trackType = 'scale'
                expected = "animData"
            else:
                assert line.endswith(" 0 0 0;") and len(tokens) == 5
                expected = "anim"
        
        elif expected == "animData":
            assert line == "animData {"
            expected = "input"
            
        elif expected == "input":
            assert line == "  input time;"
            expected = "output"
       
        elif expected == "output":
            if trackType == 'rotate':
                assert line.endswith("output angular;")
            else: 
                assert line.endswith("output linear;")
            expected = "weighted"
            
        elif expected == "weighted":
            assert line.endswith("weighted 1;")
            expected = "preInfinity"
            
        elif expected == "preInfinity":
            assert line.endswith("preInfinity constant;")
            expected = "postInfinity"
            
        elif expected == "postInfinity":
            assert line.endswith("postInfinity constant;")
            expected = "keys"
        
        elif expected == "keys":
            assert line.endswith("keys {")
            expected = "value"
        
        elif expected == "value":
            if line.endswith("}"):
                expected = "}"
                continue
            
            print(tokens)
            
            assert tokens[2] == 'fixed'
            assert tokens[3] == 'fixed'
            assert tokens[4] == '1'
            assert tokens[5] == '1'
            assert tokens[6] == '0'
            assert tokens[7] == tokens[9] and tokens[8] == tokens[10].rstrip(';')
            assert int(tokens[0]) <= endTime
            
            if trackType == 'rotate':
                currentTrack[int(tokens[0])] = radians(float(tokens[1]))
            else:
                currentTrack[int(tokens[0])] = float(tokens[1])
            
        elif expected == "}":
            assert line == "}"
            expected = "anim"

    boneList = sorted ( arm.pose.bones, key = lambda bone: (len(bone.parent_recursive), bone.name) )
    boneList = [ bone for bone in boneList if bone.name[0] != '.' ]

    for poseBone in boneList:
        
        boneName = poseBone.name
        bone = bones[boneName]
        
        dataPathLoc = 'pose.bones["%s"].location' % boneName
        dataPathRot = 'pose.bones["%s"].rotation_quaternion' % boneName
        dataPathSca = 'pose.bones["%s"].scale' % boneName

        curveLX = action.fcurves.new(dataPathLoc, index=0, action_group=boneName)
        curveLY = action.fcurves.new(dataPathLoc, index=1, action_group=boneName)
        curveLZ = action.fcurves.new(dataPathLoc, index=2, action_group=boneName)

        curveRW = action.fcurves.new(dataPathRot, index=0, action_group=boneName)    
        curveRX = action.fcurves.new(dataPathRot, index=1, action_group=boneName)
        curveRY = action.fcurves.new(dataPathRot, index=2, action_group=boneName)
        curveRZ = action.fcurves.new(dataPathRot, index=3, action_group=boneName)

        curveSX = action.fcurves.new(dataPathSca, index=0, action_group=boneName)
        curveSY = action.fcurves.new(dataPathSca, index=1, action_group=boneName)
        curveSZ = action.fcurves.new(dataPathSca, index=2, action_group=boneName)
        
        arm.pose.bones[boneName].rotation_mode = "QUATERNION"
        
        for frame in range(0, endTime+1):
            
            # todo: for loc and rot, default should be the rest value
            
            locX = get_interpolated_value(frame, bone.translateX, 0.0)
            locY = get_interpolated_value(frame, bone.translateY, 0.0)
            locZ = get_interpolated_value(frame, bone.translateZ, 0.0)
        
            rotX = get_interpolated_value(frame, bone.rotateX, 0.0)
            rotY = get_interpolated_value(frame, bone.rotateY, 0.0)
            rotZ = get_interpolated_value(frame, bone.rotateZ, 0.0)
            
            scaX = get_interpolated_value(frame, bone.scaleX, 1.0)
            scaY = get_interpolated_value(frame, bone.scaleY, 1.0)
            scaZ = get_interpolated_value(frame, bone.scaleZ, 1.0)
            
            loc = Vector((locX, locY, locZ)) * 0.1
            rot = Euler((rotX, rotY, rotZ), "XYZ")
            sca = Vector((scaX, scaY, scaZ))
            
            locMat = Matrix.Translation(loc)
            rotMat = rot.to_matrix().to_4x4()
            scaMat = Matrix.Diagonal(sca).to_4x4()
            
            basisMat = locMat @ rotMat @ scaMat
            basisMat = mat_offset(arm.pose.bones[boneName]).inverted() @ basisMat
            
            loc, rot, sca = basisMat.decompose()
            
            curveLX.keyframe_points.insert(frame, loc.x).interpolation = 'LINEAR'
            curveLY.keyframe_points.insert(frame, loc.y).interpolation = 'LINEAR'
            curveLZ.keyframe_points.insert(frame, loc.z).interpolation = 'LINEAR'
            
            curveRW.keyframe_points.insert(frame, rot.w).interpolation = 'LINEAR'
            curveRX.keyframe_points.insert(frame, rot.x).interpolation = 'LINEAR'
            curveRY.keyframe_points.insert(frame, rot.y).interpolation = 'LINEAR'
            curveRZ.keyframe_points.insert(frame, rot.z).interpolation = 'LINEAR'
            
            curveSX.keyframe_points.insert(frame, sca.x).interpolation = 'LINEAR'
            curveSY.keyframe_points.insert(frame, sca.y).interpolation = 'LINEAR'
            curveSZ.keyframe_points.insert(frame, sca.z).interpolation = 'LINEAR'

#==============================================================================#

def read_colour_anim(context, inFile):
    
    arm = context.active_object
    action = arm.animation_data.action

    boneList = sorted ( arm.pose.bones, key = lambda bone: (len(bone.parent_recursive), bone.name) )
    boneList = [ bone for bone in boneList if bone.name[0] != '.' ][1:] # without root bone

    for poseBone, clrLines in zip(boneList, inFile.read().split('\n\n')):

        boneName = poseBone.name
        
        rna_ui = poseBone.get('_RNA_UI')
        if rna_ui is None:
            poseBone['_RNA_UI'] = {}
            rna_ui = poseBone['_RNA_UI']

        poseBone['colour'] = [1.0, 1.0, 1.0, 1.0]
        rna_ui['colour'] = { 'subtype': 'COLOR' }

        dataPath = 'pose.bones["%s"]["colour"]' % boneName
        
        curveR = action.fcurves.new(dataPath, index=0, action_group=boneName)
        curveG = action.fcurves.new(dataPath, index=1, action_group=boneName)
        curveB = action.fcurves.new(dataPath, index=2, action_group=boneName)
        curveA = action.fcurves.new(dataPath, index=3, action_group=boneName)

        for frame, line in enumerate(clrLines.split()):

            curveR.keyframe_points.insert(frame, int(line[0:2], 16) / 255.0).interpolation = 'LINEAR'
            curveG.keyframe_points.insert(frame, int(line[2:4], 16) / 255.0).interpolation = 'LINEAR'
            curveB.keyframe_points.insert(frame, int(line[4:6], 16) / 255.0).interpolation = 'LINEAR'
            curveA.keyframe_points.insert(frame, int(line[6:8], 16) / 255.0).interpolation = 'LINEAR'

#==============================================================================#

from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator

class BrawlCrateAnimImport_operator(bpy.types.Operator, ImportHelper):
    """Import an animation exported from BrawlCrate"""
    
    bl_idname = "brawlcrate.anim_import"
    bl_label = "Import BrawlCrate Animation"

    filename_ext = ".anim"

    filter_glob: bpy.props.StringProperty(default="*.anim", options={'HIDDEN'})
    importColour: bpy.props.BoolProperty(name="import colour from clr.txt", default=False)
    
    def execute(self, context):
    
        from pathlib import PurePath

        with open(self.filepath, 'r') as inFile:    
            actionName = PurePath(self.filepath).with_suffix("").name
            read_brawlcrate_anim(context, actionName, inFile)

        if self.importColour:
            clrTxtPath = PurePath(self.filepath).with_name("clr.txt")
            with open(clrTxtPath, 'r') as inFile:
                read_colour_anim(context, inFile)

        return {'FINISHED'}

#==============================================================================#

def menu_func_import(self, context):
    self.layout.operator(BrawlCrateAnimImport_operator.bl_idname, text="BrawlCrate Anim (.anim)")

def register():
    bpy.utils.register_class(BrawlCrateAnimImport_operator)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)

def unregister():
    bpy.utils.unregister_class(BrawlCrateAnimImport_operator)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)

#==============================================================================#

if __name__ == "__main__":
    register()
    bpy.ops.brawlcrate.anim_import('INVOKE_DEFAULT')


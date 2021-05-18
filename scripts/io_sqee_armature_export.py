import bpy, json, re
from bpy_extras.io_utils import ExportHelper
from mathutils import Vector, Quaternion

#==============================================================================#

bl_info = {
    "name": "SQEE Armature Exporter",
    "author": "James Gangur",
    "version": (21, 5),
    "blender": (2, 92, 0),
    "location": "File > Export > SQEE Armature (.json)",
    "description": "Export an armature in the SQEE format",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Import-Export"
}

#==============================================================================#

def round_values(precision, *values):
    rounded = ( round(val, precision) for val in values )
    return tuple(0.0 if val == -0.0 else val for val in rounded)

#==============================================================================#

class SqeeExportArmature_operator(bpy.types.Operator, ExportHelper):
    """Export an armature in the SQEE format"""

    bl_idname = "sqee.export_armature_operator"
    bl_label = "Export SQEE Armature"

    filename_ext = ".json"

    filter_glob: bpy.props.StringProperty(default="*.json", options={'HIDDEN'})

    precision: bpy.props.IntProperty (name="Number of Decimal Places", default=5, min=3, max=7)
    swapYZ:    bpy.props.BoolProperty(name="Swap Y and Z Axis",        default=False)

    def invoke(self, context, event):
        self.filepath = bpy.context.active_object.name
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    #----------------------------------------------------------#

    def execute(self, context):

        arma = bpy.context.active_object.data
        
        boneList = sorted ( arma.bones, key = lambda b: (len(b.parent_recursive), b.name) )
        boneList = [ b for b in boneList if b.name[0] != '.' ]
        
        jsonArmature = []

        #----------------------------------------------------------#

        for bone in boneList:
            
            jb = { 'name': bone.name }

            if bone.parent and bone.parent.name[0] != '.':
                jb['parent'] = bone.parent.name
                mat = bone.parent.matrix_local.inverted() @ bone.matrix_local
            else:
                jb['parent'] = None
                mat = bone.matrix_local

            v = mat.to_translation()
            if self.swapYZ: jb['offset'] = round_values(self.precision, v.x, v.z, v.y)
            else: jb['offset'] = round_values(self.precision, v.x, v.y, v.z)

            q = mat.to_quaternion()
            if self.swapYZ: jb['rotation'] = round_values(self.precision, -q.x, -q.z, -q.y, q.w)
            else: jb['rotation'] = round_values(self.precision, q.x, q.y, q.z, q.w)

            v = mat.to_scale()
            if self.swapYZ: jb['scale'] = round_values(self.precision, v.x, v.z, v.y)
            else: jb['scale'] = round_values(self.precision, v.x, v.y, v.z)
            
            jsonArmature.append(jb)

        #----------------------------------------------------------#

        with open(self.filepath, 'w', encoding='utf-8') as o:

            jstr = json.dumps(jsonArmature, indent=2)

            jstr = re.sub(r"(\d),\n *", r"\1, ", jstr)
            jstr = re.sub(r"\n *([\-\d])", r" \1", jstr)
            jstr = re.sub(r"(\d)\n *", r"\1 ", jstr)

            o.write(jstr)

        #----------------------------------------------------------#

        return {'FINISHED'}

#==============================================================================#

def menu_func(self, context):
    self.layout.operator(SqeeExportArmature_operator.bl_idname, text="SQEE Armature (.json)")

def register():
    bpy.utils.register_class(SqeeExportArmature_operator)
    bpy.types.TOPBAR_MT_file_export.append(menu_func)

def unregister():
    bpy.utils.unregister_class(SqeeExportArmature_operator)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func)

#==============================================================================#

if __name__ == "__main__":
    register()
    bpy.ops.sqee.export_armature_operator('INVOKE_DEFAULT')

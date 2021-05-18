import bpy
from bpy_extras.io_utils import ExportHelper
from mathutils import Vector

#==============================================================================#

bl_info = {
    "name": "SQEE Mesh Exporter",
    "author": "James Gangur",
    "version": (21, 5),
    "blender": (2, 92, 0),
    "location": "File > Export > SQEE Mesh (.sqm)",
    "description": "Export a mesh in the SQEE format",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Import-Export"
}

#==============================================================================#

class SqeeSubMesh():
    def __init__(self, name):
        self.name = name
        self.vertexDict = {}
        self.vertexList = []
        self.faceList = []

class SqeeMesh():
    def __init__(self):
        self.origin = None
        self.extents = None
        self.radius = 0.0
        self.subMeshList = []

def tidy_value(precision, value):
    assert type(value) is float
    result = ("%%.%df" % precision % value).rstrip("0")
    if result.endswith("."): result += "0"
    if result == "-0.0": result = "0.0"
    return result

def tidy_values(precision, *values):
    return tuple(tidy_value(precision, val) for val in values)

#==============================================================================#

class SqeeExportMesh_operator(bpy.types.Operator, ExportHelper):
    """Export a mesh in the SQEE format"""

    bl_idname = "sqee.export_mesh_operator"
    bl_label = "Export SQEE Mesh"

    filename_ext = ".sqm"

    filter_glob: bpy.props.StringProperty(default="*.sqm", options={'HIDDEN'})

    disableArmature: bpy.props.BoolProperty(name="Disable Armature Modifier", default=True)
    swapYZ:          bpy.props.BoolProperty(name="Swap the Y and Z Axes",     default=False)
    exportBounds:    bpy.props.BoolProperty(name="Export Bounding Info",      default=False)
    exportTexCoords: bpy.props.BoolProperty(name="Export Texture Coords",     default=False)
    exportNormals:   bpy.props.BoolProperty(name="Export Vertex Normals",     default=False)
    exportTangents:  bpy.props.BoolProperty(name="Export Vertex Tangents",    default=False)
    exportColours:   bpy.props.BoolProperty(name="Export Vertex Colours",     default=False)
    exportBones:     bpy.props.BoolProperty(name="Export Bones and Weights",  default=False)

    #----------------------------------------------------------#

    def execute(self, context):

        if self.exportTangents:
            assert self.exportNormals, "tangents require normals"
        if self.exportBounds:
            assert not self.exportBones, "bounds don't work with bones"

        obj = context.active_object
        uvLayer = vcLayer = arma = boneIndexMap = None

        if self.disableArmature:
            armatureModifier = obj.modifiers.get('Armature')
            if armatureModifier:
                restoreArmatureModifier = armatureModifier.show_viewport
                armatureModifier.show_viewport = False

        depsgraph = context.evaluated_depsgraph_get()
        mesh = obj.evaluated_get(depsgraph).to_mesh(preserve_all_data_layers=True, depsgraph=depsgraph)
        if self.exportTangents: mesh.calc_tangents()

        if self.disableArmature and armatureModifier and restoreArmatureModifier:
            armatureModifier.show_viewport = True

        sqm = SqeeMesh()

        if self.exportTexCoords: uvLayer = mesh.uv_layers.active.data
        if self.exportColours: vcLayer = mesh.vertex_colors.active.data
        if self.exportBones: arma = obj.parent.data

        #----------------------------------------------------------#

        for name in mesh.materials.keys():
            assert ' ' not in name, "material name contains spaces: " + name
            assert len(name) < 16, "material name is too long: " + name

        # create a sub mesh for each material used by the mesh
        sqm.subMeshList = list(map(SqeeSubMesh, mesh.materials.keys()))
        if not sqm.subMeshList:
            sqm.subMeshList = [SqeeSubMesh("Default")]

        # compute mapping of mesh bone indices to armature bone indices
        if self.exportBones:
            bones = sorted(arma.bones, key = lambda bone: (len(bone.parent_recursive), bone.name))
            boneNames = tuple(bone.name for bone in bones if bone.name[0] != '.')
            assert len(boneNames) == len(obj.vertex_groups), "wrong number of vertex groups in mesh"
            boneIndexMap = tuple(boneNames.index(group) for group in obj.vertex_groups.keys())
            print(boneIndexMap)

        #----------------------------------------------------------#

        # compute axis aligned box and sphere
        if self.exportBounds:
            boundsMin = Vector.Fill(3, float('+inf'))
            boundsMax = Vector.Fill(3, float('-inf'))
            for vert in mesh.vertices:
                boundsMin = Vector(map(min, zip(boundsMin, vert.co)))
                boundsMax = Vector(map(max, zip(boundsMax, vert.co)))
            sqm.origin = (boundsMin + boundsMax) * 0.5
            sqm.extents = (boundsMax - boundsMin) * 0.5
            for vert in mesh.vertices:
                sqm.radius = max(sqm.radius, (sqm.origin - vert.co).length)
            if self.swapYZ:
                sqm.origin.y, sqm.origin.z = sqm.origin.z, sqm.origin.y
                sqm.extents.y, sqm.extents.z = sqm.extents.z, sqm.extents.y

        #----------------------------------------------------------#

        for faceNum, f in enumerate(mesh.polygons):

            # the sub mesh containing this face
            subMesh = sqm.subMeshList[f.material_index]

            # add a new face to the sub mesh
            subMesh.faceList.append([-1, -1, -1])

            for cornerNum, loopIndex in enumerate(f.loop_indices):

                l = mesh.loops[loopIndex]
                v = mesh.vertices[l.vertex_index]

                position = v.co.to_tuple(5)
                if self.swapYZ:
                    position = (position[0], position[2], position[1])

                # set all key properties to None
                texcrd = normal = tangent = colour = bones = weights = None

                # used to access uv and colour data
                layerIndex = faceNum * 3 + cornerNum

                if self.exportTexCoords:
                    texcrd = uvLayer[layerIndex].uv.to_tuple(5)

                if self.exportNormals:
                    normal = (v if f.use_smooth else f).normal.normalized().to_tuple(5)
                    if self.swapYZ:
                        normal = (normal[0], normal[2], normal[1])

                if self.exportTangents:
                    # change from blender tangent (+Y) to sqee tangent (-Y)
                    tangent = Vector((*-l.tangent.normalized(), l.bitangent_sign)).to_tuple(5)
                    if self.swapYZ:
                        tangent = (tangent[0], tangent[2], tangent[1], -tangent[3])

                if self.exportColours:
                    colour = vcLayer[layerIndex].color.to_tuple(5)

                if self.exportBones:
                    bones, weights = [-1, -1, -1, -1], [0.0, 0.0, 0.0, 0.0]
                    for index, group in enumerate(v.groups):
                        bones[index] = boneIndexMap[group.group]
                        weights[index] = round(group.weight, 4)
                    bones, weights = tuple(bones), tuple(weights)

                # key used to remove duplicate vertices
                vertexKey = (position, texcrd, normal, tangent, colour, bones, weights)
                vertexIndex = subMesh.vertexDict.get(vertexKey)

                # no existing vertex, so create a new one
                if vertexIndex is None:
                    vertexIndex = subMesh.vertexDict[vertexKey] = len(subMesh.vertexList)
                    subMesh.vertexList.append(vertexKey)

                # ensure that winding order is consistent
                if self.swapYZ:
                    cornerNum = [0, 2, 1][cornerNum]

                # add the index of this vertex to the face
                subMesh.faceList[-1][cornerNum] = vertexIndex

        #----------------------------------------------------------#

        if len(sqm.subMeshList) > 1:

            startIndex = len(sqm.subMeshList[0].vertexList)

            for subMesh in sqm.subMeshList[1:]:
                func = lambda face: tuple(i + startIndex for i in face)
                subMesh.faceList = list(map(func, subMesh.faceList))
                startIndex += len(subMesh.vertexList)

        #----------------------------------------------------------#

        with open(self.filepath, 'w', encoding='utf-8') as o:

            o.write("# SQEE Mesh Format")

            o.write("\n\n\n################################################################################\n")

            o.write("\nSECTION Header\n")

            if self.exportTexCoords or self.exportNormals or self.exportColours or self.exportBones:
                o.write("\nAttributes")
                if self.exportTexCoords: o.write(" TexCoords")
                if self.exportNormals:   o.write(" Normals")
                if self.exportTangents:  o.write(" Tangents")
                if self.exportColours:   o.write(" Colours")
                if self.exportBones:     o.write(" Bones")
                o.write("\n")

            if self.exportBounds:
                o.write("\nOrigin %s %s %s"  % tidy_values(5, *sqm.origin))
                o.write("\nExtents %s %s %s" % tidy_values(5, *sqm.extents))
                o.write("\nRadius %s\n"      % tidy_value(5, sqm.radius))

            for subMesh in sqm.subMeshList:
                args = (subMesh.name, len(subMesh.vertexList), len(subMesh.faceList) * 3)
                o.write("\nSubMesh %s %d %d" % args)

            o.write("\n\n\n################################################################################\n")

            o.write("\nSECTION Vertices\n")

            for subMesh in sqm.subMeshList:

                # comment to seperate sub meshes
                if len(sqm.subMeshList) > 1:
                    smLine = "##### SubMesh '%s' (%d) " % (subMesh.name, len(subMesh.vertexList))
                    o.write("\n\n{:#<60}\n".format(smLine))

                for vert in subMesh.vertexList:

                    # write vertex position attribute
                    o.write("\n%s %s %s" % tidy_values(5, *vert[0]))

                    # write all other attributes which are enabled
                    if self.exportTexCoords: o.write(" %s %s"       % tidy_values(5, *vert[1]))
                    if self.exportNormals:   o.write(" %s %s %s"    % tidy_values(5, *vert[2]))
                    if self.exportTangents:  o.write(" %s %s %s %s" % tidy_values(5, *vert[3]))
                    if self.exportColours:   o.write(" %s %s %s %s" % tidy_values(5, *vert[4]))
                    if self.exportBones:     o.write(" %d %d %d %d" % vert[5])
                    if self.exportBones:     o.write(" %s %s %s %s" % tidy_values(4, *vert[6]))

                o.write("\n")

            o.write("\n\n################################################################################\n")

            o.write("\nSECTION Indices\n")

            for subMesh in sqm.subMeshList:

                # comment to seperate sub meshes
                if len(sqm.subMeshList) > 1:
                    smLine = "##### SubMesh '%s' (%d) " % (subMesh.name, len(subMesh.faceList) * 3)
                    o.write("\n\n{:#<60}\n".format(smLine))

                # write each face is on its own line
                for face in subMesh.faceList:
                    o.write("\n%d %d %d" % tuple(face))

                o.write("\n")

        #----------------------------------------------------------#

        return {'FINISHED'}

#==============================================================================#

def menu_func(self, context):
    self.layout.operator(SqeeExportMesh_operator.bl_idname, text="SQEE Mesh (.sqm)")

def register():
    bpy.utils.register_class(SqeeExportMesh_operator)
    bpy.types.TOPBAR_MT_file_export.append(menu_func)

def unregister():
    bpy.utils.unregister_class(SqeeExportMesh_operator)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func)

#==============================================================================#

if __name__ == "__main__":
    register()
    bpy.ops.sqee.export_mesh_operator('INVOKE_DEFAULT')


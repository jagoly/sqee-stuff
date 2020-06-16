import bpy
from bpy_extras.io_utils import ExportHelper
from mathutils import Vector

#==============================================================================#

bl_info = {
    "name": "SQEE Mesh Exporter",
    "author": "James Gangur",
    "version": (20, 6),
    "blender": (2, 83, 0),
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
        self.hasBbox = False
        self.hasTcrd = False
        self.hasNorm = False
        self.hasTang = False
        self.hasColr = False
        self.hasBone = False
        self.sphereRadius = 0.0
        self.boxCentre = Vector((0, 0, 0))
        self.boxSize = Vector((0, 0, 0))
        self.subMeshList = []

#==============================================================================#

def round_vector(vec, precision):
    return Vector(vec.to_tuple(precision)).freeze()

def tidy_value(val, precision):
    output = ("%%.%df" % precision % val).rstrip("0")
    if output.endswith("."): output += "0"
    if output == "-0.0": output = "0.0"
    return output

def tidy_vector(vec, precision):
    return tuple(tidy_value(v, precision) for v in vec)

#==============================================================================#

class SqExportMesh_operator(bpy.types.Operator, ExportHelper):
    """Export a mesh in the SQEE format"""

    bl_idname = "sq.export_mesh_operator"
    bl_label = "Export SQEE Mesh"

    filename_ext = ".sqm"
    
    filter_glob: bpy.props.StringProperty(default="*.sqm", options={'HIDDEN'})

    exportBounds: bpy.props.BoolProperty(name="Export Bounding Info", default=True)

    useTcrd: bpy.props.BoolProperty(name="Export Texture Coords",  default=True)
    useNorm: bpy.props.BoolProperty(name="Export Vertex Normals",  default=True)
    useTang: bpy.props.BoolProperty(name="Export Vertex Tangents", default=True)
    useColr: bpy.props.BoolProperty(name="Export Vertex Colours",  default=False)
    useBone: bpy.props.BoolProperty(name="Export Bones / Weights", default=False)

    #----------------------------------------------------------#

    def execute(self, context):

        obj = context.active_object
        depsgraph = context.evaluated_depsgraph_get()
        mesh = obj.evaluated_get(depsgraph).to_mesh()
        vcLayer = uvLayer = arma = boneIndexMap = None

        sqm = SqeeMesh()

        sqm.hasTcrd = bool(self.useTcrd)
        sqm.hasNorm = bool(self.useNorm)
        sqm.hasTang = bool(self.useTang)
        sqm.hasColr = bool(self.useColr)
        sqm.hasBone = bool(self.useBone)

        if sqm.hasTang: mesh.calc_tangents()
        if sqm.hasTcrd: uvLayer = mesh.uv_layers.active.data
        if sqm.hasColr: vcLayer = mesh.vertex_colors.active.data
        if sqm.hasBone: arma = obj.parent.data

        #----------------------------------------------------------#

        if self.exportBounds == True:
            sx = sum(vert[0] for vert in obj.bound_box)
            sy = sum(vert[1] for vert in obj.bound_box)
            sz = sum(vert[2] for vert in obj.bound_box)
            sqm.boxCentre = Vector((sx, sy, sz)) / 8.0
            sqm.boxSize = obj.dimensions / 2.0

        #----------------------------------------------------------#

        # create a sub mesh for each material used by the mesh
        sqm.subMeshList = list(map(SqeeSubMesh, mesh.materials.keys()))
        if not sqm.subMeshList: sqm.subMeshList = [SqeeSubMesh("Default")]

        if sqm.hasBone == True: # compute mapping of mesh bone indices to armature bone indices
            boneNames = sorted ( arma.bones, key = lambda bone: (len(bone.parent_recursive), bone.name) )
            boneNames = [ bone.name for bone in boneNames if bone.name[0] != '.' ]
            assert len(boneNames) == len(obj.vertex_groups), "wrong number of vertex groups in mesh"
            print(boneNames)
            print(obj.vertex_groups.keys())
            boneIndexMap = [ boneNames.index(group) for group in obj.vertex_groups.keys() ]

        #----------------------------------------------------------#

        for faceNum, f in enumerate(mesh.polygons):

            # the sub mesh containing this face
            subMesh = sqm.subMeshList[f.material_index]

            # add a new face to the sub mesh
            subMesh.faceList.append([-1, -1, -1])

            for cornerNum, loopIndex in enumerate(f.loop_indices):

                l = mesh.loops[loopIndex]
                v = mesh.vertices[l.vertex_index]

                position = round_vector(v.co, 5)

                if self.exportBounds: # sphere radius
                    distance = (position - sqm.boxCentre).length
                    sqm.sphereRadius = max(sqm.sphereRadius, distance)

                # set all key properties to None
                texcrd = normal = tangent = colour = None

                # used to access uv and colour data
                layerIndex = faceNum * 3 + cornerNum

                if sqm.hasTcrd: # calculate TexCoord
                    texcrd = round_vector(uvLayer[layerIndex].uv, 5)

                if sqm.hasNorm: # calculate Normal
                    normal = (v if f.use_smooth else f).normal
                    normal = round_vector(normal.normalized(), 5)

                if sqm.hasTang: # calculate Tangent
                    tangent = round_vector(l.tangent.normalized(), 5)
                    tangent = tuple((*tangent, l.bitangent_sign))

                if sqm.hasColr: # calculate Colour
                    colour = round_vector(vcLayer[layerIndex].color, 5)

                bones = [-1, -1, -1, -1]
                weights = [0.0, 0.0, 0.0, 0.0]

                if sqm.hasBone: # bones / weights
                    for index, group in enumerate(v.groups):
                        bones[index] = boneIndexMap[group.group]
                        weights[index] = group.weight

                # key used to remove duplicate vertices
                vertexKey = (position, texcrd, normal, tangent, colour)
                vertexIndex = subMesh.vertexDict.get(vertexKey)

                if vertexIndex is None: # no existing vertex, so create a new one
                    vertexIndex = subMesh.vertexDict[vertexKey] = len(subMesh.vertexList)
                    subMesh.vertexList.append((position, texcrd, normal, tangent, colour, bones, weights))

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

            o.write("# SQEE Mesh Format\n")

            o.write("\n\n################################################################################\n")

            o.write("\nSECTION Header\n")

            o.write("\nAttrs")
            if self.useTcrd: o.write(" TCRD")
            if self.useNorm: o.write(" NORM")
            if self.useTang: o.write(" TANG")
            if self.useColr: o.write(" COLR")
            if self.useBone: o.write(" BONE")
            o.write("\n\n")

            if self.exportBounds == True:
                o.write("Origin %s %s %s\n" % tidy_vector(sqm.boxCentre, 5))
                o.write("Extents %s %s %s\n" % tidy_vector(sqm.boxSize, 5))
                o.write("Radius %s\n\n" % tidy_value(sqm.sphereRadius, 5))

            for subMesh in sqm.subMeshList:
                counts = (len(subMesh.vertexList), len(subMesh.faceList) * 3)
                o.write("SubMesh {:d} {:d}\n".format(*counts))


            o.write("\n\n################################################################################\n")

            o.write("\nSECTION Vertices\n")

            for subMesh in sqm.subMeshList:

                # comment to nicely seperate sub meshes
                smInfo = (subMesh.name, len(subMesh.vertexList))
                smLine = "##### SubMesh: '%s' (%d) " % smInfo
                o.write("\n\n{:#<60}\n\n".format(smLine))

                for vert in subMesh.vertexList:

                    # write vertex position attribute
                    o.write("%s %s %s " % tidy_vector(vert[0], 5))

                    # write all other attributes which are enabled
                    if sqm.hasTcrd: o.write("%s %s "        % tidy_vector(vert[1], 5))
                    if sqm.hasNorm: o.write("%s %s %s "     % tidy_vector(vert[2], 5))
                    if sqm.hasTang: o.write("%s %s %s %s "  % tidy_vector(vert[3], 5))
                    if sqm.hasColr: o.write("%s %s %s "     % tidy_vector(vert[4], 5))
                    if sqm.hasBone: o.write("%d %d %d %d "  % tuple(vert[5]))
                    if sqm.hasBone: o.write("%s %s %s %s "  % tidy_vector(vert[6], 4))

                    o.write("\n") # end of vertex

            o.write("\n\n################################################################################\n")

            o.write("\nSECTION Indices\n")

            for subMesh in sqm.subMeshList:

                # comment to nicely seperate sub meshes
                smInfo = (subMesh.name, len(subMesh.faceList) * 3)
                smLine = "##### SubMesh: '%s' (%d) " % smInfo
                o.write("\n\n{:#<60}\n\n".format(smLine))

                for face in subMesh.faceList:

                    # for now each face is on a new line
                    o.write("%d %d %d\n" % tuple(face))

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
    self.layout.operator(SqExportMesh_operator.bl_idname, text="SQEE Mesh (.sqm)")

def register():
    bpy.utils.register_class(SqExportMesh_operator)
    bpy.types.TOPBAR_MT_file_export.append(menu_func)

def unregister():
    bpy.utils.unregister_class(SqExportMesh_operator)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func)

#==============================================================================#

if __name__ == "__main__":
    register()
    bpy.ops.sq.export_mesh_operator('INVOKE_DEFAULT')


bl_info = {
    "name": "Exr Auto Pass Saver",
    "description": "Link all render passes to a new EXR-MulitLayer or EXR-SingleLayer save node",
    "blender": (2, 80, 0),
    "category": "Compositing",
    "author": "3d-io",
    "version": (1, 0),
    "location": "Compositor Tab > Sidebar > Exr Auto Pass Saver",
    "warning": "BSD",
    "wiki_url": "https://github.com/3d-io/",
    "support": "COMMUNITY",
}

import bpy
import subprocess
import os

bpy.types.Scene.exr_auto_pass_saver_clear_all = bpy.props.BoolProperty(
    name="Clear all nodes",
    description="Remove all nodes from the Compositor and add only RenderLayer <-> Saver Node",
    default=False,
)


bpy.types.Scene.exr_auto_pass_saver_open_dir = bpy.props.BoolProperty(
    name="Open destination folder",
    description="A folder where the Exr Image is going to be saved",
    default=False,
)

bpy.types.Scene.single_files = bpy.props.BoolProperty(
    name="Single EXRs",
    description="Create a file output node for each render pass",
    default=True,
)

bpy.types.Scene.main_out_to_jpeg = bpy.props.BoolProperty(
    name="Set main to JPEG",
    description="Set main output format to JPEG to reduce storage usage",
    default=True,
)


class Exr_Auto_Pass_Saver(bpy.types.Operator):
    bl_idname = "node.exr_pass_saver"
    bl_label = "EXR Auto Saver"
    bl_options = {"REGISTER", "UNDO"}

    # removes all currently existing nodes
    def cleannodes(self):
        nodesField = bpy.context.scene.node_tree
        for currentNode in nodesField.nodes:
            nodesField.nodes.remove(currentNode)

    # opens the directory of the current render path
    def openfolder(self):
        path = bpy.path.abspath(bpy.context.scene.render.filepath)
        if not os.path.exists(path):
            os.makedirs(path)
        subprocess.call("explorer " + path.strip("/"), shell=True)

    # returns a target render path taken from the scene's render output and cleaned up as needed
    def GetOutputPathStr(self):
        if bpy.context.scene.single_files:
            fullPath = os.path.join(
                bpy.path.abspath(bpy.context.scene.render.filepath), "SingleEXRs"
            )
        else:
            fullPath = os.path.join(
                bpy.path.abspath(bpy.context.scene.render.filepath),
                "MultiEXRs",
                "renderpasses.",
            )
        return fullPath

    # creates a new Render Layers node at the given position
    def CreateNodeRenderLayers(self, position):
        node = bpy.context.scene.node_tree.nodes.new("CompositorNodeRLayers")
        node.location = position
        return node

    # creates a new Output File node at the given position
    def CreateNodeFileOutput(self, position, sourceNode):
        scene = bpy.context.scene

        if not scene.single_files:

            bpy.context.scene.render.image_settings.file_format = "OPEN_EXR_MULTILAYER"
            bpy.context.scene.render.image_settings.color_mode = "RGBA"
            bpy.context.scene.render.image_settings.color_depth = "16"
            bpy.context.scene.render.image_settings.exr_codec = "ZIPS"
            bpy.context.scene.render.filepath = "//render/"

            node = bpy.context.scene.node_tree.nodes.new("CompositorNodeOutputFile")
            node.label = "EXR-MultiLayer"
            node.name = "EXR-MultiLayer"
            node.base_path = self.GetOutputPathStr()
            node.location = position
            node.width = 300
            node.width_hidden = 300
            node.use_custom_color = True
            node.color = (0.686, 0.204, 0.176)
            return node

        bpy.context.scene.render.image_settings.file_format = "OPEN_EXR"
        bpy.context.scene.render.image_settings.color_mode = "RGBA"
        bpy.context.scene.render.image_settings.color_depth = "16"
        bpy.context.scene.render.image_settings.exr_codec = "ZIPS"
        bpy.context.scene.render.filepath = "//render/"

        node = bpy.context.scene.node_tree.nodes.new("CompositorNodeOutputFile")
        node.label = "EXRs"
        node.name = "EXRs"
        node.base_path = self.GetOutputPathStr()
        node.location = position
        node.width = 300
        node.width_hidden = 300
        node.use_custom_color = True
        node.color = (0.686, 0.204, 0.176)
        return node

    # links all outputs of the source node to inputs of the target node
    def LinkRenderLayers(self, sourceNode, targetNode):
        for out in sourceNode.outputs:

            # skip disabled outputs
            if out.enabled == False:
                continue

            if bpy.context.scene.single_files and out.identifier.startswith(
                "CryptoObject"
            ):
                try:
                    crypto_object_node = bpy.context.scene.node_tree.nodes[
                        "CryptoObject"
                    ]

                except:
                    crypto_object_node = bpy.context.scene.node_tree.nodes.new(
                        "CompositorNodeOutputFile"
                    )
                    crypto_object_node.file_slots.clear()
                    crypto_object_node.label = "CryptoObject"
                    crypto_object_node.name = "CryptoObject"
                    crypto_object_node.format.file_format = "OPEN_EXR_MULTILAYER"
                    crypto_object_node.base_path = (
                        self.GetOutputPathStr() + "/CryptoObject"
                    )
                    crypto_object_node.location = (400, -193)
                    crypto_object_node.width = 300
                    crypto_object_node.width_hidden = 300
                    crypto_object_node.use_custom_color = True
                    crypto_object_node.color = (1.0, 0.5, 0.0)

                crypto_object_node.file_slots.new(out.identifier)
                bpy.context.scene.node_tree.links.new(
                    sourceNode.outputs[out.identifier],
                    crypto_object_node.inputs[out.identifier],
                )
            if bpy.context.scene.single_files and out.identifier.startswith(
                "CryptoMaterial"
            ):
                try:
                    crypto_material_node = bpy.context.scene.node_tree.nodes[
                        "CryptoMaterial"
                    ]

                except:
                    crypto_material_node = bpy.context.scene.node_tree.nodes.new(
                        "CompositorNodeOutputFile"
                    )
                    crypto_material_node.file_slots.clear()
                    crypto_material_node.label = "CryptoMaterial"
                    crypto_material_node.name = "CryptoMaterial"
                    crypto_material_node.format.file_format = "OPEN_EXR_MULTILAYER"
                    crypto_material_node.base_path = (
                        self.GetOutputPathStr() + "/CryptoMaterial"
                    )
                    crypto_material_node.location = (400, -393)
                    crypto_material_node.width = 300
                    crypto_material_node.width_hidden = 300
                    crypto_material_node.use_custom_color = True
                    crypto_material_node.color = (0.0, 0.5, 0.8)

                crypto_material_node.file_slots.new(out.identifier)
                bpy.context.scene.node_tree.links.new(
                    sourceNode.outputs[out.identifier],
                    crypto_material_node.inputs[out.identifier],
                )

            if bpy.context.scene.single_files and out.identifier.startswith(
                "CryptoAsset"
            ):
                try:
                    crypto_asset_node = bpy.context.scene.node_tree.nodes["CryptoAsset"]

                except:
                    crypto_asset_node = bpy.context.scene.node_tree.nodes.new(
                        "CompositorNodeOutputFile"
                    )
                    crypto_asset_node.file_slots.clear()
                    crypto_asset_node.label = "CryptoAsset"
                    crypto_asset_node.name = "CryptoAsset"
                    crypto_asset_node.format.file_format = "OPEN_EXR_MULTILAYER"
                    crypto_asset_node.base_path = (
                        self.GetOutputPathStr() + "/CryptoAsset"
                    )
                    crypto_asset_node.location = (400, -593)
                    crypto_asset_node.width = 300
                    crypto_asset_node.width_hidden = 300
                    crypto_asset_node.use_custom_color = True
                    crypto_asset_node.color = (0.0, 0.5, 0.1)

                crypto_asset_node.file_slots.new(out.identifier)
                bpy.context.scene.node_tree.links.new(
                    sourceNode.outputs[out.identifier],
                    crypto_asset_node.inputs[out.identifier],
                )

            # Combine OIDN Denoising Data to a single denoised pass
            if out.identifier.startswith("Denoising"):
                denoise_node = bpy.context.scene.node_tree.nodes.new(
                    "CompositorNodeDenoise"
                )
                denoise_node.location = (400, 580)
                bpy.context.scene.node_tree.links.new(
                    sourceNode.outputs["Image"], denoise_node.inputs["Image"]
                )
                bpy.context.scene.node_tree.links.new(
                    sourceNode.outputs["Denoising Normal"],
                    denoise_node.inputs["Normal"],
                )
                bpy.context.scene.node_tree.links.new(
                    sourceNode.outputs["Denoising Albedo"],
                    denoise_node.inputs["Albedo"],
                )
                targetNode.file_slots.new("Denoised_Image")
                bpy.context.scene.node_tree.links.new(
                    denoise_node.outputs["Image"],
                    targetNode.inputs["Denoised_Image"],
                )
                bpy.context.scene.render.image_settings.file_format
                return

            slot = 0
            found = False
            for src in targetNode.inputs:
                if src.identifier == out.identifier:
                    # target node already has matching input, link to it
                    found = True
                    bpy.context.scene.node_tree.links.new(out, targetNode.inputs[slot])
                    break
                slot = slot + 1
            if (
                bpy.context.scene.single_files
                and not found
                and not out.identifier.startswith("Crypto")
                and not out.identifier.startswith("Noisy")
            ) or (
                not found
                and not bpy.context.scene.single_files
                and not out.identifier.startswith("Noisy")
            ):
                # target node has no matching input, create one and link to it
                targetNode.file_slots.new(out.identifier.replace(" ", "_"))
                bpy.context.scene.node_tree.links.new(out, targetNode.inputs[-1])

    # Exr Auto Saver button
    # Generates reqired nodes for the OpenEXR output and links available render passes
    def execute(self, context):
        scene = bpy.context.scene  # get the scene

        if not scene.use_nodes:
            bpy.context.scene.use_nodes = 1

        if scene.exr_auto_pass_saver_clear_all:
            self.cleannodes()

        if scene.exr_auto_pass_saver_open_dir:
            self.openfolder()

        layersNode = self.CreateNodeRenderLayers((0, 400))
        outputNode = self.CreateNodeFileOutput((800, 450), layersNode)
        self.LinkRenderLayers(layersNode, outputNode)
        if scene.main_out_to_jpeg:
            bpy.context.scene.render.image_settings.file_format = "JPEG"
        return {"FINISHED"}


class Exr_Auto_Pass_Saver_Panel(bpy.types.Panel):
    bl_label = "Exr Auto Pass Saver"
    bl_category = "Exr Auto Pass Saver"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"

    def draw(self, context):
        layout = self.layout
        layout.label(text="Link all nodes:")
        # draw Auto Saver button
        row = layout.row()
        row.scale_y = 2.0
        row.operator(Exr_Auto_Pass_Saver.bl_idname, icon="TRACKING_FORWARDS")
        sce = context.scene
        # draw the checkbox (implied from property type = bool)
        layout.prop(sce, "exr_auto_pass_saver_clear_all")
        layout.prop(sce, "exr_auto_pass_saver_open_dir")
        layout.prop(sce, "single_files")
        layout.prop(sce, "main_out_to_jpeg")


classes = (Exr_Auto_Pass_Saver_Panel, Exr_Auto_Pass_Saver)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()

# (GNU GPL) <2022> <Taiseibutsu>" Developed for Blender 3.2, Tested on 3.1
# This program is free software: you can redistribute it and/or modify it, WITHOUT ANY WARRANTY that wont wake up on the backrooms. --- Kreepyrights is just a joke, this is license under GNU General Public License (GPL, or “free software”), but just with a strange name to reference, or maybe not...

bl_info = {
    "name": "Data_Tool_Renamer (DTR)", "author": "TBY",
    "version": (0, 0, 2), "blender": (4, 2, 0), "location": "3D View, N Panel",
    "description": "Custom tools for assigning names between object name and data-blocks",
    "wiki_url": "", "category": "TBY"}

import bpy, addon_utils, os, rna_keymap_ui
from bpy.types import AddonPreferences, Panel

class TBY_DTR_Properties(bpy.types.PropertyGroup):
    nametorename : bpy.props.StringProperty(default = "Enter Name", description = "Name that will be assigned to active object")
    renamerfrom : bpy.props.EnumProperty(
        name = "Enumerator/Dropdown",
        description = "Object that will rename",
        items= [('OBJECT', 'Object', 'Import name from Object','OBJECT_DATA',0),
                ('DATABLOCK','Data-block','Import name from Data-Block', 'MESH_DATA', 1),
                ('MATERIAL','Material','Import name from Active Material', 'MATERIAL', 2),
                ('ACTION','Action','Import name from Animation', 'ACTION', 3)
        ]
    )
    renamermode : bpy.props.EnumProperty(
        name = "Enumerator/Dropdown",
        description = "Mode to rename",
        items= [('SCENE', 'Scene', 'Export name to Scene','SCENE_DATA',0),
                ('SELECTION','Selection','Export name to Selection', 'RESTRICT_SELECT_OFF', 1),
                ('COLLECTION','Collection','Export name to Selected Colection', 'OUTLINER_COLLECTION', 2),
                ('ALL','All','Export name to All Objects', 'BLENDER', 3)
        ]
    )
    renamertoscene : bpy.props.PointerProperty(type=bpy.types.Scene)
    renamertosceneactive : bpy.props.BoolProperty(default = True, description = "Transfer Name to Active Scene")

    renamertocollection : bpy.props.PointerProperty(type=bpy.types.Collection)
    renamertocollectionactive : bpy.props.BoolProperty(default = False, description = "Transfer Name to ActiveCollection")

    renamertoobject : bpy.props.BoolProperty(default = True, description = "Transfer Name to Object")
    renamertodatablock : bpy.props.BoolProperty(default = True, description = "Transfer Name to Data-Block")
    renamertoaction : bpy.props.BoolProperty(default = False, description = "Transfer Name to Animation")
    renamertomaterial : bpy.props.BoolProperty(default = False, description = "Transfer Name to Material")

    tby_collapse_panel : bpy.props.BoolProperty(default = True, description = "Collapse/Expanse readability of the panel")
    tby_show_active_name : bpy.props.BoolProperty(default = True, description = "Show object, mesh, material and action name on panel")

def setrenamename(ob,renamename):
    tbtool = bpy.context.scene.tby_data_tool
    if tbtool.renamerfrom !='OBJECT' and tbtool.renamertoobject:
        ob.name = renamename
    if tbtool.renamerfrom !='DATABLOCK' and tbtool.renamertodatablock:
        ob.data.name = renamename
    if tbtool.renamerfrom !='ACTION' and tbtool.renamertoaction:
        #if ob.animation_data != None:   
            #bpy.data.actions.new(renamename)
        #else:
        ob.animation_data.action.name = renamename
    if tbtool.renamerfrom !='MATERIAL' and tbtool.renamertomaterial and ob.active_material != None:
        ob.active_material.name = renamename
      
def renamerename(ob):
    tbtool = bpy.context.scene.tby_data_tool
    if tbtool.renamerfrom =='OBJECT':
        renamename = ob.name
        setrenamename(ob,renamename)
    if tbtool.renamerfrom =='DATABLOCK':
        renamename = ob.data.name
        setrenamename(ob,renamename)
    if tbtool.renamerfrom =='ACTION':
        if ob.animation_data != None:
            if ob.animation_data.action != None:
                renamename = ob.animation_data.action.name
                setrenamename(ob,renamename)
    if tbtool.renamerfrom =='MATERIAL':
        if ob.active_material != None:
            print("HAS MATERIAL")
            renamename = ob.active_material.name
            setrenamename(ob,renamename)        

class TBY_RENAMER(bpy.types.Operator):
    bl_idname = "tby_ops.renamercut"
    bl_label = "Renames data"
    bl_description = "Rename Data"
    
    def execute(self, context):
        acobj = bpy.context.active_object
        acobjt = acobj.type
        tbtool = context.scene.tby_data_tool

        if tbtool.renamermode =='SELECTION':  
            for ob in bpy.context.selected_objects:
                renamerename(ob)        
        if tbtool.renamermode =='ALL':
            for ob in bpy.data.objects:
                renamerename(ob)                  
        if tbtool.renamermode =='SCENE':
            if tbtool.renamertosceneactive:
                for ob in bpy.context.scene.objects:
                    renamerename(ob) 
            else:
                if tbtool.renamertoscene != None:
                    for ob in tbtool.renamertoscene.objects:
                        renamerename(ob) 
        if tbtool.renamermode =='COLLECTION':
            if tbtool.renamertocollectionactive:
                for ob in bpy.context.collection.objects:
                    renamerename(ob) 
            else:
                if tbtool.renamertocollection != None:
                    for ob in tbtool.renamertocollection.objects:
                        renamerename(ob)
        return {"FINISHED"}


def tbdatarenamer(self, context):
    acobj = bpy.context.active_object
    acobjt = acobj.type
    if acobjt != 'EMPTY':
        tbtool = context.scene.tby_data_tool
        
        layout = self.layout
        box = layout.box()
        row = box.row(align=True)
        if tbtool.tby_collapse_panel:
            row.prop(tbtool,"tby_collapse_panel",text="Collapse Panel",icon='FULLSCREEN_EXIT')
        else:
            row.prop(tbtool,"tby_collapse_panel",text="Expand Panel",icon='FULLSCREEN_ENTER')
        row.separator()
        row.prop(tbtool,"tby_show_active_name", text="Linked Names", icon='SYNTAX_OFF')

        if acobjt != 'GPENCIL' and acobjt != 'LIGHT_PROBE' and acobjt != 'SPEAKER':
            datablockicon = bpy.context.active_object.type + '_DATA'
        elif acobjt == 'GPENCIL':
            datablockicon = 'OUTLINER_DATA_GREASEPENCIL'
        elif acobjt == 'LIGHT_PROBE':
            datablockicon = 'OUTLINER_DATA_LIGHTPROBE'
        elif acobjt == 'SPEAKER':
            datablockicon = 'SPEAKER'
        

        if tbtool.tby_show_active_name:
            box = layout.box()
            row = box.row(align=True)
            row.template_ID(context.view_layer.objects, "active", filter='AVAILABLE')
            if tbtool.renamertodatablock:
                row.template_ID(context.view_layer.objects.active, "data")
            if tbtool.renamerfrom =='ACTION' or tbtool.renamerfrom =='MATERIAL' or tbtool.renamertomaterial and acobjt in ['MESH','META','HAIR','CURVE','POINTCLOUD','SURFACE','GPENCIL','VOLUME'] or tbtool.renamertoaction:
                row = box.row(align=True)
            if tbtool.renamerfrom =='MATERIAL' or tbtool.renamertomaterial and acobjt in ['MESH','META','HAIR','CURVE','POINTCLOUD','SURFACE','GPENCIL','VOLUME']:
                row.template_ID(acobj, "active_material", new="material.new")
            if (tbtool.renamerfrom =='ACTION' or tbtool.renamertoaction) and (tbtool.renamerfrom =='MATERIAL' or tbtool.renamertomaterial and acobjt in ['MESH','META','HAIR','CURVE','POINTCLOUD','SURFACE','GPENCIL','VOLUME']):
                row.separator()
            if tbtool.renamertoaction or tbtool.renamerfrom =='ACTION':        
                #layout.template_ID(st, "action", new="action.new", unlink="action.unlink")
                if acobj.animation_data.action != None:
                    row.prop(acobj.animation_data.action, "name" , text="",icon='ACTION')
                else:
                    row.label(text="No Active Action",icon='ACTION')

        box = layout.box()
        if tbtool.tby_collapse_panel:
            row = box.row(align=True)
            row.label(text="Rename From")
        else:
            row = box.row(align=True)
        if tbtool.renamerfrom == 'DATABLOCK':
            row.prop(tbtool, "renamerfrom",text="",icon=datablockicon)
        else:
            row.prop(tbtool, "renamerfrom",text="")
        if tbtool.tby_collapse_panel:
            row = box.row(align=True)
            row.label(text="To")
            texticonob = "Object"
            texticondb = "Data-Block"
            texticonmat = "Material"
            texticonac = "Action" 
        else:
            texticonob = ""
            texticondb = ""
            texticonmat = ""
            texticonac = "" 
        row.label(icon='TRACKING_FORWARDS_SINGLE')
        if tbtool.renamerfrom != 'DATABLOCK':
            row.prop(tbtool, "renamertodatablock",text=texticondb,icon=datablockicon)
        if tbtool.renamerfrom != 'OBJECT':
            row.prop(tbtool, "renamertoobject",text=texticonob,icon='OBJECT_DATA')
        if tbtool.renamerfrom != 'ACTION':
            row.prop(tbtool, "renamertoaction",text=texticonac,icon='ACTION')
        if acobj.type in {'MESH','SURFACE','CURVE','FONT','META','GPENCIL'}:
            if tbtool.renamerfrom != 'MATERIAL':
                row.prop(tbtool, "renamertomaterial",text=texticonmat,icon='MATERIAL')
        if tbtool.tby_collapse_panel:
            row = box.row(align=True)
            row.label(text="Rename for")
        else:
            row.separator()
        if tbtool.renamermode =='SCENE':
            if tbtool.renamertosceneactive:
                row.prop(tbtool, "renamertosceneactive",text="Active Scene",icon='PIVOT_ACTIVE')
            else:
                row.prop(tbtool, "renamertoscene",text="",icon='SCENE_DATA')
                row.prop(tbtool, "renamertosceneactive",text="",icon='PIVOT_ACTIVE')
        if tbtool.renamermode =='COLLECTION':
            if tbtool.renamertocollectionactive:
                row.prop(tbtool, "renamertocollectionactive",text="Active Collection",icon='PIVOT_ACTIVE')
            else:
                row.prop(tbtool, "renamertocollection",text="",icon='OUTLINER_COLLECTION')
                row.prop(tbtool, "renamertocollectionactive",text="",icon='PIVOT_ACTIVE')
        
        if tbtool.renamermode in ['COLLECTION','SCENE']:
            icononlyrename = True
        else:
            icononlyrename = False
        row.prop(tbtool, "renamermode",text="",icon_only=icononlyrename)
        if tbtool.tby_collapse_panel:
            box = layout.box()
        row = box.row(align=True)
        row.operator("tby_ops.renamercut",text="Rename",icon='SORTALPHA')

    else:
        layout = self.layout
        row = layout.row(align=True)
        row.label(text="Empty Data has nolinked Data Block",icon='EMPTY_DATA')
        row = layout.row(align=True)
        row.template_ID(context.view_layer.objects, "active", filter='AVAILABLE')
        if acobj.empty_display_type == 'IMAGE':
            row = layout.row(align=True)
            row.template_ID(acobj, "data", open="image.open", unlink="object.unlink_data")

class tby_data_toolS_PNL(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "TB"
    bl_label = ""
    bl_idname = "TBY_PNL_Data_Tools"
    @classmethod
    def poll(cls, context):
        return context.object is not None
    def draw_header(self,context):
        tbtool = context.scene.tby_data_tool
        layout = self.layout
        layout.label(icon='FILE_TEXT')
        layout.label(text="Data_Tool_Renamer")
    def draw (self,context):
        tbdatarenamer(self, context)

class tby_data_toolS_PNL_POP(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "tbycontext.tbdatarenamerpopup"
    bl_label = "Data Renamer"
    @classmethod
    def poll(cls, context):
        return context.object is not None
    def invoke(self, context, event):
        widthsize = 500     
        return context.window_manager.invoke_props_dialog(self,width = widthsize)        
    def draw(self, context):
        tbdatarenamer(self, context)
    def execute(self, context):
        return {'FINISHED'}

class TBY_Datarenamer_PreferencesPanel(AddonPreferences):
    bl_idname = __name__
    def draw(self, context):
        layout = self.layout
        box=layout.box()
        tbtool = context.scene.tby_data_tool
        if tbtool.tby_collapse_panel:
            box.prop(tbtool,"tby_collapse_panel",text="Collapse Panel",icon='FULLSCREEN_EXIT')
        else:
            box.prop(tbtool,"tby_collapse_panel",text="Expand Panel",icon='FULLSCREEN_ENTER')
            box=layout.box()
            box.label(text="Hotkey:")
            col = box.column()
            kc = bpy.context.window_manager.keyconfigs.addon
            for km, kmi in addon_keymaps:
                km = km.active()
                col.context_pointer_set("keymap", km)
                rna_keymap_ui.draw_kmi([], kc, km, kmi, col, 0)
            row = layout.row()
            col = row.column()
            col.prop(self, "TBOVER", text="")


classes = (
    TBY_DTR_Properties,
    tby_data_toolS_PNL,
    tby_data_toolS_PNL_POP,
    TBY_Datarenamer_PreferencesPanel,
    TBY_RENAMER,
    )
addon_keymaps = []         


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
        bpy.types.Scene.tby_data_tool = bpy.props.PointerProperty(type= TBY_DTR_Properties)
 #KEYMAP
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
     #VIEW3D        
        km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
        kmi = km.keymap_items.new("tbycontext.tbdatarenamerpopup", 'F2', 'PRESS', alt=True, ctrl=False, shift=False)
        kmi.active = True
        addon_keymaps.append((km, kmi))


def unregister():
 #CLASSES
    for cls in classes:
        bpy.utils.unregister_class(cls)
        bpy.types.Scene.tby_data_tool
 #KEYMAP
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()        
if __name__ == "__main__":
    register()

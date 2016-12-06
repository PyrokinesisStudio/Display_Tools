# space_view_3d_display_tools.py Copyright (C) 2014, Jordi Vall-llovera
#
# Multiple display tools for fast navigate/interact with the viewport
#
# ***** BEGIN GPL LICENSE BLOCK *****
#
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ***** END GPL LICENCE BLOCK *****

bl_info = {
    "name": "Display Tools",
    "author": "Jordi Vall-llovera Medina, Jhon Wallace",
    "version": (1, 6, 0),
    "blender": (2, 7, 0),
    "location": "Toolshelf",
    "description": "Display tools for fast navigate/interact with the viewport",
    "warning": "",
    "wiki_url": "http://wiki.blender.org/index.php/Extensions:2.6/Py/Scripts/"
                "3D_interaction/Display_Tools",
    "tracker_url": "",
    "category": "3D View"}

"""
Additional links:
    Author Site: http://www.jordiart.com
"""

import bpy
from bpy.types import (
        Operator,
        Panel,
        )
from bpy.props import (
        IntProperty,
        BoolProperty,
        EnumProperty,
        )


# Fast Navigate toggle function
def trigger_fast_navigate(trigger):
    scene = bpy.context.scene
    scene.FastNavigateStop = False

    trigger = not trigger


# Control how to display particles during fast navigate
def display_particles(mode):
    scene = bpy.context.scene

    if mode is True:
        for particles in bpy.data.particles:
            if particles.type == 'EMITTER':
                particles.draw_method = 'DOT'
                particles.draw_percentage = 100
            else:
                particles.draw_method = 'RENDER'
                particles.draw_percentage = 100
    else:
        for particles in bpy.data.particles:
            if particles.type == 'EMITTER':
                particles.draw_method = 'DOT'
                particles.draw_percentage = scene.ParticlesPercentageDisplay
            else:
                particles.draw_method = 'RENDER'
                particles.draw_percentage = scene.ParticlesPercentageDisplay


# Do repetitive fast navigate related stuff
def fast_navigate_stuff(self, context, event):
    scene = bpy.context.scene
    view = context.space_data

    if bpy.context.area.type != 'VIEW_3D':
        return self.cancel(context)

    if event.type == 'ESC' or event.type == 'RET' or event.type == 'SPACE':
        return self.cancel(context)

    if scene.FastNavigateStop is True:
        return self.cancel(context)

    # fast navigate while orbit/panning
    if event.type == 'MIDDLEMOUSE':
        if scene.Delay is True:
            if scene.DelayTime < scene.DelayTimeGlobal:
                scene.DelayTime += 1
        view.viewport_shade = scene.FastMode
        self.mode = False

    # fast navigate while transform operations
    if event.type == 'G' or event.type == 'R' or event.type == 'S':
        if scene.Delay is True:
            if scene.DelayTime < scene.DelayTimeGlobal:
                scene.DelayTime += 1
        view.viewport_shade = scene.FastMode
        self.mode = False

    # fast navigate while menu popups or duplicates
    if event.type == 'W' or event.type == 'D' or event.type == 'L'\
      or event.type == 'U' or event.type == 'I' or event.type == 'M'\
      or event.type == 'A' or event.type == 'B':
        if scene.Delay is True:
            if scene.DelayTime < scene.DelayTimeGlobal:
                scene.DelayTime += 1
        view.viewport_shade = scene.FastMode
        self.mode = False

    # fast navigate while numpad navigation
    if event.type == 'NUMPAD_PERIOD' or event.type == 'NUMPAD_1'\
      or event.type == 'NUMPAD_2' or event.type == 'NUMPAD_3'\
      or event.type == 'NUMPAD_4' or event.type == 'NUMPAD_5'\
      or event.type == 'NUMPAD_6' or event.type == 'NUMPAD_7'\
      or event.type == 'NUMPAD_8' or event.type == 'NUMPAD_9':
        if scene.Delay is True:
            if scene.DelayTime < scene.DelayTimeGlobal:
                scene.DelayTime += 1
        view.viewport_shade = scene.FastMode
        self.mode = False

    # fast navigate while zooming with mousewheel too
    if event.type == 'WHEELUPMOUSE' or event.type == 'WHEELDOWNMOUSE':
        scene.DelayTime = scene.DelayTimeGlobal
        view.viewport_shade = scene.FastMode
        self.mode = False

    if event.type == 'MOUSEMOVE':
        if scene.Delay is True:
            if scene.DelayTime == 0:
                scene.DelayTime = scene.DelayTimeGlobal
                view.viewport_shade = scene.OriginalMode
                self.mode = True
        else:
            view.viewport_shade = scene.OriginalMode
            self.mode = True

    if scene.Delay is True:
        scene.DelayTime -= 1
        if scene.DelayTime == 0:
            scene.DelayTime = scene.DelayTimeGlobal
            view.viewport_shade = scene.OriginalMode
            self.mode = True

    if scene.ShowParticles is False:
        for particles in bpy.data.particles:
            if particles.type == 'EMITTER':
                particles.draw_method = 'NONE'
            else:
                particles.draw_method = 'NONE'
    else:
        display_particles(self.mode)


# Fast Navigate operator
class FastNavigate(Operator):
    bl_idname = "view3d.fast_navigate_operator"
    bl_label = "Fast Navigate"
    bl_description = "Operator that runs Fast navigate in modal mode"

    trigger = BoolProperty(default=False)
    mode = BoolProperty(default=False)

    def modal(self, context, event):
        scene = bpy.context.scene

        if scene.EditActive is True:
            fast_navigate_stuff(self, context, event)
            return {'PASS_THROUGH'}
        else:
            obj = context.active_object
            if obj:
                if obj.mode != 'EDIT':
                    fast_navigate_stuff(self, context, event)
                    return {'PASS_THROUGH'}
                else:
                    return {'PASS_THROUGH'}
            else:
                fast_navigate_stuff(self, context, event)
                return {'PASS_THROUGH'}

    def execute(self, context):
        context.window_manager.modal_handler_add(self)
        trigger_fast_navigate(self.trigger)
        scene = bpy.context.scene
        scene.DelayTime = scene.DelayTimeGlobal
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        scene = context.scene
        for particles in bpy.data.particles:
            particles.draw_percentage = scene.InitialParticles
        return {'CANCELLED'}


# Fast Navigate Stop
def fast_navigate_stop(context):
    scene = bpy.context.scene
    scene.FastNavigateStop = True


# Fast Navigate Stop Operator
class FastNavigateStop(Operator):
    bl_idname = "view3d.fast_navigate_stop"
    bl_label = "Stop"
    bl_description = "Stop Fast Navigate Operator"

    FastNavigateStop = IntProperty(
                            name="FastNavigateStop",
                            description="Stop fast navigate mode",
                            default=0
                            )

    def execute(self, context):
        fast_navigate_stop(context)
        return {'FINISHED'}


# Drawtype textured
def draw_textured(context):
    view = context.space_data
    view.viewport_shade = 'TEXTURED'
    bpy.context.scene.game_settings.material_mode = 'GLSL'
    selection = bpy.context.selected_objects

    if not selection:
        for obj in bpy.data.objects:
            obj.draw_type = 'TEXTURED'
    else:
        for obj in selection:
            obj.draw_type = 'TEXTURED'


class DisplayTextured(Operator):
    bl_idname = "view3d.display_textured"
    bl_label = "Textured"
    bl_description = "Display objects in textured mode"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        draw_textured(context)
        return {'FINISHED'}


# Drawtype solid
def draw_solid(context):
    view = context.space_data
    view.viewport_shade = 'TEXTURED'
    bpy.context.scene.game_settings.material_mode = 'GLSL'
    selection = bpy.context.selected_objects

    if not(selection):
        for obj in bpy.data.objects:
            obj.draw_type = 'SOLID'
    else:
        for obj in selection:
            obj.draw_type = 'SOLID'


class DisplaySolid(Operator):
    bl_idname = "view3d.display_solid"
    bl_label = "Solid"
    bl_description = "Display objects in solid mode"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        draw_solid(context)

        return {'FINISHED'}


# Drawtype wire
def draw_wire(context):
    view = context.space_data
    view.viewport_shade = 'TEXTURED'
    bpy.context.scene.game_settings.material_mode = 'GLSL'
    selection = bpy.context.selected_objects

    if not(selection):
        for obj in bpy.data.objects:
            obj.draw_type = 'WIRE'
    else:
        for obj in selection:
            obj.draw_type = 'WIRE'


class DisplayWire(Operator):
    bl_idname = "view3d.display_wire"
    bl_label = "Wire"
    bl_description = "Display objects in wireframe mode"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        draw_wire(context)
        return {'FINISHED'}


# Drawtype bounds
def draw_bounds(context):
    view = context.space_data
    view.viewport_shade = 'TEXTURED'
    bpy.context.scene.game_settings.material_mode = 'GLSL'
    selection = bpy.context.selected_objects

    if not(selection):
        for obj in bpy.data.objects:
            obj.draw_type = 'BOUNDS'
    else:
        for obj in selection:
            obj.draw_type = 'BOUNDS'


class DisplayBounds(Operator):
    bl_idname = "view3d.display_bounds"
    bl_label = "Bounds"
    bl_description = "Display objects in bounds mode"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        draw_bounds(context)
        return {'FINISHED'}


# Shade smooth
def shade_smooth(context):
    selection = bpy.context.selected_objects
    try:
        if not(selection):
            for obj in bpy.data.objects:
                bpy.ops.object.select_all(action='TOGGLE')
                bpy.ops.object.shade_smooth()
                bpy.ops.object.select_all(action='TOGGLE')
        else:
            obj = context.active_object
            if obj.mode == 'OBJECT':
                for obj in selection:
                    bpy.ops.object.shade_smooth()
            else:
                bpy.ops.mesh.faces_shade_smooth()
    except:
        print("Setting shade smooth failed")


class DisplayShadeSmooth(Operator):
    bl_idname = "view3d.display_shade_smooth"
    bl_label = "Smooth"
    bl_description = "Display shade smooth meshes"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        shade_smooth(context)
        return {'FINISHED'}


# Shade flat
def shade_flat(context):
    selection = bpy.context.selected_objects

    if not(selection):
        for obj in bpy.data.objects:
            bpy.ops.object.select_all(action='TOGGLE')
            bpy.ops.object.shade_flat()
            bpy.ops.object.select_all(action='TOGGLE')
    else:
        obj = context.active_object
        if obj.mode == 'OBJECT':
            for obj in selection:
                bpy.ops.object.shade_flat()
        else:
            bpy.ops.mesh.faces_shade_flat()


class DisplayShadeFlat(Operator):
    bl_idname = "view3d.display_shade_flat"
    bl_label = "Flat"
    bl_description = "Display shade flat meshes"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        shade_flat(context)
        return {'FINISHED'}


# Shadeless on
def shadeless_on(context):
    selection = bpy.context.selected_objects

    if not(selection):
        for obj in bpy.data.materials:
            obj.use_shadeless = True
    else:
        for sel in selection:
            if sel.type == 'MESH':
                materials = sel.data.materials
                for mat in materials:
                    mat.use_shadeless = True


class DisplayShadelessOn(Operator):
    bl_idname = "view3d.display_shadeless_on"
    bl_label = "On"
    bl_description = "Display shadeless material"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        shadeless_on(context)
        return {'FINISHED'}


# Shadeless off
def shadeless_off(context):
    selection = bpy.context.selected_objects

    if not(selection):
        for obj in bpy.data.materials:
            obj.use_shadeless = False
    else:
        for sel in selection:
            if sel.type == 'MESH':
                materials = sel.data.materials
                for mat in materials:
                    mat.use_shadeless = False


class DisplayShadelessOff(Operator):
    bl_idname = "view3d.display_shadeless_off"
    bl_label = "Off"
    bl_description = "Display shaded material"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        shadeless_off(context)
        return {'FINISHED'}


# Wireframe on
def wire_on(context):
    selection = bpy.context.selected_objects

    if not(selection):
        for obj in bpy.data.objects:
            obj.show_wire = True
            obj.show_all_edges = True

    else:
        for obj in selection:
            obj.show_wire = True
            obj.show_all_edges = True


class DisplayWireframeOn(Operator):
    bl_idname = "view3d.display_wire_on"
    bl_label = "On"
    bl_description = "Display wireframe overlay on"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        wire_on(context)
        return {'FINISHED'}


# Wireframe off
def wire_off(context):
    selection = bpy.context.selected_objects

    if not(selection):
        for obj in bpy.data.objects:
            obj.show_wire = False
            obj.show_all_edges = False

    else:
        for obj in selection:
            obj.show_wire = False
            obj.show_all_edges = False


class DisplayWireframeOff(Operator):
    bl_idname = "view3d.display_wire_off"
    bl_label = "Off"
    bl_description = "Display wireframe overlay off"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        wire_off(context)
        return {'FINISHED'}


# Bounds on
def bounds_on(context):
    scene = context.scene
    selection = bpy.context.selected_objects

    if not(selection):
        for obj in bpy.data.objects:
            obj.show_bounds = True
            obj.draw_bounds_type = scene.BoundingMode
    else:
        for obj in selection:
            obj.show_bounds = True
            obj.draw_bounds_type = scene.BoundingMode


class DisplayBoundsOn(Operator):
    bl_idname = "view3d.display_bounds_on"
    bl_label = "On"
    bl_description = "Display Bounding box overlay on"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        bounds_on(context)
        return {'FINISHED'}


# Wireframe off
def bounds_off(context):
    selection = bpy.context.selected_objects

    if not(selection):
        for obj in bpy.data.objects:
            obj.show_bounds = False
    else:
        for obj in selection:
            obj.show_bounds = False


class DisplayBoundsOff(Operator):
    bl_idname = "view3d.display_bounds_off"
    bl_label = "Off"
    bl_description = "Display Bounding box overlay off"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        bounds_off(context)
        return {'FINISHED'}


# Double Sided on
def double_sided_on(context):
    selection = bpy.context.selected_objects

    if not(selection):
        for mesh in bpy.data.meshes:
            mesh.show_double_sided = True
    else:
        for sel in selection:
            if sel.type == 'MESH':
                mesh = sel.data
                mesh.show_double_sided = True


class DisplayDoubleSidedOn(Operator):
    bl_idname = "view3d.display_double_sided_on"
    bl_label = "On"
    bl_description = "Turn on face double shaded mode"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        double_sided_on(context)
        return {'FINISHED'}


# Double Sided off
def double_sided_off(context):
    selection = bpy.context.selected_objects

    if not(selection):
        for mesh in bpy.data.meshes:
            mesh.show_double_sided = False
    else:
        for sel in selection:
            if sel.type == 'MESH':
                mesh = sel.data
                mesh.show_double_sided = False


class DisplayDoubleSidedOff(Operator):
    bl_idname = "view3d.display_double_sided_off"
    bl_label = "Off"
    bl_description = "Turn off face double sided shade mode"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        double_sided_off(context)
        return {'FINISHED'}


# XRay on
def x_ray_on(context):
    selection = bpy.context.selected_objects

    if not(selection):
        for obj in bpy.data.objects:
            obj.show_x_ray = True
    else:
        for obj in selection:
            obj.show_x_ray = True


class DisplayXRayOn(Operator):
    bl_idname = "view3d.display_x_ray_on"
    bl_label = "On"
    bl_description = "X-Ray display on"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        x_ray_on(context)
        return {'FINISHED'}


# XRay off
def x_ray_off(context):
    selection = bpy.context.selected_objects

    if not(selection):
        for obj in bpy.data.objects:
            obj.show_x_ray = False
    else:
        for obj in selection:
            obj.show_x_ray = False


class DisplayXRayOff(Operator):
    bl_idname = "view3d.display_x_ray_off"
    bl_label = "Off"
    bl_description = "X-Ray display off"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        x_ray_off(context)
        return {'FINISHED'}


# Set Render Settings
def set_render_settings(conext):
    scene = bpy.context.scene
    render = scene.render
    render.simplify_subdivision = 0
    render.simplify_shadow_samples = 0
    render.simplify_child_particles = 0
    render.simplify_ao_sss = 0


class DisplaySimplify(Operator):
    '''Display scene simplified'''
    bl_idname = "view3d.display_simplify"
    bl_label = "Reset"

    Mode = EnumProperty(
        items=[('WIREFRAME', 'Wireframe', ''),
                 ('BOUNDBOX', 'Bounding Box', '')],
        name="Mode"
        )
    ShowParticles = BoolProperty(
        name="ShowParticles",
        description="Show or hide particles on fast navigate mode",
        default=True
        )
    ParticlesPercentageDisplay = IntProperty(
        name="Display",
        description="Display a percentage value of particles",
        default=25,
        min=0,
        max=100,
        soft_min=0,
        soft_max=100,
        subtype='FACTOR'
        )

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        set_render_settings(context)
        return {'FINISHED'}


# Display Modifiers Render on
def modifiers_render_on(context):
    scene = bpy.context.scene
    scene['Simplify'] = 1

    selection = bpy.context.selected_objects

    if not(selection):
        for obj in bpy.data.objects:
            for mod in obj.modifiers:
                mod.show_render = True
    else:
        for obj in selection:
            for mod in obj.modifiers:
                mod.show_render = True


class DisplayModifiersRenderOn(Operator):
    bl_idname = "view3d.display_modifiers_render_on"
    bl_label = "On"
    bl_description = "Display modifiers in render"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        modifiers_render_on(context)
        return {'FINISHED'}


# Display Modifiers Render off
def modifiers_render_off(context):
    selection = bpy.context.selected_objects

    if not(selection):
        for obj in bpy.data.objects:
            for mod in obj.modifiers:
                mod.show_render = False
    else:
        for obj in selection:
            for mod in obj.modifiers:
                mod.show_render = False


class DisplayModifiersRenderOff(Operator):
    bl_idname = "view3d.display_modifiers_render_off"
    bl_label = "Off"
    bl_description = "Hide modifiers in render"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        modifiers_render_off(context)
        return {'FINISHED'}


# Display Modifiers Viewport on
def modifiers_viewport_on(context):
    selection = bpy.context.selected_objects

    if not(selection):
        for obj in bpy.data.objects:
            for mod in obj.modifiers:
                mod.show_viewport = True
    else:
        for obj in selection:
            for mod in obj.modifiers:
                mod.show_viewport = True


class DisplayModifiersViewportOn(Operator):
    bl_idname = "view3d.display_modifiers_viewport_on"
    bl_label = "On"
    bl_description = "Display modifiers in viewport"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        modifiers_viewport_on(context)
        return {'FINISHED'}


# Display Modifiers Viewport off
def modifiers_viewport_off(context):
    selection = bpy.context.selected_objects

    if not(selection):
        for obj in bpy.data.objects:
            for mod in obj.modifiers:
                mod.show_viewport = False
    else:
        for obj in selection:
            for mod in obj.modifiers:
                mod.show_viewport = False


class DisplayModifiersViewportOff(Operator):
    bl_idname = "view3d.display_modifiers_viewport_off"
    bl_label = "Off"
    bl_description = "Hide modifiers in viewport"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        modifiers_viewport_off(context)
        return {'FINISHED'}


# Display Modifiers Edit on
def modifiers_edit_on(context):
    selection = bpy.context.selected_objects

    if not(selection):
        for obj in bpy.data.objects:
            for mod in obj.modifiers:
                mod.show_in_editmode = True
    else:
        for obj in selection:
            for mod in obj.modifiers:
                mod.show_in_editmode = True


class DisplayModifiersEditOn(Operator):
    bl_idname = "view3d.display_modifiers_edit_on"
    bl_label = "On"
    bl_description = "Display modifiers during edit mode"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        modifiers_edit_on(context)
        return {'FINISHED'}


# Display Modifiers Edit off
def modifiers_edit_off(context):
    selection = bpy.context.selected_objects

    if not(selection):
        for obj in bpy.data.objects:
            for mod in obj.modifiers:
                mod.show_in_editmode = False
    else:
        for obj in selection:
            for mod in obj.modifiers:
                mod.show_in_editmode = False


class DisplayModifiersEditOff(Operator):
    bl_idname = "view3d.display_modifiers_edit_off"
    bl_label = "Off"
    bl_description = "Hide modifiers during edit mode"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        modifiers_edit_off(context)
        return {'FINISHED'}


# Display Modifiers Cage on
def modifiers_cage_on(context):
    selection = bpy.context.selected_objects

    if not(selection):
        for obj in bpy.data.objects:
            for mod in obj.modifiers:
                mod.show_on_cage = True
    else:
        for obj in selection:
            for mod in obj.modifiers:
                mod.show_on_cage = True


class DisplayModifiersCageOn(Operator):
    bl_idname = "view3d.display_modifiers_cage_on"
    bl_label = "On"
    bl_description = "Display modifiers editing cage during edit mode"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        modifiers_cage_on(context)
        return {'FINISHED'}


# Display Modifiers Cage off
def modifiers_cage_off(context):
    selection = bpy.context.selected_objects

    if not(selection):
        for obj in bpy.data.objects:
            for mod in obj.modifiers:
                mod.show_on_cage = False
    else:
        for obj in selection:
            for mod in obj.modifiers:
                mod.show_on_cage = False


class DisplayModifiersCageOff(Operator):
    bl_idname = "view3d.display_modifiers_cage_off"
    bl_label = "Off"
    bl_description = "Hide modifiers editing cage during edit mode"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        modifiers_cage_off(context)
        return {'FINISHED'}


# Display Modifiers Expand
def modifiers_expand(context):
    selection = bpy.context.selected_objects

    if not(selection):
        for obj in bpy.data.objects:
            for mod in obj.modifiers:
                mod.show_expanded = True
    else:
        for obj in selection:
            for mod in obj.modifiers:
                mod.show_expanded = True


class DisplayModifiersExpand(Operator):
    bl_idname = "view3d.display_modifiers_expand"
    bl_label = "Expand"
    bl_description = "Expand all modifiers on modifier stack"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        modifiers_expand(context)
        return {'FINISHED'}


# Display Modifiers Collapse
def modifiers_collapse(context):
    selection = bpy.context.selected_objects

    if not(selection):
        for obj in bpy.data.objects:
            for mod in obj.modifiers:
                mod.show_expanded = False
    else:
        for obj in selection:
            for mod in obj.modifiers:
                mod.show_expanded = False


class DisplayModifiersCollapse(Operator):
    bl_idname = "view3d.display_modifiers_collapse"
    bl_label = "Collapse"
    bl_description = "Collapse all modifiers on modifier stack"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        modifiers_collapse(context)
        return {'FINISHED'}


# Apply modifiers
def modifiers_apply(context):
    selection = bpy.context.selected_objects

    if not selection:
        bpy.ops.object.select_all(action='TOGGLE')
        bpy.ops.object.convert(target='MESH', keep_original=False)
        bpy.ops.object.select_all(action='TOGGLE')
    else:
        for mesh in selection:
            if mesh.type == "MESH":
                bpy.ops.object.convert(target='MESH', keep_original=False)


class DisplayModifiersApply(Operator):
    '''Apply modifiers'''
    bl_idname = "view3d.display_modifiers_apply"
    bl_label = "Apply All"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        modifiers_apply(context)
        return {'FINISHED'}


# Delete modifiers
def modifiers_delete(context):
    selection = bpy.context.selected_objects

    if not(selection):
        for obj in bpy.data.objects:
            for mod in obj.modifiers:
                bpy.context.scene.objects.active = obj
                bpy.ops.object.modifier_remove(modifier=mod.name)
    else:
        for obj in selection:
            for mod in obj.modifiers:
                bpy.context.scene.objects.active = obj
                bpy.ops.object.modifier_remove(modifier=mod.name)


class DisplayModifiersDelete(Operator):
    bl_idname = "view3d.display_modifiers_delete"
    bl_label = "Delete All"
    bl_description = "Delete modifiers"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        modifiers_delete(context)
        return {'FINISHED'}


# Put dummy modifier for boost subsurf
def modifiers_set_dummy(context):
    selection = bpy.context.selected_objects

    if not(selection):
        for obj in bpy.data.objects:
            bpy.context.scene.objects.active = obj
            bpy.ops.object.modifier_add(type='SIMPLE_DEFORM')
            value = 0
            for mod in obj.modifiers:
                if mod != 0:
                    if mod.type == 'SIMPLE_DEFORM':
                        value = value + 1
                        mod.factor = 0
                    if value > 1:
                        bpy.ops.object.modifier_remove(modifier="SimpleDeform")
    else:
        for obj in selection:
            bpy.context.scene.objects.active = obj
            bpy.ops.object.modifier_add(type='SIMPLE_DEFORM')
            value = 0
            for mod in obj.modifiers:
                if mod.type == 'SIMPLE_DEFORM':
                    value = value + 1
                    mod.factor = 0
                if value > 1:
                    bpy.ops.object.modifier_remove(modifier="SimpleDeform")


# Delete dummy modifier
def modifiers_delete_dummy(context):
    selection = bpy.context.selected_objects

    if not(selection):
        for obj in bpy.data.objects:
            bpy.context.scene.objects.active = obj
            for mod in obj.modifiers:
                if mod.type == 'SIMPLE_DEFORM':
                    bpy.ops.object.modifier_remove(modifier="SimpleDeform")
                    bpy.ops.object.modifier_remove(modifier="SimpleDeform.001")
    else:
        for obj in selection:
            bpy.context.scene.objects.active = obj
            for mod in obj.modifiers:
                if mod.type == 'SIMPLE_DEFORM':
                    bpy.ops.object.modifier_remove(modifier="SimpleDeform")
                    bpy.ops.object.modifier_remove(modifier="SimpleDeform.001")


class DisplayAddDummy(Operator):
    bl_idname = "view3d.display_modifiers_set_dummy"
    bl_label = "Put Dummy"
    bl_description = ("Add a dummy simple deform modifier to boost "
                     "subsurf modifier viewport performance")

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        modifiers_set_dummy(context)
        return {'FINISHED'}


class DisplayDeleteDummy(Operator):
    bl_idname = "view3d.display_modifiers_delete_dummy"
    bl_label = "Delete Dummy"
    bl_description = ("Delete a dummy simple deform modifier to boost "
                      "subsurf modifier viewport performance")

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        modifiers_delete_dummy(context)
        return {'FINISHED'}


# Display subsurf level 0
def modifiers_subsurf_level_0(context):
    selection = bpy.context.selected_objects

    if not selection:
        for obj in bpy.data.objects:
            bpy.context.scene.objects.active = obj
            bpy.ops.object.modifier_add(type='SUBSURF')
            value = 0
            for mod in obj.modifiers:
                if mod.type == 'SUBSURF':
                    value = value + 1
                    mod.levels = 0
                if value > 1:
                    bpy.ops.object.modifier_remove(modifier="Subsurf")
    else:
        for obj in selection:
            bpy.ops.object.subdivision_set(level=0, relative=False)
            for mod in obj.modifiers:
                if mod.type == 'SUBSURF':
                    mod.levels = 0


# Display subsurf level 1
def modifiers_subsurf_level_1(context):
    selection = bpy.context.selected_objects

    if not(selection):
        for obj in bpy.data.objects:
            bpy.context.scene.objects.active = obj
            bpy.ops.object.modifier_add(type='SUBSURF')
            value = 0
            for mod in obj.modifiers:
                if mod.type == 'SUBSURF':
                    value = value + 1
                    mod.levels = 1
                if value > 1:
                    bpy.ops.object.modifier_remove(modifier="Subsurf")
    else:
        for obj in selection:
            bpy.ops.object.subdivision_set(level=1, relative=False)
            for mod in obj.modifiers:
                if mod.type == 'SUBSURF':
                    mod.levels = 1


# Display subsurf level 2
def modifiers_subsurf_level_2(context):
    selection = bpy.context.selected_objects

    if not(selection):
        for obj in bpy.data.objects:
            bpy.context.scene.objects.active = obj
            bpy.ops.object.modifier_add(type='SUBSURF')
            value = 0
            for mod in obj.modifiers:
                if mod.type == 'SUBSURF':
                    value = value + 1
                    mod.levels = 2
                if value > 1:
                    bpy.ops.object.modifier_remove(modifier="Subsurf")
    else:
        for obj in selection:
            bpy.ops.object.subdivision_set(level=2, relative=False)
            for mod in obj.modifiers:
                if mod.type == 'SUBSURF':
                    mod.levels = 2


# Display subsurf level 3
def modifiers_subsurf_level_3(context):
    selection = bpy.context.selected_objects

    if not(selection):
        for obj in bpy.data.objects:
            bpy.context.scene.objects.active = obj
            bpy.ops.object.modifier_add(type='SUBSURF')
            value = 0
            for mod in obj.modifiers:
                if mod.type == 'SUBSURF':
                    value = value + 1
                    mod.levels = 3
                if value > 1:
                    bpy.ops.object.modifier_remove(modifier="Subsurf")
    else:
        for obj in selection:
            bpy.ops.object.subdivision_set(level=3, relative=False)
            for mod in obj.modifiers:
                if mod.type == 'SUBSURF':
                    mod.levels = 3


# Display subsurf level 4
def modifiers_subsurf_level_4(context):
    selection = bpy.context.selected_objects

    if not(selection):
        for obj in bpy.data.objects:
            bpy.context.scene.objects.active = obj
            bpy.ops.object.modifier_add(type='SUBSURF')
            value = 0
            for mod in obj.modifiers:
                if mod.type == 'SUBSURF':
                    value = value + 1
                    mod.levels = 4
                if value > 1:
                    bpy.ops.object.modifier_remove(modifier="Subsurf")
    else:
        for obj in selection:
            bpy.ops.object.subdivision_set(level=4, relative=False)
            for mod in obj.modifiers:
                if mod.type == 'SUBSURF':
                    mod.levels = 4


# Display subsurf level 5
def modifiers_subsurf_level_5(context):
    selection = bpy.context.selected_objects

    if not(selection):
        for obj in bpy.data.objects:
            bpy.context.scene.objects.active = obj
            bpy.ops.object.modifier_add(type='SUBSURF')
            value = 0
            for mod in obj.modifiers:
                if mod.type == 'SUBSURF':
                    value = value + 1
                    mod.levels = 5
                if value > 1:
                    bpy.ops.object.modifier_remove(modifier="Subsurf")
    else:
        for obj in selection:
            bpy.ops.object.subdivision_set(level=5, relative=False)
            for mod in obj.modifiers:
                if mod.type == 'SUBSURF':
                    mod.levels = 5


# Display subsurf level 6
def modifiers_subsurf_level_6(context):
    selection = bpy.context.selected_objects

    if not(selection):
        for obj in bpy.data.objects:
            bpy.context.scene.objects.active = obj
            bpy.ops.object.modifier_add(type='SUBSURF')
            value = 0
            for mod in obj.modifiers:
                if mod.type == 'SUBSURF':
                    value = value + 1
                    mod.levels = 6
                if value > 1:
                    bpy.ops.object.modifier_remove(modifier="Subsurf")
    else:
        for obj in selection:
            bpy.ops.object.subdivision_set(level=6, relative=False)
            for mod in obj.modifiers:
                if mod.type == 'SUBSURF':
                    mod.levels = 6


# main class of Display subsurf level 0
class ModifiersSubsurfLevel_0(Operator):
    bl_idname = "view3d.modifiers_subsurf_level_0"
    bl_label = "0"
    bl_description = "Change subsurf modifier level"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        modifiers_subsurf_level_0(context)
        return {'FINISHED'}


# main class of Display subsurf level 1
class ModifiersSubsurfLevel_1(Operator):
    bl_idname = "view3d.modifiers_subsurf_level_1"
    bl_label = "1"
    bl_description = "Change subsurf modifier level"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        modifiers_subsurf_level_1(context)
        return {'FINISHED'}


# main class of Display subsurf level 2
class ModifiersSubsurfLevel_2(Operator):
    bl_idname = "view3d.modifiers_subsurf_level_2"
    bl_label = "2"
    bl_description = "Change subsurf modifier level"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        modifiers_subsurf_level_2(context)
        return {'FINISHED'}


# main class of Display subsurf level 3
class ModifiersSubsurfLevel_3(Operator):
    bl_idname = "view3d.modifiers_subsurf_level_3"
    bl_label = "3"
    bl_description = "Change subsurf modifier level"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        modifiers_subsurf_level_3(context)
        return {'FINISHED'}


# main class of Display subsurf level 4
class ModifiersSubsurfLevel_4(Operator):
    bl_idname = "view3d.modifiers_subsurf_level_4"
    bl_label = "4"
    bl_description = "Change subsurf modifier level"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        modifiers_subsurf_level_4(context)
        return {'FINISHED'}


# main class of Display subsurf level 5
class ModifiersSubsurfLevel_5(Operator):
    bl_idname = "view3d.modifiers_subsurf_level_5"
    bl_label = "5"
    bl_description = "Change subsurf modifier level"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        modifiers_subsurf_level_5(context)
        return {'FINISHED'}


# main class of Display subsurf level 6
class ModifiersSubsurfLevel_6(Operator):
    bl_idname = "view3d.modifiers_subsurf_level_6"
    bl_label = "6"
    bl_description = "Change subsurf modifier level"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        modifiers_subsurf_level_6(context)
        return {'FINISHED'}


# main class for Fast Navigate
class VIEW3D_PT_FastNavigate(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Display Tools"
    bl_label = "Fast Navigate"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout

        # Tools
        scene = context.scene
        row = layout.row(align=True)
        row.alignment = 'LEFT'
        row.operator("view3d.fast_navigate_operator")
        row.operator("view3d.fast_navigate_stop")
        layout.label("Settings :")
        row = layout.row()
        box = row.box()
        box.prop(scene, "OriginalMode")
        box.prop(scene, "FastMode")
        box.prop(scene, "EditActive", "Edit mode")
        box.prop(scene, "Delay")
        box.prop(scene, "DelayTimeGlobal", "Delay time")
        box.alignment = 'LEFT'
        box.prop(scene, "ShowParticles")
        box.prop(scene, "ParticlesPercentageDisplay")


# main class for Display Mode
class VIEW3D_PT_DisplayMode(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Display Tools"
    bl_label = "Display Mode"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout

        # Tools
        col = layout.column()
        col.alignment = 'EXPAND'
        row = col.row()
        row.operator("view3d.display_textured", icon='TEXTURE_SHADED')
        row.operator("view3d.display_solid", icon='SOLID')
        col = layout.column()
        col.alignment = 'EXPAND'
        row = col.row()
        row.operator("view3d.display_wire", icon='WIRE')
        row.operator("view3d.display_bounds", icon='BBOX')


# main class for Shading Setup
class VIEW3D_PT_ShadingSetup(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Display Tools"
    bl_label = "Shading Setup"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout

        # Tools
        col = layout.column(align=True)
        row = col.row()
        row.operator("view3d.display_shade_smooth")
        row.operator("view3d.display_shade_flat")
        row = col.row()
        row.operator("view3d.display_shadeless_on", "Shadeless On",
                      icon='SOLID')
        row.operator("view3d.display_shadeless_off",
                     "Shadeless Off", icon='SOLID')
        row = col.row()
        row.operator("view3d.display_wire_on", "Wire On", icon='WIRE')
        row.operator("view3d.display_wire_off", "Wire Off", icon='WIRE')
        row = col.row()
        row.operator("view3d.display_bounds_on", "Bounds On", icon='BBOX')
        row.operator("view3d.display_bounds_off", "Bounds Off", icon='BBOX')
        row = col.row()
        row.operator("view3d.display_double_sided_on",
                     "DSided On", icon='MESH_DATA')
        row.operator("view3d.display_double_sided_off",
                     "DSided Off", icon='MESH_DATA')
        row = col.row()
        row.operator("view3d.display_x_ray_on",
                     "XRay On", icon='GHOST_ENABLED')
        row.operator("view3d.display_x_ray_off",
                     "XRay Off", icon='GHOST_ENABLED')
        row = col.row()
        row.separator()

        row = col.row()
        scene = context.scene
        row.prop(scene, "BoundingMode")


# main class for Scene Visualization
class VIEW3D_PT_SceneVisualization(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Display Tools"
    bl_label = "Scene Visualization"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout

        # Tools
        scene = context.scene
        render = scene.render
        space = context.space_data
        layout.prop(space, "show_manipulator")
        layout.prop(space, "show_outline_selected")
        layout.prop(space, "show_only_render")
        layout.prop(space, "show_textured_solid")
        layout.prop(space, "show_backface_culling")
        layout.prop(space, "show_all_objects_origin")
        layout.prop(render, "use_simplify", "Simplify")
        if scene.render.use_simplify is True:
            layout.label("Settings :")
            row = layout.row()
            box = row.box()
            box.prop(render, "simplify_subdivision", "Subdivision")
            box.prop(render, "simplify_shadow_samples", "Shadow Samples")
            box.prop(render, "simplify_child_particles", "Child Particles")
            box.prop(render, "simplify_ao_sss", "AO and SSS")
            layout.operator("view3d.display_simplify")


# main class for Modifier Tools
class VIEW3D_PT_ModifierTools(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Display Tools"
    bl_label = "Modifier Tools"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout

        # Tools
        layout.label("Modifiers", icon='MODIFIER')
        col = layout.column(align=True)
        col.alignment = 'EXPAND'
        row = col.row()
        row.operator("view3d.display_modifiers_render_on",
                      icon='RENDER_STILL')
        row.operator("view3d.display_modifiers_render_off")
        row.operator("view3d.display_modifiers_viewport_on",
                     icon='RESTRICT_VIEW_OFF')
        row.operator("view3d.display_modifiers_viewport_off")
        col = layout.column(align=True)
        col.alignment = 'EXPAND'
        row = col.row()
        row.operator("view3d.display_modifiers_edit_on", icon='EDITMODE_HLT')
        row.operator("view3d.display_modifiers_edit_off")
        row.operator("view3d.display_modifiers_cage_on",
                     icon='EDITMODE_HLT')
        row.operator("view3d.display_modifiers_cage_off")
        row = layout.row(align=True)
        row.operator("view3d.display_modifiers_expand", icon='TRIA_DOWN')
        row.operator("view3d.display_modifiers_collapse", icon='TRIA_RIGHT')
        row = layout.row(align=True)
        row.operator("view3d.display_modifiers_apply", icon='MODIFIER')
        row.operator("view3d.display_modifiers_delete", icon='X')
        row = layout.row(align=True)
        row.operator("view3d.display_modifiers_set_dummy",
                     icon='OUTLINER_OB_ARMATURE')
        row.operator("view3d.display_modifiers_delete_dummy",
                     icon='X')
        layout.label("Subdivision Level", icon='MOD_SUBSURF')
        row = layout.row(align=True)
        row.operator("view3d.modifiers_subsurf_level_0")
        row.operator("view3d.modifiers_subsurf_level_1")
        row.operator("view3d.modifiers_subsurf_level_2")
        row.operator("view3d.modifiers_subsurf_level_3")
        row.operator("view3d.modifiers_subsurf_level_4")
        row.operator("view3d.modifiers_subsurf_level_5")
        row.operator("view3d.modifiers_subsurf_level_6")


# register the classes and props
def register():

    # Init delay variables
    bpy.types.Scene.Delay = BoolProperty(
            default=False,
            description="Activate delay return to normal viewport mode"
            )
    bpy.types.Scene.DelayTime = IntProperty(
            default=30,
            min=1,
            max=500,
            soft_min=10,
            soft_max=250,
            description="Delay time to return to normal viewport"
                        "mode after move your mouse cursor"
            )
    bpy.types.Scene.DelayTimeGlobal = IntProperty(
            default=30,
            min=1,
            max=500,
            soft_min=10,
            soft_max=250,
            description="Delay time to return to normal viewport"
                        "mode after move your mouse cursor"
            )
    # Init variable for fast navigate
    bpy.types.Scene.EditActive = BoolProperty(
            default=True,
            description="Activate for fast navigate in edit mode too"
            )

    # Init properties for scene
    bpy.types.Scene.FastNavigateStop = BoolProperty(
            name="Fast Navigate Stop",
            description="Stop fast navigate mode",
            default=False
            )
    bpy.types.Scene.OriginalMode = EnumProperty(
            items=[('TEXTURED', 'Texture', 'Texture display mode'),
                ('SOLID', 'Solid', 'Solid display mode')],
            name="Normal",
            default='SOLID'
            )
    bpy.types.Scene.BoundingMode = EnumProperty(
            items=[('BOX', 'Box', 'Box shape'),
                ('SPHERE', 'Sphere', 'Sphere shape'),
                ('CYLINDER', 'Cylinder', 'Cylinder shape'),
                ('CONE', 'Cone', 'Cone shape')],
            name="BB Mode"
            )
    bpy.types.Scene.FastMode = EnumProperty(
            items=[('WIREFRAME', 'Wireframe', 'Wireframe display'),
                ('BOUNDBOX', 'Bounding Box', 'Bounding Box display')],
            name="Fast"
            )
    bpy.types.Scene.ShowParticles = BoolProperty(
            name="Show Particles",
            description="Show or hide particles on fast navigate mode",
            default=True
            )
    bpy.types.Scene.ParticlesPercentageDisplay = IntProperty(
            name="Display",
            description="Display only a percentage of particles",
            default=25,
            min=0,
            max=100,
            soft_min=0,
            soft_max=100,
            subtype='FACTOR'
            )
    bpy.types.Scene.InitialParticles = IntProperty(
            name="Count for initial particle setting before enter fast navigate",
            description="Display a percentage value of particles",
            default=100,
            min=0,
            max=100,
            soft_min=0,
            soft_max=100
            )

    bpy.types.Scene.Symplify = IntProperty(
            name="Integer",
            description="Enter an integer"
            )

    bpy.utils.register_class(FastNavigate)
    bpy.utils.register_class(DisplayTextured)
    bpy.utils.register_class(DisplaySolid)
    bpy.utils.register_class(DisplayWire)
    bpy.utils.register_class(DisplayBounds)
    bpy.utils.register_class(DisplayWireframeOn)
    bpy.utils.register_class(DisplayWireframeOff)
    bpy.utils.register_class(DisplayBoundsOn)
    bpy.utils.register_class(DisplayBoundsOff)
    bpy.utils.register_class(DisplayShadeSmooth)
    bpy.utils.register_class(DisplayShadeFlat)
    bpy.utils.register_class(DisplayShadelessOn)
    bpy.utils.register_class(DisplayShadelessOff)
    bpy.utils.register_class(DisplayDoubleSidedOn)
    bpy.utils.register_class(DisplayDoubleSidedOff)
    bpy.utils.register_class(DisplayXRayOn)
    bpy.utils.register_class(DisplayXRayOff)
    bpy.utils.register_class(DisplayModifiersRenderOn)
    bpy.utils.register_class(DisplayModifiersRenderOff)
    bpy.utils.register_class(DisplayModifiersViewportOn)
    bpy.utils.register_class(DisplayModifiersViewportOff)
    bpy.utils.register_class(DisplayModifiersEditOn)
    bpy.utils.register_class(DisplayModifiersEditOff)
    bpy.utils.register_class(DisplayModifiersCageOn)
    bpy.utils.register_class(DisplayModifiersCageOff)
    bpy.utils.register_class(DisplayModifiersExpand)
    bpy.utils.register_class(DisplayModifiersCollapse)
    bpy.utils.register_class(DisplayModifiersApply)
    bpy.utils.register_class(DisplayModifiersDelete)
    bpy.utils.register_class(DisplayAddDummy)
    bpy.utils.register_class(DisplayDeleteDummy)
    bpy.utils.register_class(DisplaySimplify)
    bpy.utils.register_class(ModifiersSubsurfLevel_0)
    bpy.utils.register_class(ModifiersSubsurfLevel_1)
    bpy.utils.register_class(ModifiersSubsurfLevel_2)
    bpy.utils.register_class(ModifiersSubsurfLevel_3)
    bpy.utils.register_class(ModifiersSubsurfLevel_4)
    bpy.utils.register_class(ModifiersSubsurfLevel_5)
    bpy.utils.register_class(ModifiersSubsurfLevel_6)
    bpy.utils.register_module(__name__)
    pass


def unregister():
    del bpy.types.Scene.Delay
    del bpy.types.Scene.DelayTime
    del bpy.types.Scene.DelayTimeGlobal
    del bpy.types.Scene.EditActive

    del bpy.types.Scene.FastNavigateStop
    del bpy.types.Scene.OriginalMode
    del bpy.types.Scene.BoundingMode
    del bpy.types.Scene.FastMode
    del bpy.types.Scene.ShowParticles
    del bpy.types.Scene.ParticlesPercentageDisplay
    del bpy.types.Scene.InitialParticles
    del bpy.types.Scene.Symplify

    bpy.utils.unregister_class(FastNavigate)
    bpy.utils.unregister_class(DisplayTextured)
    bpy.utils.unregister_class(DisplaySolid)
    bpy.utils.unregister_class(DisplayWire)
    bpy.utils.unregister_class(DisplayBounds)
    bpy.utils.unregister_class(DisplayShadeSmooth)
    bpy.utils.unregister_class(DisplayShadeFlat)
    bpy.utils.unregister_class(DisplayShadelessOn)
    bpy.utils.unregister_class(DisplayShadelessOff)
    bpy.utils.unregister_class(DisplayWireframeOn)
    bpy.utils.unregister_class(DisplayWireframeOff)
    bpy.utils.unregister_class(DisplayBoundsOn)
    bpy.utils.unregister_class(DisplayBoundsOff)
    bpy.utils.unregister_class(DisplayDoubleSidedOn)
    bpy.utils.unregister_class(DisplayDoubleSidedOff)
    bpy.utils.unregister_class(DisplayXRayOn)
    bpy.utils.unregister_class(DisplayXRayOff)
    bpy.utils.unregister_class(DisplayModifiersRenderOn)
    bpy.utils.unregister_class(DisplayModifiersRenderOff)
    bpy.utils.unregister_class(DisplayModifiersViewportOn)
    bpy.utils.unregister_class(DisplayModifiersViewportOff)
    bpy.utils.unregister_class(DisplayModifiersEditOn)
    bpy.utils.unregister_class(DisplayModifiersEditOff)
    bpy.utils.unregister_class(DisplayModifiersCageOn)
    bpy.utils.unregister_class(DisplayModifiersCageOff)
    bpy.utils.unregister_class(DisplayModifiersExpand)
    bpy.utils.unregister_class(DisplayModifiersCollapse)
    bpy.utils.unregister_class(DisplayModifiersApply)
    bpy.utils.unregister_class(DisplayModifiersDelete)
    bpy.utils.unregister_class(DisplayAddDummy)
    bpy.utils.unregister_class(DisplayDeleteDummy)
    bpy.utils.unregister_class(DisplaySimplify)
    bpy.utils.unregister_class(ModifiersSubsurfLevel_0)
    bpy.utils.unregister_class(ModifiersSubsurfLevel_1)
    bpy.utils.unregister_class(ModifiersSubsurfLevel_2)
    bpy.utils.unregister_class(ModifiersSubsurfLevel_3)
    bpy.utils.unregister_class(ModifiersSubsurfLevel_4)
    bpy.utils.unregister_class(ModifiersSubsurfLevel_5)
    bpy.utils.unregister_class(ModifiersSubsurfLevel_6)
    bpy.utils.unregister_module(__name__)
    pass

if __name__ == "__main__":
    register()

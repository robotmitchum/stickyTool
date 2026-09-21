# coding:utf-8
"""
    :module: sticky.py
    :description: Create "Sticky Deformer", cluster or softmod pinned to a mesh
    :author: Michel 'Mitch' Pecqueur
    :date: 2026.06

import aresTools.stickyTool.sticky as sticky
sticky.create_sticky_on_cp(typ='softmod')
"""

import re
from colorsys import hsv_to_rgb
from random import random

import maya.api.OpenMaya as om
import maya.cmds as mc


# import aresCore.shapes.defs as shapes


def create_sticky_on_cp(typ: str = 'softmod', radius: float = 1.0) -> tuple:
    """
    Create sticky on selected components
    :param typ:
    :param radius:
    :return:
    """
    cpsel = get_cp_sel()
    if cpsel is None:
        return None
    obj, pos = cpsel
    with DisableCycleCheck():  # Avoid potential pesky messages while building
        result = create_sticky(obj=obj, pos=pos, typ=typ, radius=radius)
    mc.selectMode(object=True)
    mc.select(result[1], r=True)
    return result


def delete_sticky(objlist: list) -> list | None:
    """
    Delete sticky related to given objects
    :param objlist:
    :return: Deleted sticky deformer(s)
    """
    sticky = get_sticky(objlist)
    if not sticky:
        return
    sticky = sorted(list(set(sticky)))
    deps = get_sticky_deps(sticky) or []
    if deps:
        for dep in deps:
            # Delete dependencies and sticky group if empty
            par = mc.listRelatives(dep[0], p=True, pa=True) or []
            is_sticky_grp = [at for at in mc.listAttr(par, ud=True) or [] if at == 'animStickyGroup']
            mc.delete(dep)
            if par and is_sticky_grp and not mc.listRelatives(par, c=True):
                mc.delete(par[0])

        return sticky


def get_sticky(objlist: list = ()) -> list:
    """
    Retrieve sticky deformers from given objects
    :param objlist:
    :return:
    """
    result = []
    for obj in objlist:
        attrs = [at for at in mc.listAttr(obj, ud=True) or [] if at.startswith('animSticky')]
        if not attrs:
            continue
        if 'animStickyDeform' in attrs:
            if obj not in set(result):
                result.append(obj)
            continue
        else:
            deform = [d for d in mc.listConnections(f'{obj}.message', s=0, d=1, t='geometryFilter') if
                      mc.objExists(f'{d}.animStickyDeform')]
            if deform:
                if deform[0] not in set(result):
                    result.append(deform[0])
    return result


def get_sticky_deps(objlist: list = ()) -> list[list]:
    """
    Retrieve dependencies from given sticky deformer(s)
    :param objlist: list of sticky deformer(s)
    :return:
    """
    result = []
    for obj in objlist:
        deps = mc.listConnections(f'{obj}.animStickyDeform', s=1, d=0) or []
        deps.append(obj)
        result.append(deps)
    return result


# Auxiliary defs

def get_cp_sel() -> tuple | None:
    """
    Get component selection
    :return: object, position
    """
    sel = mc.ls(sl=True)
    if not sel:
        warning_msg('Nothing selected')
        return

    cp_sel_check = False
    if not sel[0].endswith('[*]'):
        # Check if components are selected
        cp_kwds = ('.vtx[', '.e[', '.f[')
        for kw in cp_kwds:
            if kw in sel[0]:
                cp_sel_check = True

    if not cp_sel_check:
        warning_msg('Select mesh components (vertices, edges or faces)')
        return

    obj = sel[0].split('.')[0]

    if mc.objectType(obj) == 'mesh':
        obj = mc.listRelatives(obj, p=True, pa=True)[0]

    bb = mc.xform(sel, q=True, a=True, ws=True, bb=True)
    pos = [(bb[i] + bb[i + 3]) / 2 for i in range(3)]

    return obj, pos


def create_sticky(obj: str, pos: list, typ: str = 'softmod', radius: float = 1.0) -> tuple:
    """
    Create 'Sticky Deformer', cluster or softmod pinned to a mesh

    :param obj: Create sticky on given object
    :param pos: Position
    :param typ: softmod or cluster
    :param radius: Radius in cm

    :return: sticky_base, sticky_ctrl, sticky_deformer
    """
    ns = get_ns(obj)

    sticky_grp = f'{ns}:animsticky_grp'
    if not mc.objExists(sticky_grp):
        sticky_grp = mc.createNode('transform', n=sticky_grp)
        mc.addAttr(sticky_grp, ln='animStickyGroup', h=True)

    sticky_set = f'{ns}:animsticky_anim_set'
    if not mc.objExists(sticky_set):
        sticky_set = mc.sets(em=1, n=sticky_set)
        mc.addAttr(sticky_grp, ln='animStickySet', h=True)

    # defshp = create_deform_shape(objs=as_list(obj), suffix='Deformed', keepns=True, fromsel=False)[0]

    basename = f'{shorten_with_ns(obj)}_animsticky'

    sticky_idx = get_next_obj_idx(basename + '_base_')
    sticky_base = f'{basename}_base_{sticky_idx:02d}'
    sticky_ctrl = f'{basename}_ctrl_{sticky_idx:02d}'

    # Create main control
    hue = random()
    ctrl_rgb = hsv_to_rgb(hue, .5, 1)
    ctrl_rgb_vp = [v ** 2.2 for v in ctrl_rgb]
    sticky_ctrl_shp = {'cluster': 'flatLocator', 'softmod': 'sparkle'}[typ]
    # sticky_ctrl = shapes.add(sticky_ctrl, shape=sticky_ctrl_shp, axis='z', color=ctrl_rgb_vp)[0]
    sticky_ctrl = add_shape(sticky_ctrl, shape=sticky_ctrl_shp, color=ctrl_rgb_vp)
    mc.setAttr(sticky_ctrl + '.useOutlinerColor', True)
    mc.setAttr(sticky_ctrl + '.outlinerColor', *ctrl_rgb)
    mc.setAttr(sticky_ctrl + '.v', k=False, cb=True)

    # Create deformers
    match typ:
        # cluster : Simpler, painting required
        case 'cluster':
            deform_name = f'{basename}_cluster_{sticky_idx:02d}'
            sticky_deform = mc.cluster(obj, wn=(sticky_ctrl, sticky_ctrl), n=deform_name)[0]
            mc.select(obj, r=True)
            mc.percent(sticky_deform, v=0.0)
            # mc.polyEvaluate(obj, v=True)

        # softmod : Nice sliding effect, painting possible but not required
        case _:
            deform_name = f'{basename}_softmod_{sticky_idx:02d}'
            sticky_deform = mc.softMod(obj, wn=(sticky_ctrl, sticky_ctrl), n=deform_name)[0]
            mc.addAttr(sticky_ctrl, ln='radius', min=0, dv=radius, k=True)
            mc.connectAttr(sticky_ctrl + '.radius', sticky_deform + '.fr')

    connect_geo_to_deform_gm(obj=obj, deform=sticky_deform)

    # Add attribute identifying sticky deformer
    mc.addAttr(sticky_deform, ln='animStickyDeform', at='message',
               multi=True, indexMatters=False, disconnectBehaviour=0)

    # UV Pin
    # Create UV pin AFTER deformer, so we can better determine where to plug it
    # uvp_suffix is chosen, so it's different from anything used in the rigs
    uv_pin = sticky_uvpin(obj, name=sticky_base, uvp_suffix='_animsticky_uvp', pos=pos, index=-1)
    mc.parent(uv_pin[0], sticky_grp)

    # Use UV pin transform as sticky base control
    base_rgb = hsv_to_rgb(hue, .2, 1)
    base_rgb_vp = [v ** 2.2 for v in base_rgb]
    # shapes.add(sticky_base, shape='circle', axis='z', color=base_rgb_vp)
    add_shape(sticky_base, shape='circle', color=base_rgb_vp)
    mc.setAttr(sticky_base + '.useOutlinerColor', True)
    mc.setAttr(sticky_base + '.outlinerColor', *base_rgb)
    mc.setAttr(sticky_base + '.v', k=False, cb=True)
    mc.parent(sticky_ctrl, sticky_base, r=True)

    if typ == 'softmod':
        dm = mc.createNode('decomposeMatrix', n=f'{basename}_dm_{sticky_idx:02d}')
        mc.connectAttr(sticky_base + '.wm', dm + '.imat')
        mc.connectAttr(dm + '.ot', sticky_deform + '.fcr')

        cm = mc.createNode('composeMatrix', n=f'{basename}_shp_cm')
        mc.setAttr(cm + '.ihi', 0)

        for item in [sticky_base, sticky_ctrl]:
            crv_shporig = mc.createNode('nurbsCurve', n=item + 'ShapeOrig', p=item)
            tg = mc.createNode('transformGeometry', n=item + 'Shape_tg')
            for o in [crv_shporig, tg]:
                mc.setAttr(o + '.ihi', 0)
            mc.connectAttr(item + '.l', crv_shporig + '.cr')
            mc.getAttr(crv_shporig + '.d')
            mc.disconnectAttr(item + '.l', crv_shporig + '.cr')
            mc.setAttr(crv_shporig + '.io', 1)
            mc.connectAttr(crv_shporig + '.l', tg + '.ig')
            mc.connectAttr(tg + '.og', item + '.cr')
            mc.connectAttr(cm + '.omat', tg + '.txf')

        for axis in 'xyz':
            mc.connectAttr(sticky_ctrl + '.radius', f'{cm}.is{axis}')

    # Add attributes to retrieve dependencies even if they are renamed
    for i, (item, attr) in enumerate(zip([sticky_base, sticky_ctrl], ['animStickyBase', 'animStickyCtrl'])):
        mc.addAttr(item, ln=attr, at='bool', h=True)
        mc.connectAttr(f'{item}.message', f'{sticky_deform}.animStickyDeform[{i}]')

    mc.connectAttr(sticky_base + '.wim', sticky_deform + '.bindPreMatrix')

    mc.sets(sticky_ctrl, sticky_base, add=sticky_set)

    shps = mc.listRelatives([sticky_base, sticky_ctrl, sticky_deform], s=True, pa=True) or []
    if shps:
        mc.reorder(shps, b=True)

    mc.select(sticky_ctrl, r=True)

    return sticky_base, sticky_ctrl, sticky_deform


def sticky_uvpin(obj: str, name: str | None = 'uvpin', uvp_suffix: str | None = '_uvp',
                 pos: list | None = None, uv: list | None = None,
                 index: int = 0, sticky_deform_attr: str = 'animStickyDeform') -> tuple:
    """
    Create UV pin on given surface
    Specific version for sticky deformers

    :param obj: Input object
    :param name: Name of created UV pin transform, not created if no name supplied
    :param uvp_suffix:
    :param list or None pos: Input position, if None use UV parameters
    :param list or None uv: If None use [.5,.5]
    :param index: Index of pin on node, if -1 use the first free index
    :param sticky_deform_attr: Name of the attribute identifying a sticky deformer

    :return: UV pin transform, UV pin node
    """
    shp = mc.listRelatives(obj, s=True, pa=True, ni=True)[0]
    shp_orig = get_shp_orig(obj)[0]

    srf_type = mc.objectType(shp)  # Get surface type
    if srf_type == 'mesh':
        mc.setAttr(shp + '.qsp', 0)  # Define fixed tesselation to avoid flipping with polygons

    # Create UV pin node
    uvpin = shorten_with_ns(obj) + (uvp_suffix, '_uvp')[uvp_suffix is None]

    # Reuse existing UV pin node if existent
    if not mc.objExists(uvpin):
        uvpin = mc.createNode('uvPin', n=uvpin)
        # Match follicle default orientation
        mc.setAttr('.normalAxis', 2)
        mc.setAttr('.tangentAxis', 3)

        # Node and attribute dictionary depending on surface type
        shp_out = {'mesh': '.worldMesh', 'nurbsSurface': '.ws'}[srf_type]
        shporig_out = {'mesh': '.o', 'nurbsSurface': '.l'}[srf_type]

        mc.connectAttr(f'{shp_orig}{shporig_out}', f'{uvpin}.originalGeometry')

        plug = None
        if sticky_deform_attr:
            # Find UV pin plug
            deform = mc.ls(scoped_history(obj), typ='geometryFilter')
            sticky_deform = [d for d in deform if mc.objExists(f'{d}.{sticky_deform_attr}')]

            if sticky_deform:
                plug = mc.listConnections(sticky_deform[0] + '.input', s=1, d=0, p=1)
            else:
                plug = mc.listConnections(shp + '.i', s=1, d=0, p=1)

            if plug:
                print(f'[uvPin] {plug[0]} -> {uvpin}')
                mc.connectAttr(plug[0], uvpin + '.deformedGeometry', f=True)

        if not plug:
            mc.connectAttr(f'{shp}{shp_out}', f'{uvpin}.deformedGeometry')

    # UV parameters
    uv = uv or [.5, .5]
    if pos:
        sl = om.MSelectionList()
        sl.add(obj)
        u, v = .5, .5
        if srf_type == 'nurbsSurface':
            mfn = om.MFnNurbsSurface(sl.getDagPath(0))
            _, u, v = mfn.closestPoint(om.MPoint(pos), om.MSpace.kWorld)
        if srf_type == 'mesh':
            mfn = om.MFnMesh(sl.getDagPath(0))
            cp, _ = mfn.getClosestPoint(om.MPoint(pos), om.MSpace.kWorld)
            u, v, _ = mfn.getUVAtPoint(cp, om.MSpace.kWorld)
        uv = u, v

    if index == -1:
        idx = 0
        # Use first available index
        cn = mc.listConnections(uvpin + '.outputMatrix', s=0, d=1, c=1) or []
        if cn:
            cn_idx = [get_idx(c) for c in cn[0::2] if c]
            idx = find_first_idx(cn_idx)
    else:
        idx = index

    mc.setAttr(f'{uvpin}.coord[{idx}]', *uv)

    # Create transform
    if name:
        uvp_tr = mc.createNode('transform', n=name)
        mc.setAttr(uvp_tr + '.it', False)
        mc.connectAttr(f'{uvpin}.outputMatrix[{idx}]', uvp_tr + '.offsetParentMatrix', f=True)
    else:
        uvp_tr = None

    print(f'[uvPin] {uvpin}.outputMatrix[{idx}] -> {uvp_tr}')

    # Refresh UV pin and match deformed state transformation
    mat = mc.getAttr(f'{uvpin}.outputMatrix[{idx}]')
    mc.dgdirty(uvpin)
    mc.getAttr(f'{uvpin}.outputMatrix[{idx}]')
    mc.xform(uvp_tr, a=1, ws=1, m=mat)

    return uvp_tr, uvpin


# Control shapes

def add_shape(obj, shape: str = 'circle', axis: str = 'z', color=(1, 1, 0)):
    """
    Add shape to transform
    (minimal version)

    :param obj: given transform
    :param shape: 'circle' (default), 'flatLocator' or 'sparkle'
    :param axis: Given shape axis
    :param color: rgb color

    :return:
    """
    sn = obj.split('|')[-1]

    if not mc.objExists(obj):
        obj = mc.createNode('transform', n=sn)

    match shape:
        case 'flatLocator':
            data = [1, 4, 0, False, 3, [0, 1, 2, 3, 4], 5, 5, [-1, 0, 0], [1, 0, 0], [0, 0, 0], [0, 0, 1], [0, 0, -1]]
        case 'sparkle':
            data = [3, 8, 2, False, 3, [-2, -1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 13, 11, [0.196, 0, -0.196],
                    [0, 0, -1.108], [-0.196, 0, -0.196], [-1.108, 0, 0], [-0.196, 0, 0.196], [0, 0, 1.108],
                    [0.196, 0, 0.196], [1.108, 0, 0], [0.196, 0, -0.196], [0, 0, -1.108], [-0.196, 0, -0.196]]
        case _:
            data = [3, 8, 2, False, 3, [-2, -1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 13, 11, [0.784, 0, -0.784],
                    [0, 0, -1.108], [-0.784, 0, -0.784], [-1.108, 0, 0], [-0.784, 0, 0.784], [0, 0, 1.108],
                    [0.784, 0, 0.784], [1.108, 0, 0], [0.784, 0, -0.784], [0, 0, -1.108], [-0.784, 0, -0.784]]

    crv = mc.createNode('nurbsCurve', n=sn + 'Shape', p=obj, ss=1)
    mc.setAttr(crv + '.cc', *data, type='nurbsCurve')

    axes = {'x': [0, 0, -90], 'y': [0, 0, 0], 'z': [90, 0, 0]}
    rot = axes[axis.lower().strip('-')]
    mc.xform(crv + '.cp[*]', ro=rot, r=True)
    if '-' in axis:
        scl = [-1] * 3
        mc.scale(scl[0], scl[1], scl[2], crv + '.cp[*]', r=1)

    mc.setAttr(crv + '.ove', True)
    mc.setAttr(crv + '.ovrgbf', True)
    mc.setAttr(crv + '.ovrgb', *color)

    return obj


# Utility functions

def scoped_history(obj: str) -> list:
    """
    Get history focused on given objects
    :param obj:
    :return:
    """
    shp_orig = get_shp_orig(obj)
    hist = mc.listHistory(obj)
    # Stop at shape orig to avoid collecting history from other objects
    hist = hist[:hist.index(shp_orig[0]) + 1]
    return hist


def get_deform_geo_index(deform: str, use_transform: bool = True) -> dict:
    """
    Get deformer geometry indices as a dict
    :param deform:
    :param use_transform: Use corresponding transform instead of shape
    :return:
    """
    geo = mc.deformer(deform, q=True, g=True) or []
    if use_transform:
        geo = mc.listRelatives(geo, p=True, pa=True) or []
    geo_idx = mc.deformer(deform, q=True, gi=True)
    geo_idx_dict = dict(zip(geo, geo_idx))
    return geo_idx_dict


def connect_geo_to_deform_gm(obj: str, deform: str, rm: bool = False) -> bool | None:
    """
    Connect object matrix to the adequate
    :param obj:
    :param deform:
    :param rm: Disconnect instead
    :return:
    """
    geo_idx_dict = get_deform_geo_index(deform, use_transform=True)
    geo_idx = geo_idx_dict.get(obj, None)
    if geo_idx is None:
        return False
    if not rm:
        mc.connectAttr(f'{obj}.worldMatrix[0]', f'{deform}.geomMatrix[{geo_idx}]', f=True)
    else:
        mc.disconnectAttr(f'{obj}.worldMatrix[0]', f'{deform}.geomMatrix[{geo_idx}]')
    return True


def get_next_obj_idx(name: str, start: int = 1) -> int:
    """
    Get the next free name index
    :param start: Start index
    :param name: Given object name
    :return: First available index
    """
    basename = re.sub('(\d+$)', '', name).rstrip('_')
    objlist = [a for a in mc.ls(basename + '*') if a[-1].isdigit()]

    if not objlist:
        return start

    idxlist = []
    for obj in objlist:
        tmp = obj.replace(basename, '').lstrip('_')
        if tmp:
            idxlist.append(int(tmp))

    lastidx = sorted(idxlist)[-1]
    i = 0
    for i in range(start, lastidx + 1):
        if i not in idxlist:
            return i

    return i + 1


def get_idx(name: str) -> int:
    """
    Get last index between brackets in a string
    :param name:
    :return: Index
    """
    match = re.search(r"\[(\d+)]$", name)
    if match:
        idx = int(match.group(1))
        return idx
    else:
        return None


def find_first_idx(indices: list) -> int:
    """
    Find 1st "hole" in a list of indices
    :param indices:
    :return: Free index
    """
    for i, idx in enumerate(indices):
        if i != idx:
            return i
    return len(indices)


def shorten_with_ns(name: str) -> str:
    """
    Shorten name path keeping namespace
    :param name:
    """
    return name.split('|')[-1]


def get_ns(name: str) -> str:
    """
    Get namespace from name
    :param str name: Input string
    :return: Namespace
    :rtype: str
    """

    splits = name.split(':')
    if len(splits) > 1:
        return splits[0]
    return ''


def get_shp_orig(objlist: list | str, io: bool = True) -> list:
    """
    Get Shape origin of given objects
    Shape origin is the shape ahead of an object's history

    :param objlist: Object(s) from where to look for the shape
    :param io: Restrict to intermediate object

    :return: List of shape(s)
    """
    result = []
    if isinstance(objlist, str):
        objlist = [objlist]
    for obj in objlist:
        shp = mc.listRelatives(obj, pa=1, s=1) or []
        hist = mc.listHistory(obj, bf=1) or []
        hist = [h for h in hist if h in shp]
        hist = mc.ls(hist, io=io) or hist
        result.append(hist[-1])
    return result


class DisableCycleCheck(object):
    """
    Temporary CycleCheck disable
    """

    def __enter__(self):
        mc.cycleCheck(e=False)

    def __exit__(self, typ, val, traceback):
        mc.cycleCheck(e=True)


# User feedback
def warning_msg(msg: str, color: list = (.0, .0, .0)):
    """
    Display warning message as in-view message AND to stdout
    :param msg:
    :param color:
    """
    back_color = rgbf_to_hex(color)
    mc.inViewMessage(amg=msg, pos='topCenter', fade=True, bkc=back_color)
    mc.warning(msg)


def rgbf_to_hex(rgb: list = (1., 1., 0), gamma: float = 2.2) -> int:
    """
    Convert rgb color to integer
    This is the color format accepted for in-view message
    :param rgb: Floating point rgb values
    :param gamma: Gamma correction
    :return: Encoded color
    """
    gc = 1.0 / gamma
    col = [int(round(v ** gc * 255)) for v in rgb]
    return (col[0] << 16) + (col[1] << 8) + col[2]

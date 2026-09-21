# coding:utf-8
"""
    :module: sticky_tool_UI.py
    :description: UI to create/edit sticky deformers
    :author: Michel 'Mitch' Pecqueur
    :date: 2026.06

import aresTools.stickyTool.sticky_tool_UI as stk_ui
stk_ui.StickyToolUI()

import stickyTool.sticky_tool_UI as stk_ui
stk_ui.StickyToolUI()
"""

from functools import partial
from pathlib import Path
from typing import cast, Self

import maya.cmds as mc
import maya.mel as mel
import shiboken6 as shiboken
from PySide6 import QtWidgets, QtGui, QtCore
from PySide6.QtCore import QObject, QEvent, Signal

from . import sticky as stk
from .UI import sticky_tool_ui as gui
from .__init__ import __version__  # noqa

try:
    from maya.OpenMayaUI import MQtUtil
except:
    pass


class StickyToolUI(gui.Ui_sticky_tool_mw, QtWidgets.QMainWindow):
    """
    StickyTool Main Window
    """

    def __init__(self):
        mc.help(popupMode=True)
        delete_qwidget(name='sticky_tool_mw')
        self.current_sticky = ''

        QtWidgets.QMainWindow.__init__(self, get_maya_window())

        self.setupUi(self)

        self.current_sticky_l = replace_widget(self.current_sticky_l, ClickableLabel())
        self.current_sticky_l = cast(ClickableLabel, self.current_sticky_l)  # For auto-completion
        style_widget(self.current_sticky_l, properties={'color': 'gray'}, clickable=True)

        self.default_icons_path = Path(__file__).parent / 'icons'
        self.icon_file = self.default_icons_path / 'stickyTool_64.png'
        self.setWindowIcon(QtGui.QIcon(str(self.icon_file)))

        self.tool_name = 'StickyTool'
        self.tool_version = __version__
        self.setWindowTitle(f'{self.tool_name} v{self.tool_version}')

        self.no_wheel_filter = WheelFilter(self)
        self.sticky_type_cmb.installEventFilter(self.no_wheel_filter)

        self.setup_menu_bar()
        self.tooltip_to_statusbar()
        self.setup_connections()

        self.set_sticky(disp_msg=False)

        self.show()

    def setup_connections(self):
        """
        Connect widgets
        """
        add_ctx(self.radius_dsb, [1, 2.5, 5, 10, 20])

        self.create_sticky_pb.clicked.connect(self.create_sticky)
        self.delete_sticky_pb.clicked.connect(self.delete_sticky)

        self.set_current_pb.clicked.connect(partial(self.set_sticky, disp_msg=True))

        self.current_sticky_l.doubleClicked.connect(self.select_sticky)

        self.add_obj_pb.clicked.connect(self.edit_sticky)
        self.rm_obj_pb.clicked.connect(partial(self.edit_sticky, rm=True))

        self.paint_pb.clicked.connect(partial(self.paint_sticky, value=1))
        self.erase_pb.clicked.connect(partial(self.paint_sticky, value=0))

    def setup_menu_bar(self):
        """
        Add menu bar
        """
        self.menu_bar = QtWidgets.QMenuBar(self)
        self.menu_bar.setNativeMenuBar(False)

        plt = self.menu_bar.palette()
        plt.setColor(QtGui.QPalette.ColorRole.Window, QtGui.QColor(55, 55, 55))
        self.menu_bar.setPalette(plt)

        # Help Menu
        self.help_menu = QtWidgets.QMenu(self.menu_bar)
        self.help_menu.setTitle('?')

        self.about_a = QtGui.QAction(self)
        self.about_a.setText('About')
        self.help_menu.addAction(self.about_a)

        self.menu_bar.addAction(self.help_menu.menuAction())

        self.about_a.triggered.connect(self.about_dialog)

        # Add menu bar
        self.setMenuBar(self.menu_bar)

    def create_sticky(self):
        """
        Create sticky deformer
        """
        sticky_type = self.sticky_type_cmb.currentText()
        radius = self.radius_dsb.value()

        with UndoChunk():
            result = stk.create_sticky_on_cp(typ=sticky_type, radius=radius)
        if result:
            self.update_current_sticky(result[-1])
            color = [v * .2 for v in self.get_sticky_color(result[-1], to_int=False)]
            if sticky_type == 'cluster':
                self.paint_sticky()
            stk.warning_msg(f'{self.current_sticky} created ✨', color=color)

    def delete_sticky(self):
        """
        Delete sticky deformer
        """
        sel = mc.ls(sl=True, tr=True)
        if not sel:
            stk.warning_msg('Nothing selected')
            return
        with UndoChunk():
            result = stk.delete_sticky(sel)

        if not result:
            stk.warning_msg('Select some sticky deformer(s) to delete')
        else:
            items_str = ' '.join(result)
            stk.warning_msg(f'{items_str} deleted ❌')
            if self.current_sticky in result:
                self.update_current_sticky('')

    def set_sticky(self, disp_msg: bool = True):
        """
        Set selected sticky as current
        :param disp_msg: Enable in-vew message display
        """
        sel = mc.ls(sl=True, tr=True)
        if not sel:
            if disp_msg:
                stk.warning_msg('Select a sticky control')
            return

        sticky = stk.get_sticky(sel)
        if sticky:
            self.update_current_sticky(sticky[0])
        else:
            if disp_msg:
                stk.warning_msg('Select a sticky control')
            return

    def update_current_sticky(self, sticky: str = ''):
        """
        Set given sticky as current sticky
        :param sticky: given sticky name
        """
        self.current_sticky = sticky
        self.current_sticky_l.setText(sticky)
        if sticky:
            rgb = self.get_sticky_color(sticky)
            style_widget(self.current_sticky_l, properties={'color': f'rgb{rgb}'}, clickable=True)
        else:
            self.current_sticky_l.setStyleSheet('')

    @staticmethod
    def get_sticky_color(sticky: str = '', gamma=1.0, to_int=True) -> tuple:
        """
        Get current sticky color for UI display
        :param sticky:
        :param gamma:
        :param to_int:
        :return:
        """
        deps = stk.get_sticky_deps([sticky])
        if deps:
            rgb = mc.getAttr(deps[0][1] + '.outlinerColor')[0]
            if to_int:
                gc = 1.0 / gamma
                rgb = tuple(int(round((v ** gc) * 255)) for v in rgb)
            return rgb

    def edit_sticky(self, rm: bool = False):
        """
        Edit influenced geometries by current sticky
        :param rm:
        """
        if not mc.ls(self.current_sticky):
            button_text = self.set_current_pb.text()
            stk.warning_msg(f"Set a valid sticky with '{button_text}'")
            return

        sel = mc.ls(sl=True, tr=True)
        if not sel:
            stk.warning_msg('Select some mesh object(s)')
            return

        objlist = [o for o in sel if mc.listRelatives(s=True, typ='mesh', ni=1, pa=True)]
        if not objlist:
            stk.warning_msg('Please select MESH object(s) 🙂')
            return

        with UndoChunk():
            for obj in objlist:
                if not rm:
                    mc.deformer(self.current_sticky, e=True, g=obj)
                    stk.connect_geo_to_deform_gm(obj=obj, deform=self.current_sticky, rm=False)
                if rm:
                    stk.connect_geo_to_deform_gm(obj=obj, deform=self.current_sticky, rm=True)
                    mc.deformer(self.current_sticky, e=True, rm=True, g=obj)

        objlist_str = ' '.join(objlist)
        if rm:
            stk.warning_msg(f'{objlist_str} removed from {self.current_sticky}')
        else:
            stk.warning_msg(f'{objlist_str} added to {self.current_sticky}')

    def paint_sticky(self, value: float = 1.0):
        """
        Paint weights for current sticky
        :param value: Default weight value in tool window
        """
        sel_shp = mc.listRelatives(mc.ls(sl=True), s=True, pa=True, ni=True) or []

        if self.current_sticky and mc.objExists(self.current_sticky):
            geo = mc.deformer(self.current_sticky, q=True, g=True) or []
            if geo:
                mc.select(geo, r=True)
                sel_shp = [s for s in sel_shp if s in set(geo)]
                if sel_shp:
                    mc.select(sel_shp, r=True)
                mel_cmd = f'artSetToolAndSelectAttr("artAttrCtx", "cluster.{self.current_sticky}.weights")'
                mel.eval(mel_cmd)
                mel.eval('artAttrPaintOperation("artAttrCtx","Replace")')
                mel.eval(f'artAttrCtx -e -value {value} `currentCtx`')
                mc.toolPropertyWindow()
                return

        button_text = self.set_current_pb.text()
        stk.warning_msg(f"Set a valid sticky with '{button_text}'")

    def select_sticky(self):
        """
        Select current sticky
        """
        if mc.ls(self.current_sticky):
            deps = stk.get_sticky_deps([self.current_sticky])
            if deps:
                mc.select(deps[0][1], r=True)

    def tooltip_to_statusbar(self):
        """
        Copy toolTip messages to statusTip
        """
        for item in self.findChildren(QtWidgets.QWidget):
            tooltip = item.toolTip()
            if tooltip:
                item.setStatusTip(tooltip)

    def about_dialog(self):
        """
        Display some info about this tool
        """
        try:
            about_dlg = AboutDialog(parent=self,
                                    icon_file=self.icon_file,
                                    title=f'About {self.tool_name}')
            text = (f"{self.tool_name} Version {__version__}\n"
                    f"Copyright © 2026 Michel 'Mitch' Pecqueur\n\n")
            about_dlg.set_text(text)
            about_dlg.append_url('https://github.com/robotmitchum/stickyTool')
            about_dlg.exec()
        except Exception as e:
            print(e)
            pass


# Widgets utility functions
class WheelFilter(QObject):
    """
    Event filter intercepting and ignoring wheel events
    """

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.Wheel:
            # Intercept the wheel event
            event.accept()
            return True
        # Pass through for other events
        return super().eventFilter(obj, event)


class ClickableLabel(QtWidgets.QLabel):
    """
    Clickable QLabel
    """
    doubleClicked = Signal()

    def mouseDoubleClickEvent(self, event):
        self.doubleClicked.emit()
        super().mouseDoubleClickEvent(event)


class AboutDialog(QtWidgets.QDialog):
    """
    Display an info dialog
    """

    def __init__(self, parent: QtWidgets.QWidget = None, title: str = 'About', icon_file: Path | str | None = None):
        super().__init__(parent)
        self.setSizePolicy(QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Minimum)
        self.setFixedSize(0, 0)
        self.setWindowTitle(title or 'About')

        # Icon
        self.icon_l = QtWidgets.QLabel(self)
        self.icon_pixmap = None
        self.set_icon(icon_file)

        # Message with clickable URL
        self.msg_l = QtWidgets.QLabel(self)
        self.msg_l.setTextFormat(QtCore.Qt.TextFormat.RichText)
        self.msg_l.setTextInteractionFlags(QtCore.Qt.TextInteractionFlag.TextBrowserInteraction)
        self.msg_l.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.msg_l.linkActivated.connect(self.handle_link_clicked)

        # - Layout -
        self.content_lyt = QtWidgets.QHBoxLayout()
        self.content_lyt.addWidget(self.icon_l)
        self.content_lyt.addWidget(self.msg_l)

        self.lyt = QtWidgets.QVBoxLayout()
        self.lyt.addLayout(self.content_lyt)

        self.setLayout(self.lyt)

    def set_icon(self, icon_file: Path | str | None = None):
        if icon_file:
            self.icon_pixmap = QtGui.QPixmap(str(icon_file))
        else:
            self.icon_pixmap = QtGui.QPixmap(64, 64)
            self.icon_pixmap.fill(QtCore.Qt.GlobalColor.green)
        self.icon_l.setPixmap(self.icon_pixmap)

    def set_text(self, value: str, append: bool = True):
        v = value.replace('\n', '<br>')
        if append:
            self.msg_l.setText(self.msg_l.text() + v)
        else:
            self.msg_l.setText(v)

    def append_url(self, value: str, end_line: str = '\n'):
        v = end_line.replace('\n', '<br>')
        self.msg_l.setText(f'{self.msg_l.text()}<a href="{value}">{value}</a>' + v)

    def handle_link_clicked(self, url: str):
        QtGui.QDesktopServices.openUrl(QtCore.QUrl(url))
        self.accept()


def replace_widget(old_widget: QtWidgets.QWidget, new_widget: QtWidgets.QWidget) -> QtWidgets.QWidget:
    """
    Replace a placeholder widget with another widget (typically a customized version of this widget)
    :param old_widget:
    :param new_widget:
    """
    copy_properties(old_widget, new_widget)
    lyt = old_widget.parentWidget().layout()
    lyt.replaceWidget(old_widget, new_widget)
    old_widget.deleteLater()
    return new_widget


def copy_properties(src, tgt):
    """
    Copy properties from a source widget to target widget
    :param src: source widget
    :param tgt: target widget
    """
    meta = src.metaObject()
    for i in range(meta.propertyCount()):
        prop = meta.property(i)
        if prop.isReadable() and prop.isWritable():
            name = prop.name()
            if name == 'alignment':
                tgt.setAlignment(src.alignment())
            else:
                value = src.property(name)
                tgt.setProperty(name, value)


# Stylesheet utils

def dict_to_stylesheet(widget: str, properties: dict) -> str:
    """
    Convert properties dict to a css stylesheet string
    :param widget:
    :param properties:
    :return:
    """
    result = ('', f'{widget} {{')[bool(widget)]
    for key, value in properties.items():
        result += f'{key}: {value}; '
    result = (result[:-1], result[:-1] + '}')[bool(widget)]
    return result


def get_text_color(widget: QtWidgets.QWidget) -> QtGui.QColor:
    """Get most relevant text color"""
    plt = widget.palette()
    for role in [QtGui.QPalette.ColorRole.ButtonText, QtGui.QPalette.ColorRole.WindowText,
                 QtGui.QPalette.ColorRole.Text]:
        color = plt.color(role)
        if color.isValid():
            return color
    return QtGui.QColor(0, 0, 0)


def style_widget(widget: QtWidgets.QWidget, properties: dict, clickable: bool = True):
    """
    Style a given widget using stylesheet creating derived colors for hover and disabled state

    NOTE : This is a modified version using custom Array class instead of a numpy array class for color blending!

    :param widget:
    :param properties:
    :param clickable: Create a clicked state (typically for buttons)
    """
    wid_class = widget.__class__.__name__

    enabled = widget.isEnabled()
    widget.setEnabled(True)  # Enable widget to capture properly its original palette

    widget.show()  # Force color update
    plt = widget.palette()

    text_color = get_text_color(widget)
    bg_color = plt.color(widget.backgroundRole())
    # bg_alpha = bg_color.alpha()

    prop = dict(properties)
    prop['color'] = properties.get('color', text_color.name())

    ss = widget.styleSheet()

    bg_transparent = False
    if isinstance(widget, QtWidgets.QLabel) and not ss:
        bg_transparent = True
    elif 'background-color:transparent' in ss.replace(' ', '').lower():
        bg_transparent = True

    if bg_transparent:
        prop['background-color'] = 'transparent'
    else:
        prop['background-color'] = properties.get('background-color', bg_color.name())

    ss = dict_to_stylesheet(wid_class, prop)

    widget.setStyleSheet(ss)
    plt = widget.palette()
    text_color = get_text_color(widget)
    bg_color = plt.color(widget.backgroundRole())

    # Calculate hover, disabled and pressed states from base color
    text_rgb = Array(text_color.getRgb()[:3])
    bg_rgb = Array(bg_color.getRgb()[:3])

    # Hover: original color mixed with white
    hover_text_color = Array(text_rgb).lerp(255, .5).as_int()
    hover_bg_color = Array(bg_rgb).lerp(255, .5).as_int()

    # Disabled : original color converted to luminance mixed with dark gray
    disabled_text_color = Array([max(text_rgb)] * 3).lerp(63, .5).as_int()
    disabled_bg_color = Array([max(bg_rgb)] * 3).lerp(63, .5).as_int()

    ss += f'\n{wid_class}:hover {{color: rgb{hover_text_color};'
    ss += (f' background-color: rgb{hover_bg_color};}}', '}')[bg_transparent]

    ss += f'\n{wid_class}:disabled {{color: rgb{disabled_text_color};'
    ss += (f' background-color: rgb{disabled_bg_color};}}', '}')[bg_transparent]

    if clickable:
        # Pressed : original color mixed with middle gray
        pressed_bg_color = Array(bg_rgb).lerp(127, .3).as_int()
        ss += f'\n{wid_class}:pressed {{color: {text_color.name()};'
        ss += (f' background-color: rgb{pressed_bg_color};}}', '}')[bg_transparent]

    widget.setEnabled(enabled)  # Set widget to its original state

    widget.setStyleSheet(ss)


# Math functions

class Array(object):
    """
    Simple N-dimensional Array class emulating some of the most basic functionality of a numpy array
    Useful to avoid including numpy for undemanding things such as color blending
    """

    def __init__(self, values):
        self.values = values

    def __str__(self) -> str:
        """
        Printable
        """
        return str(self.values)

    def __repr__(self) -> str:
        """
        Evaluable
        """
        return str(self.values)

    def __call__(self) -> list[float]:
        """
        Get array object as a list
        """
        return list(self.values)

    def __getitem__(self, idx: int) -> float:
        """
        Get the index value
        """
        return self.values[idx]

    def __iter__(self) -> iter:
        """
        Iterable
        """
        return self.values.__iter__()

    def __len__(self) -> int:
        """
        Get the array dimension
        """
        return len(self.values)

    def __neg__(self) -> Self:
        """
        Negate array
        """
        return self.__mul__(-1)

    def __add__(self, other: Self | float) -> Self:
        """
        +
        """
        result = self
        if isinstance(other, Array):
            result = tuple(a + b for a, b in zip(self.values, other.values))
        elif isinstance(other, (int, float)):
            result = tuple(a + other for a in self.values)
        return Array(result)

    def __radd__(self, other: Self | float) -> Self:
        return self.__add__(other)

    def __sub__(self, other: Self | float) -> Self:
        """
        -
        """
        result = self
        if isinstance(self, type(other)):
            result = tuple(a - b for a, b in zip(self.values, other.values))
        elif isinstance(other, (int, float)):
            result = tuple(a - other for a in self.values)
        return Array(result)

    def __rsub__(self, other: Self | float) -> Self:
        return self.__mul__(-1).__add__(other)

    def __mul__(self, other: Self | float) -> Self:
        """
        *
        """
        result = self
        if isinstance(self, type(other)):
            result = tuple(a * b for a, b in zip(self.values, other.values))
        elif isinstance(other, (int, float)):
            result = tuple(a * other for a in self.values)
        return Array(result)

    def __rmul__(self, other: Self | float) -> Self:
        """
        Reverse multiplication
        """
        return self.__mul__(other)

    def __truediv__(self, other: Self | float) -> Self:
        """
        /
        """
        result = self
        if isinstance(self, type(other)):
            result = tuple(a / b for a, b in zip(self.values, other.values))
        elif isinstance(other, (int, float)):
            result = tuple(a / other for a in self.values)
        return Array(result)

    def __rtruediv__(self, other):
        result = self
        if isinstance(self, type(other)):
            result = tuple(b / a for a, b in zip(self.values, other.values))
        elif isinstance(other, (int, float)):
            result = tuple(other / a for a in self.values)
        return Array(result)

    def __pow__(self, other: Self | float) -> Self:
        """
        **
        """
        result = self
        if isinstance(self, type(other)):
            result = tuple(a ** b for a, b in zip(self.values, other.values))
        elif isinstance(other, (int, float)):
            result = tuple(a ** other for a in self.values)
        return Array(result)

    def lerp(self, other: Self | float, x: float) -> Self:
        """
        Linear interpolation
        :param other:
        :param x: Blending factor
        """
        result = self
        if isinstance(other, Array):
            result = tuple(lerp(a, b, x) for a, b in zip(self.values, other.values))
        elif isinstance(other, (int, float)):
            result = tuple(lerp(a, other, x) for a in self.values)
        return Array(result)

    def as_int(self) -> tuple[int, ...]:
        """
        Round values and return as int
        :return:
        """
        result = tuple(int(round(v)) for v in self.values)
        return result


def lerp(a, b, x):
    """
    Linear interpolation between a and b
    :param a:
    :param b:
    :param x:
    :return:
    """
    return a + (b - a) * x


# Misc UI functions

class UndoChunk(object):
    """
    Open/close an undo chunk to ensure correct undo behavior when calling code from a UI

    Example:
    from aresCoreUI.ui_utils import UndoChunk

    with UndoChunk():
        res = mc.ls(...)
        print(res)

    UndoChunk is active only within current context
    """

    def __enter__(self):
        mc.undoInfo(ock=True)

    def __exit__(self, typ, val, traceback):
        mc.undoInfo(cck=True)


def get_maya_window() -> QtWidgets or None:
    """
    Get Maya main window
    :return: Maya window pointer
    """
    mwindow = MQtUtil.mainWindow()
    pointer = shiboken.wrapInstance(int(mwindow), QtWidgets.QMainWindow)
    return pointer


def delete_qwidget(name: str):
    """
    Delete given QWidget
    :param name:
    :return: None
    """
    mwindow = MQtUtil.findControl(name)
    if mwindow:
        pointer = shiboken.wrapInstance(int(mwindow), QtWidgets.QMainWindow)
        shiboken.delete(pointer)


def add_ctx(widget: QtWidgets.QWidget, values: list = (), names: list | None = None, default_idx: int | None = None,
            trigger: QtWidgets.QWidget | None = None):
    """
    Add a simple context menu setting provided values to the given widget

    (Ported from PyQt5 with minor modifications to make it work)

    :param widget: The widget to which the context menu will be added
    :param values: A list of values to be added as actions in the context menu
    :param default_idx:
    :param names: A list of strings or values to be added as action names
    must match values length
    :param trigger: Optional widget triggering the context menu
    typically a QPushButton or QToolButton
    """
    if not names:
        names = list(values)
        if default_idx is not None:
            names[default_idx] = f'{names[default_idx]} (Default)'

    def show_context_menu(event):
        menu = QtWidgets.QMenu(widget)
        for name, value in zip(names, values):
            if value == '---':
                menu.addSeparator()
            else:
                action = menu.addAction(f'{name}')
                if hasattr(widget, 'setValue'):
                    action.triggered.connect(partial(widget.setValue, value))
                elif hasattr(widget, 'setFullPath'):
                    action.triggered.connect(partial(widget.setFullPath, value))
                elif hasattr(widget, 'setText'):
                    action.triggered.connect(partial(widget.setText, value))

        pos = widget.mapToGlobal(widget.contentsRect().bottomLeft())
        menu.setMinimumWidth(widget.width())
        menu.exec_(pos)
        menu.deleteLater()

    widget.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
    if trigger is None:
        widget.customContextMenuRequested.connect(show_context_menu)
    else:
        trigger.clicked.connect(show_context_menu)

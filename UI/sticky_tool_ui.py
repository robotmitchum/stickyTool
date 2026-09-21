# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'sticky_tool_ui.ui'
##
## Created by: Qt User Interface Compiler version 6.10.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QAbstractSpinBox, QApplication, QComboBox, QDoubleSpinBox,
    QHBoxLayout, QLabel, QMainWindow, QPushButton,
    QSizePolicy, QStatusBar, QVBoxLayout, QWidget)

class Ui_sticky_tool_mw(object):
    def setupUi(self, sticky_tool_mw):
        if not sticky_tool_mw.objectName():
            sticky_tool_mw.setObjectName(u"sticky_tool_mw")
        sticky_tool_mw.resize(480, 320)
        font = QFont()
        font.setPointSize(10)
        sticky_tool_mw.setFont(font)
        sticky_tool_mw.setLocale(QLocale(QLocale.English, QLocale.UnitedStates))
        self.centralwidget = QWidget(sticky_tool_mw)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setSpacing(4)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(8, 8, 8, 8)
        self.create_sticky_l = QLabel(self.centralwidget)
        self.create_sticky_l.setObjectName(u"create_sticky_l")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.create_sticky_l.sizePolicy().hasHeightForWidth())
        self.create_sticky_l.setSizePolicy(sizePolicy)
        self.create_sticky_l.setMinimumSize(QSize(0, 20))
        self.create_sticky_l.setStyleSheet(u"background-color: rgb(95, 95, 127);")

        self.verticalLayout.addWidget(self.create_sticky_l)

        self.sticky_settings_lyt = QHBoxLayout()
        self.sticky_settings_lyt.setObjectName(u"sticky_settings_lyt")
        self.sticky_type_l = QLabel(self.centralwidget)
        self.sticky_type_l.setObjectName(u"sticky_type_l")
        sizePolicy.setHeightForWidth(self.sticky_type_l.sizePolicy().hasHeightForWidth())
        self.sticky_type_l.setSizePolicy(sizePolicy)
        self.sticky_type_l.setAlignment(Qt.AlignCenter)

        self.sticky_settings_lyt.addWidget(self.sticky_type_l)

        self.sticky_type_cmb = QComboBox(self.centralwidget)
        self.sticky_type_cmb.addItem("")
        self.sticky_type_cmb.addItem("")
        self.sticky_type_cmb.setObjectName(u"sticky_type_cmb")
        self.sticky_type_cmb.setFrame(False)

        self.sticky_settings_lyt.addWidget(self.sticky_type_cmb)

        self.radius_l = QLabel(self.centralwidget)
        self.radius_l.setObjectName(u"radius_l")
        sizePolicy.setHeightForWidth(self.radius_l.sizePolicy().hasHeightForWidth())
        self.radius_l.setSizePolicy(sizePolicy)
        self.radius_l.setAlignment(Qt.AlignCenter)

        self.sticky_settings_lyt.addWidget(self.radius_l)

        self.radius_dsb = QDoubleSpinBox(self.centralwidget)
        self.radius_dsb.setObjectName(u"radius_dsb")
        self.radius_dsb.setFrame(False)
        self.radius_dsb.setAlignment(Qt.AlignCenter)
        self.radius_dsb.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.radius_dsb.setMinimum(0.500000000000000)
        self.radius_dsb.setMaximum(50.000000000000000)
        self.radius_dsb.setValue(2.500000000000000)

        self.sticky_settings_lyt.addWidget(self.radius_dsb)


        self.verticalLayout.addLayout(self.sticky_settings_lyt)

        self.create_delete_lyt = QHBoxLayout()
        self.create_delete_lyt.setObjectName(u"create_delete_lyt")
        self.create_sticky_pb = QPushButton(self.centralwidget)
        self.create_sticky_pb.setObjectName(u"create_sticky_pb")
        font1 = QFont()
        font1.setBold(False)
        font1.setItalic(False)
        self.create_sticky_pb.setFont(font1)
        self.create_sticky_pb.setStyleSheet(u"")

        self.create_delete_lyt.addWidget(self.create_sticky_pb)

        self.delete_sticky_pb = QPushButton(self.centralwidget)
        self.delete_sticky_pb.setObjectName(u"delete_sticky_pb")
        self.delete_sticky_pb.setStyleSheet(u"")

        self.create_delete_lyt.addWidget(self.delete_sticky_pb)


        self.verticalLayout.addLayout(self.create_delete_lyt)

        self.edit_sticky_l = QLabel(self.centralwidget)
        self.edit_sticky_l.setObjectName(u"edit_sticky_l")
        sizePolicy.setHeightForWidth(self.edit_sticky_l.sizePolicy().hasHeightForWidth())
        self.edit_sticky_l.setSizePolicy(sizePolicy)
        self.edit_sticky_l.setMinimumSize(QSize(0, 20))
        self.edit_sticky_l.setStyleSheet(u"background-color: rgb(95, 95, 127);")

        self.verticalLayout.addWidget(self.edit_sticky_l)

        self.set_current_pb = QPushButton(self.centralwidget)
        self.set_current_pb.setObjectName(u"set_current_pb")
        self.set_current_pb.setStyleSheet(u"")

        self.verticalLayout.addWidget(self.set_current_pb)

        self.current_sticky_lyt = QHBoxLayout()
        self.current_sticky_lyt.setObjectName(u"current_sticky_lyt")
        self.current_stick_title_l = QLabel(self.centralwidget)
        self.current_stick_title_l.setObjectName(u"current_stick_title_l")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.current_stick_title_l.sizePolicy().hasHeightForWidth())
        self.current_stick_title_l.setSizePolicy(sizePolicy1)

        self.current_sticky_lyt.addWidget(self.current_stick_title_l)

        self.current_sticky_l = QLabel(self.centralwidget)
        self.current_sticky_l.setObjectName(u"current_sticky_l")
        sizePolicy.setHeightForWidth(self.current_sticky_l.sizePolicy().hasHeightForWidth())
        self.current_sticky_l.setSizePolicy(sizePolicy)
        font2 = QFont()
        font2.setBold(True)
        font2.setItalic(True)
        self.current_sticky_l.setFont(font2)
        self.current_sticky_l.setAlignment(Qt.AlignCenter)

        self.current_sticky_lyt.addWidget(self.current_sticky_l)


        self.verticalLayout.addLayout(self.current_sticky_lyt)

        self.add_rm_lyt = QHBoxLayout()
        self.add_rm_lyt.setObjectName(u"add_rm_lyt")
        self.add_obj_pb = QPushButton(self.centralwidget)
        self.add_obj_pb.setObjectName(u"add_obj_pb")
        self.add_obj_pb.setStyleSheet(u"")

        self.add_rm_lyt.addWidget(self.add_obj_pb)

        self.rm_obj_pb = QPushButton(self.centralwidget)
        self.rm_obj_pb.setObjectName(u"rm_obj_pb")
        self.rm_obj_pb.setStyleSheet(u"")

        self.add_rm_lyt.addWidget(self.rm_obj_pb)


        self.verticalLayout.addLayout(self.add_rm_lyt)

        self.paint_weights_lyt = QHBoxLayout()
        self.paint_weights_lyt.setObjectName(u"paint_weights_lyt")
        self.paint_pb = QPushButton(self.centralwidget)
        self.paint_pb.setObjectName(u"paint_pb")
        self.paint_pb.setStyleSheet(u"")

        self.paint_weights_lyt.addWidget(self.paint_pb)

        self.erase_pb = QPushButton(self.centralwidget)
        self.erase_pb.setObjectName(u"erase_pb")
        self.erase_pb.setStyleSheet(u"")

        self.paint_weights_lyt.addWidget(self.erase_pb)


        self.verticalLayout.addLayout(self.paint_weights_lyt)

        sticky_tool_mw.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(sticky_tool_mw)
        self.statusbar.setObjectName(u"statusbar")
        sticky_tool_mw.setStatusBar(self.statusbar)

        self.retranslateUi(sticky_tool_mw)

        QMetaObject.connectSlotsByName(sticky_tool_mw)
    # setupUi

    def retranslateUi(self, sticky_tool_mw):
        sticky_tool_mw.setWindowTitle(QCoreApplication.translate("sticky_tool_mw", u"StickyTool", None))
        self.create_sticky_l.setText(QCoreApplication.translate("sticky_tool_mw", u"Create Sticky", None))
        self.sticky_type_l.setText(QCoreApplication.translate("sticky_tool_mw", u"Sticky Type", None))
        self.sticky_type_cmb.setItemText(0, QCoreApplication.translate("sticky_tool_mw", u"softmod", None))
        self.sticky_type_cmb.setItemText(1, QCoreApplication.translate("sticky_tool_mw", u"cluster", None))

#if QT_CONFIG(tooltip)
        self.sticky_type_cmb.setToolTip(QCoreApplication.translate("sticky_tool_mw", u"Deformer Type: softmod or cluster", None))
#endif // QT_CONFIG(tooltip)
        self.radius_l.setText(QCoreApplication.translate("sticky_tool_mw", u"Radius", None))
#if QT_CONFIG(tooltip)
        self.radius_dsb.setToolTip(QCoreApplication.translate("sticky_tool_mw", u"Default radius for sofmod, can be changed after creation", None))
#endif // QT_CONFIG(tooltip)
        self.radius_dsb.setSuffix(QCoreApplication.translate("sticky_tool_mw", u" cm", None))
#if QT_CONFIG(tooltip)
        self.create_sticky_pb.setToolTip(QCoreApplication.translate("sticky_tool_mw", u"Create sticky on selected component(s)", None))
#endif // QT_CONFIG(tooltip)
        self.create_sticky_pb.setText(QCoreApplication.translate("sticky_tool_mw", u"\u2728 Create", None))
#if QT_CONFIG(tooltip)
        self.delete_sticky_pb.setToolTip(QCoreApplication.translate("sticky_tool_mw", u"Cleanly delete selected sticky deformer(s)", None))
#endif // QT_CONFIG(tooltip)
        self.delete_sticky_pb.setText(QCoreApplication.translate("sticky_tool_mw", u"\u274c Delete", None))
        self.edit_sticky_l.setText(QCoreApplication.translate("sticky_tool_mw", u"Edit Sticky", None))
#if QT_CONFIG(tooltip)
        self.set_current_pb.setToolTip(QCoreApplication.translate("sticky_tool_mw", u"Set selected sticky as current sticky deformer", None))
#endif // QT_CONFIG(tooltip)
        self.set_current_pb.setText(QCoreApplication.translate("sticky_tool_mw", u"\u25bc Set Current Sticky", None))
        self.current_stick_title_l.setText(QCoreApplication.translate("sticky_tool_mw", u"Current Sticky", None))
#if QT_CONFIG(tooltip)
        self.current_sticky_l.setToolTip(QCoreApplication.translate("sticky_tool_mw", u"Add / Remove / Paint will modify this sticky deformer", None))
#endif // QT_CONFIG(tooltip)
        self.current_sticky_l.setText("")
#if QT_CONFIG(tooltip)
        self.add_obj_pb.setToolTip(QCoreApplication.translate("sticky_tool_mw", u"Add selected object(s) to current sticky deformer", None))
#endif // QT_CONFIG(tooltip)
        self.add_obj_pb.setText(QCoreApplication.translate("sticky_tool_mw", u"\uff0b Add to Sticky", None))
#if QT_CONFIG(tooltip)
        self.rm_obj_pb.setToolTip(QCoreApplication.translate("sticky_tool_mw", u"Remove selected object(s) from current sticky deformer", None))
#endif // QT_CONFIG(tooltip)
        self.rm_obj_pb.setText(QCoreApplication.translate("sticky_tool_mw", u"\uff0d Remove from Sticky", None))
#if QT_CONFIG(tooltip)
        self.paint_pb.setToolTip(QCoreApplication.translate("sticky_tool_mw", u"Paint current sticky deformer", None))
#endif // QT_CONFIG(tooltip)
        self.paint_pb.setText(QCoreApplication.translate("sticky_tool_mw", u"\U0001f58c\U0000fe0f Paint Weights", None))
#if QT_CONFIG(tooltip)
        self.erase_pb.setToolTip(QCoreApplication.translate("sticky_tool_mw", u"Paint current sticky deformer", None))
#endif // QT_CONFIG(tooltip)
        self.erase_pb.setText(QCoreApplication.translate("sticky_tool_mw", u"\U0001f9f9 Erase Weights", None))
    # retranslateUi


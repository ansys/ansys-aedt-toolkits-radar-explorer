# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mode_column.ui'
##
## Created by: Qt User Interface Compiler version 6.7.3
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import QCoreApplication
from PySide6.QtCore import QMetaObject
from PySide6.QtWidgets import QSizePolicy
from PySide6.QtWidgets import QSpacerItem
from PySide6.QtWidgets import QStackedWidget
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QWidget


class Ui_LeftColumn(object):
    def setupUi(self, LeftColumn):
        if not LeftColumn.objectName():
            LeftColumn.setObjectName("LeftColumn")
        LeftColumn.resize(815, 600)
        self.verticalLayout = QVBoxLayout(LeftColumn)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.verticalLayout.setContentsMargins(5, 5, 5, 5)
        self.menus = QStackedWidget(LeftColumn)
        self.menus.setObjectName("menus")
        self.menu_mode_select = QWidget()
        self.menu_mode_select.setObjectName("menu_mode_select")
        self.menu_home_layout = QVBoxLayout(self.menu_mode_select)
        self.menu_home_layout.setSpacing(5)
        self.menu_home_layout.setObjectName("menu_home_layout")
        self.menu_home_layout.setContentsMargins(5, 5, 5, 5)
        self.mode_select_vertical_layout = QVBoxLayout()
        self.mode_select_vertical_layout.setObjectName("mode_select_vertical_layout")

        self.menu_home_layout.addLayout(self.mode_select_vertical_layout)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.menu_home_layout.addItem(self.verticalSpacer)

        self.menus.addWidget(self.menu_mode_select)

        self.verticalLayout.addWidget(self.menus)

        self.retranslateUi(LeftColumn)

        self.menus.setCurrentIndex(0)

        QMetaObject.connectSlotsByName(LeftColumn)

    # setupUi

    def retranslateUi(self, LeftColumn):
        LeftColumn.setWindowTitle(QCoreApplication.translate("LeftColumn", "Form", None))

    # retranslateUi

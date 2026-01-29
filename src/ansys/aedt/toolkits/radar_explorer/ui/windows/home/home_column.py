# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'home_column.ui'
##
## Created by: Qt User Interface Compiler version 6.7.1
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


class Ui_HomeColumn(object):
    def setupUi(self, HomeColumn):
        if not HomeColumn.objectName():
            HomeColumn.setObjectName("HomeColumn")
        HomeColumn.resize(815, 600)
        self.verticalLayout = QVBoxLayout(HomeColumn)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.verticalLayout.setContentsMargins(5, 5, 5, 5)
        self.menus = QStackedWidget(HomeColumn)
        self.menus.setObjectName("menus")
        self.menu_home = QWidget()
        self.menu_home.setObjectName("menu_home")
        self.menu_home_layout = QVBoxLayout(self.menu_home)
        self.menu_home_layout.setSpacing(5)
        self.menu_home_layout.setObjectName("menu_home_layout")
        self.menu_home_layout.setContentsMargins(5, 5, 5, 5)
        self.home_vertical_layout = QVBoxLayout()
        self.home_vertical_layout.setObjectName("home_vertical_layout")

        self.menu_home_layout.addLayout(self.home_vertical_layout)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.menu_home_layout.addItem(self.verticalSpacer)

        self.menus.addWidget(self.menu_home)

        self.verticalLayout.addWidget(self.menus)

        self.retranslateUi(HomeColumn)

        self.menus.setCurrentIndex(0)

        QMetaObject.connectSlotsByName(HomeColumn)

    # setupUi

    def retranslateUi(self, HomeColumn):
        HomeColumn.setWindowTitle(QCoreApplication.translate("HomeColumn", "Form", None))

    # retranslateUi

# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'home_page.ui'
##
## Created by: Qt User Interface Compiler version 6.7.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import QCoreApplication
from PySide6.QtCore import QMetaObject
from PySide6.QtCore import QSize
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QSizePolicy
from PySide6.QtWidgets import QSpacerItem
from PySide6.QtWidgets import QVBoxLayout


class Ui_Home(object):
    def setupUi(self, Home):
        if not Home.objectName():
            Home.setObjectName("Home")
        Home.resize(1199, 792)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Home.sizePolicy().hasHeightForWidth())
        Home.setSizePolicy(sizePolicy)
        Home.setMinimumSize(QSize(0, 0))
        self.verticalLayout_2 = QVBoxLayout(Home)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.home_label = QLabel(Home)
        self.home_label.setObjectName("home_label")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.home_label.sizePolicy().hasHeightForWidth())
        self.home_label.setSizePolicy(sizePolicy1)
        font = QFont()
        font.setPointSize(10)
        font.setBold(False)
        self.home_label.setFont(font)
        self.home_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_2.addWidget(self.home_label)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Maximum)

        self.verticalLayout_2.addItem(self.verticalSpacer)

        self.home_layout = QVBoxLayout()
        self.home_layout.setObjectName("home_layout")
        self.home_layout.setContentsMargins(-1, 0, -1, -1)

        self.verticalLayout_2.addLayout(self.home_layout)

        self.retranslateUi(Home)

        QMetaObject.connectSlotsByName(Home)

    # setupUi

    def retranslateUi(self, Home):
        Home.setWindowTitle(QCoreApplication.translate("Home", "Form", None))
        # self.home_label.setText(QCoreApplication.translate("Home", u"Radar Explorer Main Menu", None))

    # retranslateUi

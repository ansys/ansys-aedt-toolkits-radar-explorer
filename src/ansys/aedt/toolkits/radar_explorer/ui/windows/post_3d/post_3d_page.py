# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'plot_design_page.ui'
##
## Created by: Qt User Interface Compiler version 6.7.3
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import QCoreApplication
from PySide6.QtCore import QMetaObject
from PySide6.QtCore import QSize
from PySide6.QtWidgets import QSizePolicy
from PySide6.QtWidgets import QVBoxLayout


class Ui_Plot_Design(object):
    def setupUi(self, Plot_Design):
        if not Plot_Design.objectName():
            Plot_Design.setObjectName("Plot_Design")
        Plot_Design.resize(1205, 805)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Plot_Design.sizePolicy().hasHeightForWidth())
        Plot_Design.setSizePolicy(sizePolicy)
        Plot_Design.setMinimumSize(QSize(0, 0))
        self.verticalLayout_2 = QVBoxLayout(Plot_Design)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.plot_design_layout = QVBoxLayout()
        self.plot_design_layout.setObjectName("plot_design_layout")
        self.plot_design_layout.setContentsMargins(-1, 0, -1, -1)

        self.verticalLayout_2.addLayout(self.plot_design_layout)

        self.retranslateUi(Plot_Design)

        QMetaObject.connectSlotsByName(Plot_Design)

    # setupUi

    def retranslateUi(self, Plot_Design):
        Plot_Design.setWindowTitle(QCoreApplication.translate("Plot_Design", "Form", None))

    # retranslateUi

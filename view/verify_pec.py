# !/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# MIT License
#
# Copyright (c) 2022 FIT-Project and others
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# -----
######
import os
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog

from common.utility import get_ntp_date_and_time
from controller.verify_pec.verify_pec import verifyPec as verifyPecController
from view.error import Error as ErrorView

from view.case import Case as CaseView
from view.configuration import Configuration as ConfigurationView

from common.constants.view import verify_pec, general 
from common.utility import get_platform


class VerifyPec(QtWidgets.QMainWindow):
    stop_signal = QtCore.pyqtSignal()

    def __init__(self, *args, **kwargs):
        super(VerifyPec, self).__init__(*args, **kwargs)
        self.configuration_view = ConfigurationView(self)
        self.acquisition_directory = None

    def init(self, case_info, wizard, options=None):
        self.__init__()
        self.wizard = wizard
        self.width = 600
        self.height = 230
        self.setFixedSize(self.width, self.height)
        self.case_info = case_info

        self.case_view = CaseView(self.case_info, self)
        self.case_view.hide()

        self.setWindowIcon(QtGui.QIcon(os.path.join('assets/svg/', 'FIT.svg')))
        self.setObjectName("verify_pec_window")

        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.centralwidget.setStyleSheet("QWidget {background-color: rgb(255, 255, 255);}")
        self.setCentralWidget(self.centralwidget)

        # MENU BAR
        self.setCentralWidget(self.centralwidget)
        self.menuBar().setNativeMenuBar(False)

        # CONF BUTTON
        self.menu_configuration = QtWidgets.QAction("Configuration", self)
        self.menu_configuration.setObjectName("menuConfiguration")
        self.menu_configuration.triggered.connect(self.__configuration)
        self.menuBar().addAction(self.menu_configuration)

        # CASE BUTTON
        self.case_action = QtWidgets.QAction("Case", self)
        self.case_action.setStatusTip("Show case info")
        self.case_action.triggered.connect(self.__case)
        self.menuBar().addAction(self.case_action)

        # BACK ACTION
        back_action = QtWidgets.QAction("Back to wizard", self)
        back_action.setStatusTip("Go back to the main menu")
        back_action.triggered.connect(self.__back_to_wizard)
        self.menuBar().addAction(back_action)

        self.eml_group_box = QtWidgets.QGroupBox(self.centralwidget)
        self.eml_group_box.setEnabled(True)
        self.eml_group_box.setGeometry(QtCore.QRect(50, 20, 500, 180))
        self.eml_group_box.setObjectName("eml_group_box")

        # EML
        self.input_eml = QtWidgets.QLineEdit(self.centralwidget)
        self.input_eml.setGeometry(QtCore.QRect(160, 60, 260, 20))
        self.input_eml.setObjectName("input_eml")
        self.input_eml.setEnabled(False)
        self.input_eml_button = QtWidgets.QPushButton(self.centralwidget)
        self.input_eml_button.setGeometry(QtCore.QRect(450, 60, 75, 20))
        self.input_eml_button.clicked.connect(self.__dialog)

        # EML LABEL
        self.label_eml = QtWidgets.QLabel(self.centralwidget)
        self.label_eml.setGeometry(QtCore.QRect(80, 60, 50, 20))
        self.label_eml.setAlignment(QtCore.Qt.AlignRight)
        self.label_eml.setObjectName("label_eml")

        # VERIFICATION BUTTON
        self.verification_button = QtWidgets.QPushButton(self.centralwidget)
        self.verification_button.setGeometry(QtCore.QRect(450, 140, 75, 30))
        self.verification_button.clicked.connect(self.__verify)
        self.verification_button.setObjectName("StartAction")
        self.verification_button.setEnabled(False)

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)

        # DISABLE SCRAPE BUTTON IF FIELDS ARE EMPTY
        self.input_fields = [self.input_eml]
        for input_field in self.input_fields:
            input_field.textChanged.connect(self.__onTextChanged)

    def retranslateUi(self):
        self.setWindowTitle(general.MAIN_WINDOW_TITLE)
        self.eml_group_box.setTitle(verify_pec.EML_SETTINGS)
        self.label_eml.setText(verify_pec.EML_FILE)
        self.verification_button.setText(verify_pec.BUTTON_VERIFY)
        self.input_eml_button.setText(general.BROWSE)

    def __onTextChanged(self):
        all_fields_filled = all(input_field.text() for input_field in self.input_fields)
        self.verification_button.setEnabled(all_fields_filled)

    def __verify(self):
        self.configuration_general = self.configuration_view.get_tab_from_name("configuration_general")
        # Get network parameters for (NTP)
        self.configuration_network = self.configuration_general.findChild(QtWidgets.QGroupBox,
                                                                          'group_box_network_check')
        ntp = get_ntp_date_and_time(self.configuration_network.configuration["ntp_server"])
        pec = verifyPecController()
        try:
            pec.verify(self.input_eml.text(), self.case_info, ntp)
        except Exception as e:
            error_dlg = ErrorView(QtWidgets.QMessageBox.Critical,
                                    verify_pec.VERIFY_PEC_FAILED,
                                    verify_pec.VERIFY_PEC_FAILED_MGS,
                                    str(e))
            error_dlg.exec_()
        
        path = os.path.dirname(str(self.input_eml.text()))
        if get_platform() == 'win':
            os.startfile(os.path.join(path,"report_integrity_pec_verification.pdf"))


    def __dialog(self):

        file, check = QFileDialog.getOpenFileName(None, verify_pec.OPEN_EML_FILE, 
                                                    self.__get_acquisition_directory(), verify_pec.EML_FILES)
        if check:
            self.input_eml.setText(file)

    def __case(self):
        self.case_view.exec_()

    def __configuration(self):
        self.configuration_view.exec_()
    

    def __get_acquisition_directory(self):
        if not self.acquisition_directory:
            configuration_general = self.configuration_view.get_tab_from_name("configuration_general")
            open_folder = os.path.expanduser(
                os.path.join(configuration_general.configuration['cases_folder_path'], self.case_info['name']))
            return open_folder
        else:
            return self.acquisition_directory
        

    def __back_to_wizard(self):
        self.deleteLater()
        self.wizard.reload_case_info()
        self.wizard.show()

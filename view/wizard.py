#!/usr/bin/env python3
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

from PyQt5 import QtCore, QtGui, QtWidgets

from view.case_form import CaseForm as CaseFormView
from view.error import Error as ErrorView

from common.error import ErrorMessage

class CaseInfoPage(QtWidgets.QWizardPage):
    def __init__(self, parent=None):
        super(CaseInfoPage, self).__init__(parent)
        self.setObjectName("CaseInfoPage")

        self.case_info = {}

        self.error_msg = ErrorMessage()

        self.case_form_widget = QtWidgets.QWidget(self)
        self.case_form_widget.setGeometry(QtCore.QRect(0, 0, 795, 515))
        self.case_form_widget.setObjectName("case_form_widget")

        self.form = CaseFormView(self.case_form_widget)
        self.form.setGeometry(QtCore.QRect(0, 0, 400, 200))
      

        x = (self.case_form_widget.frameGeometry().width()/2) - (self.form.frameGeometry().width()/2) -20
        y = (self.case_form_widget.frameGeometry().height()/2) - (self.form.frameGeometry().height()/2)
        self.form.move(x, y)

        #This allow to edit every row on combox
        self.form.name.setEditable(True)
        self.form.name.setCurrentIndex(-1)
        self.form.name.currentTextChanged.connect(self.completeChanged)
        self.form.case_form_layout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.form.name)
           
    def isComplete(self):
        if self.form.name.findText(self.form.name.currentText()) >= 0:
            self.set_case_information(self.form.name.currentText())
        else:
            self.clear_case_information()
        return self.form.name.currentText() != ""
    
    def set_case_information(self, name):
        self.case_info = next((item for item in self.form.cases if item["name"] == name), None)
        if self.case_info is not None:
            for keyword, value in self.case_info.items():
                item = self.findChild(QtCore.QObject, keyword)
                if item is not None:
                    if isinstance(item, QtWidgets.QLineEdit) is not False:
                        if value is not None:
                            item.setText(value)
                    if isinstance(item, QtWidgets.QComboBox):
                        if keyword in 'types_proceedings_id': 
                            if value is not None:
                                item.setCurrentIndex(value)
                        else:
                            if value is not None:
                                item.setCurrentText(value)
    
    def clear_case_information(self):
        self.case_info = {}
        self.form.lawyer_name.setText("")
        self.form.types_proceedings.setCurrentIndex(-1)
        self.form.courthouse.setText("")
        self.form.proceedings_number.setText("")
    


class SelectTaskPage(QtWidgets.QWizardPage):
    def __init__(self, parent=None):
        super(SelectTaskPage, self).__init__(parent)

        self.setObjectName("SelectTask")

        # Create a button group for radio buttons
        self.radio_button_group = QtWidgets.QButtonGroup()
        self.radio_button_group.buttonToggled[QtWidgets.QAbstractButton, bool].connect(self.completeChanged)
        self.radio_button_container = QtWidgets.QWidget(self)
        self.radio_button_container.setGeometry(QtCore.QRect(130, 80, 501, 112))
        self.radio_button_container.setObjectName("radio_button_container")
        self.radio_buttons_hlayout = QtWidgets.QHBoxLayout(self.radio_button_container)
        self.radio_buttons_hlayout.setContentsMargins(0, 0, 0, 0)
        self.radio_buttons_hlayout.setObjectName("radio_buttons_hlayout")

        
        #RADIO BUTTON WEB
        self.web_radio_button_wrapper = QtWidgets.QWidget(self.radio_button_container)
        self.web_radio_button_wrapper.setStyleSheet("QWidget#web_radio_button_wrapper {\n""border: 1px solid black;\n""}")
        self.web_radio_button_wrapper.setObjectName("web_radio_button_wrapper")
        self.web_vlayout = QtWidgets.QVBoxLayout(self.web_radio_button_wrapper)
        self.web_vlayout.setContentsMargins(5, 5, 5, 5)
        self.web_vlayout.setObjectName("web_vlayout")
        self.web_img = QtWidgets.QLabel(self.web_radio_button_wrapper)
        self.web_img.setStyleSheet("image: url(asset/images/wizard/web.png);")
        self.web_img.setText("")
        self.web_img.setObjectName("web_img")
        self.web_vlayout.addWidget(self.web_img)
        self.web = QtWidgets.QRadioButton(self.web_radio_button_wrapper)
        self.web.setObjectName("web")
        self.web_vlayout.addWidget(self.web)
        self.radio_buttons_hlayout.addWidget(self.web_radio_button_wrapper)
        self.radio_button_group.addButton(self.web, 0)

        #RADIO BUTTON MAIL
        self.mail_radio_button_wrapper = QtWidgets.QWidget(self.radio_button_container)
        self.mail_radio_button_wrapper.setStyleSheet("QWidget#mail_radio_button_wrapper {\n""border: 1px solid #c3c3c3;\n""}")
        self.mail_radio_button_wrapper.setObjectName("mail_radio_button_wrapper")
        self.mail_vlayout = QtWidgets.QVBoxLayout(self.mail_radio_button_wrapper)
        self.mail_vlayout.setContentsMargins(5, 5, 5, 5)
        self.mail_vlayout.setObjectName("mail_vlayout")
        self.mail_img = QtWidgets.QLabel(self.mail_radio_button_wrapper)
        self.mail_img.setEnabled(False)
        self.mail_img.setStyleSheet("image: url(asset/images/wizard/mail-disabled.png);\n")
        self.mail_img.setText("")
        self.mail_img.setObjectName("mail_img")
        self.mail_vlayout.addWidget(self.mail_img)
        self.mail = QtWidgets.QRadioButton(self.mail_radio_button_wrapper)
        self.mail.setEnabled(False)
        self.mail.setObjectName("mail")
        self.mail_vlayout.addWidget(self.mail)
        self.radio_buttons_hlayout.addWidget(self.mail_radio_button_wrapper)
        self.radio_button_group.addButton(self.mail, 1)
        
        #RADIO BUTTON FACEBOOK
        self.fb_radio_button_wrapper = QtWidgets.QWidget(self.radio_button_container)
        self.fb_radio_button_wrapper.setStyleSheet("QWidget#fb_radio_button_wrapper {\n""border: 1px solid #c3c3c3;\n""}")
        self.fb_radio_button_wrapper.setObjectName("fb_radio_button_wrapper")
        self.fb_vlayout = QtWidgets.QVBoxLayout(self.fb_radio_button_wrapper)
        self.fb_vlayout.setContentsMargins(5, 5, 5, 5)
        self.fb_vlayout.setObjectName("fb_vlayout")
        self.fb_img = QtWidgets.QLabel(self.fb_radio_button_wrapper)
        self.fb_img.setEnabled(False)
        self.fb_img.setStyleSheet("image: url(asset/images/wizard/fb-disabled.png);")
        self.fb_img.setText("")
        self.fb_img.setObjectName("fb_img")
        self.fb_vlayout.addWidget(self.fb_img)
        self.fb = QtWidgets.QRadioButton(self.fb_radio_button_wrapper)
        self.fb.setEnabled(False)
        self.fb.setObjectName("fb")
        self.fb_vlayout.addWidget(self.fb)
        self.radio_buttons_hlayout.addWidget(self.fb_radio_button_wrapper)
        self.radio_button_group.addButton(self.fb, 2)


        #AREA RECAP INFO
        self.acquisition_group_box = QtWidgets.QGroupBox(self)
        self.acquisition_group_box.setEnabled(True)
        self.acquisition_group_box.setGeometry(QtCore.QRect(130, 280, 501, 171))
        self.acquisition_group_box.setObjectName("acquisition_group_box")
        self.recap_case_info = QtWidgets.QTextBrowser(self.acquisition_group_box)
        self.recap_case_info.setGeometry(QtCore.QRect(30, 30, 430, 121))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.recap_case_info.setFont(font)
        self.recap_case_info.setReadOnly(True)
        self.recap_case_info.setObjectName("recap_case_info")

    def isComplete(self):
        return self.radio_button_group.checkedId() >= 0


class Wizard(QtWidgets.QWizard):
    finished = QtCore.pyqtSignal(str, dict)

    def __init__(self, parent=None):
        super(Wizard, self).__init__(parent)

        self.width = 800
        self.height = 600
        self.setObjectName("WizardView")  



    def init_wizard(self):
        self.setFixedSize(self.width, self.height)
        self.setSizeGripEnabled(False)
        self.setWizardStyle(QtWidgets.QWizard.ModernStyle)
        self.setTitleFormat(QtCore.Qt.RichText)
        self.setSubTitleFormat(QtCore.Qt.RichText)
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)
        self.setWindowIcon(QtGui.QIcon('asset/images/icon.png'))


        self.case_info_page = CaseInfoPage(self)
        self.select_task_page = SelectTaskPage(self)

        self.addPage(self.case_info_page)
        self.addPage(self.select_task_page)

        self.button(QtWidgets.QWizard.NextButton).clicked.connect(lambda: self.select_task_page.recap_case_info.setHtml(self._get_recap_case_info_HTML()))

        self.button(QtWidgets.QWizard.FinishButton).clicked.connect(self._save_case)

        self.button(QtWidgets.QWizard.FinishButton).setDisabled(True)


        self.retranslateUi()

    def _save_case(self):
        
        buttons = self.select_task_page.radio_button_group.buttons()
        selected_buttons_index = [buttons[x].isChecked() for x in range(len(buttons))].index(True)
        task = buttons[selected_buttons_index].objectName()

        case_info = {}

        if 'id' in self.case_info_page.case_info:
            case_info = self.case_info_page.case_info

        #store information case on the local DB
        try:
            if case_info:
                self.case_info_page.form.controller.cases = self.case_info_page.case_info
            else:
                case_info =  self.case_info_page.form.controller.add(self.case_info_page.case_info)
        except Exception as error:
            error_dlg = ErrorView(QtWidgets.QMessageBox.Warning,
                            self.case_info_page.error_msg.TITLES['insert_update_case_info'],
                            self.case_info_page.error_msg.MESSAGES['insert_update_case_info'],
                            str(error)
                            )

            error_dlg.buttonClicked.connect(self.close)
            error_dlg.exec_()

        #Send signal to main loop to start the acquisition window
        self.finished.emit(task, case_info)

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("FITWizard", "FIT 1.0"))
        self.select_task_page.acquisition_group_box.setTitle(_translate("FITWizard", "Riepilogo anagrafica caso"))
        self.select_task_page.web.setText(_translate("FITWizard", "WEB"))
        self.select_task_page.mail.setText(_translate("FITWizard", "MAIL"))
        self.select_task_page.fb.setText(_translate("FITWizard", "FACEBOOK"))


    def _get_recap_case_info_HTML(self):

        self.case_info_page.case_info = self.case_info_page.form.get_current_case_info()

        html = "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
        html += "<html>\n"
        html += "<head>\n"
        html += "<meta name=\"qrichtext\" content=\"1\" />\n"
        html += "<style type=\"text/css\">\n"
        html += "p, li { white-space: pre-wrap; }\n"
        html += "</style>\n"
        html += "</head>\n"
        html += "<body style=\" font-family:\'Arial\'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
        for keyword, value in self.case_info_page.case_info.items():
            item = self.findChild(QtWidgets.QLabel, keyword + '_label')
            if item is not None:
                if value is None:
                    value = "N/A"
                label = item.text()
                html += "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; line-height:19px;\">\n"
                html += "<span style=\" font-family:\'Arial\',\'Courier New\',\'monospace\'; font-size:14px; font-weight:300; color:#000000;\">" + label  + ": </span>\n"
                html += "<span style=\" font-size:14px; font-weight:600;  color:#000000;\">" + str(value)  + "</span>\n"
                html += "</p>\n"
        html += "</body>\n"
        html += "</html>"

        return html
        
        
# !/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######

from PyQt6 import QtWidgets
from PyQt6.QtCore import QObject, pyqtSignal, QThread, QEventLoop, QTimer

from view.tasks.task import Task
from view.error import Error as ErrorView

from controller.pec import Pec as PecController
from controller.configurations.tabs.pec.pec import Pec as PecConfigController

from common.constants.view.pec import pec
from common.constants import logger, state, status, tasks


class PecAndDownloadEml(QObject):
    sentpec = pyqtSignal(str)
    downloadedeml = pyqtSignal(str)
    error = pyqtSignal(object)
    started = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

    def set_options(self, options):
        self.options = PecConfigController().options
        self.options["case_info"] = options["case_info"]
        self.options["acquisition_directory"] = options["acquisition_directory"]
        self.options["type"] = options["type"]

    def send(self):
        __status = status.SUCCESS

        self.pec_controller = PecController(
            self.options.get("pec_email"),
            self.options.get("password"),
            self.options.get("type"),
            self.options.get("case_info"),
            self.options.get("acquisition_directory"),
            self.options.get("smtp_server"),
            self.options.get("smtp_port"),
            self.options.get("imap_server"),
            self.options.get("imap_port"),
        )
        self.started.emit()
        try:
            self.pec_controller.send_pec()

        except Exception as e:
            __status = status.FAIL
            self.error.emit(
                {
                    "title": pec.LOGIN_FAILED,
                    "message": pec.SMTP_FAILED_MGS,
                    "details": str(e),
                }
            )

        self.sentpec.emit(__status)

    def download_eml(self):
        for i in range(self.options.get("retries")):
            __status = status.FAIL

            # whait for 8 seconds
            loop = QEventLoop()
            QTimer.singleShot(8000, loop.quit)
            loop.exec()

            try:
                if self.pec_controller.retrieve_eml():
                    __status = status.SUCCESS
                    break
            except Exception as e:
                self.error.emit(
                    {
                        "title": pec.LOGIN_FAILED,
                        "message": pec.IMAP_FAILED_MGS,
                        "details": str(e),
                    }
                )
                break

        self.downloadedeml.emit(__status)


class TaskPecAndDownloadEml(Task):
    def __init__(
        self, options, logger, table, progress_bar=None, status_bar=None, parent=None
    ):
        self.name = tasks.PEC_AND_DOWNLOAD_EML
        super().__init__(options, logger, table, progress_bar, status_bar, parent)

        self.pec_thread = QThread()
        self.pec = PecAndDownloadEml()
        self.pec.moveToThread(self.pec_thread)
        self.pec_thread.started.connect(self.pec.send)
        self.pec.started.connect(self.__started)
        self.pec.sentpec.connect(self.__is_pec_sent)
        self.pec.error.connect(self.__handle_error)
        self.pec.downloadedeml.connect(self.__is_eml_downloaded)
        self.dependencies = [tasks.REPORTFILE, tasks.TIMESTAMP]

    def start(self):
        self.pec.set_options(self.options)
        self.update_task(state.STARTED, status.PENDING)
        self.set_message_on_the_statusbar(logger.PEC_AND_DOWNLOAD_EML_STARTED)
        self.pec_thread.start()

    def __handle_error(self, error):
        error_dlg = ErrorView(
            QtWidgets.QMessageBox.Icon.Critical,
            error.get("title"),
            error.get("message"),
            error.get("details"),
        )
        error_dlg.exec()

    def __started(self):
        self.update_task(state.STARTED, status.COMPLETED)
        self.started.emit()

    def __is_pec_sent(self, __status):
        self.name = tasks.PEC
        self.table.add_task(self.name, state.FINISHED, status.COMPLETED, __status)
        self.logger.info(
            logger.PEC_SENT.format(self.pec.options.get("pec_email"), __status)
        )
        self.set_message_on_the_statusbar(
            logger.PEC_SENT.format(self.pec.options.get("pec_email"), __status)
        )
        self.upadate_progress_bar()

        if __status == status.SUCCESS:
            self.pec.download_eml()
        else:
            self.logger.info(logger.PEC_HAS_NOT_BEEN_SENT_CANNOT_DOWNLOAD_EML)
            self.__finished()

    def __is_eml_downloaded(self, __status):
        self.name = tasks.EML
        self.table.add_task(self.name, state.FINISHED, status.COMPLETED, __status)
        self.set_message_on_the_statusbar(logger.EML_DOWNLOAD.format(__status))
        self.upadate_progress_bar()
        self.__finished()

    def __finished(self):
        self.name = tasks.PEC_AND_DOWNLOAD_EML
        self.set_message_on_the_statusbar(logger.PEC_AND_DOWNLOAD_EML_COMPLETED)
        self.upadate_progress_bar()

        self.update_task(state.FINISHED, status.COMPLETED)

        self.finished.emit()

        self.pec_thread.quit()
        self.pec_thread.wait()

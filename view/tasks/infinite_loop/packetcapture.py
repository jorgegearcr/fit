#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######

import scapy.all as scapy
import os

from PyQt6.QtCore import QObject, QEventLoop, QTimer, pyqtSignal, QThread
from PyQt6.QtWidgets import QMessageBox
from common.constants.view.tasks import labels, state, status


from view.tasks.task import Task
from view.error import Error as ErrorView

from controller.configurations.tabs.packetcapture.packetcapture import (
    PacketCapture as PacketCaptureCotroller,
)

from common.constants import logger, details, error


class PacketCapture(QObject):
    finished = pyqtSignal()
    started = pyqtSignal()
    error = pyqtSignal(object)

    def __init__(self, parent=None):
        QObject.__init__(self, parent=parent)
        self.options = None
        self.output_file = None
        self.sniffer = scapy.AsyncSniffer()

    def set_options(self, options):
        self.output_file = os.path.join(
            options["acquisition_directory"], options["filename"]
        )

    def start(self):
        self.started.emit()
        try:
            self.sniffer.start()
        except Exception as e:
            self.error.emit(
                {
                    "title": labels.PACKET_CAPTURE,
                    "message": error.PACKET_CAPTURE,
                    "details": str(e),
                }
            )

    def stop(self):
        self.sniffer.stop()
        loop = QEventLoop()
        QTimer.singleShot(1000, loop.quit)
        loop.exec()
        scapy.wrpcap(self.output_file, self.sniffer.results)
        self.finished.emit()


class TaskPacketCapture(Task):
    def __init__(self, logger, progress_bar=None, status_bar=None, parent=None):
        super().__init__(logger, progress_bar, status_bar, parent)

        self.label = labels.PACKET_CAPTURE
        self.is_infinite_loop = True

        self.packetcapture_thread = QThread()
        self.packetcapture = PacketCapture()
        self.packetcapture.moveToThread(self.packetcapture_thread)

        self.packetcapture_thread.started.connect(self.packetcapture.start)

        self.packetcapture.started.connect(self.__started)
        self.packetcapture.finished.connect(self.__finished)
        self.packetcapture.error.connect(self.__handle_error)

    @Task.options.getter
    def options(self):
        return self._options

    @options.setter
    def options(self, options):
        folder = options["acquisition_directory"]
        options = PacketCaptureCotroller().options
        options["acquisition_directory"] = folder
        self._options = options

    def __handle_error(self, error):
        error_dlg = ErrorView(
            QMessageBox.Icon.Critical,
            error.get("title"),
            error.get("message"),
            error.get("details"),
        )
        error_dlg.exec()

    def start(self):
        self.update_task(state.STARTED, status.PENDING)
        self.set_message_on_the_statusbar(logger.NETWORK_PACKET_CAPTURE_STARTED)

        self.packetcapture.set_options(self.options)
        self.packetcapture_thread.start()

    def __started(self):
        self.update_task(
            state.STARTED,
            status.SUCCESS,
            details.NETWORK_PACKET_CAPTURE_STARTED,
        )

        self.logger.info(logger.NETWORK_PACKET_CAPTURE_STARTED)
        self.started.emit()

    def stop(self):
        self.update_task(state.STOPPED, status.PENDING)
        self.set_message_on_the_statusbar(logger.NETWORK_PACKET_CAPTURE_STOPPED)
        self.packetcapture.stop()

    def __finished(self):
        self.logger.info(logger.NETWORK_PACKET_CAPTURE_COMPLETED)
        self.set_message_on_the_statusbar(logger.NETWORK_PACKET_CAPTURE_COMPLETED)
        self.upadate_progress_bar()

        self.update_task(
            state.COMPLETED,
            status.SUCCESS,
            details.NETWORK_PACKET_CAPTURE_COMPLETED,
        )

        self.finished.emit()

        self.packetcapture_thread.quit()
        self.packetcapture_thread.wait()

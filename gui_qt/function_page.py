#!/usr/bin/env python
"""Shared Qt controls for video processing pages."""

import os

from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class TaskThread(QThread):
    status_changed = pyqtSignal(str, str)
    progress_changed = pyqtSignal(int)
    failed = pyqtSignal(str)

    def __init__(self, task, parent=None):
        super().__init__(parent)
        self.task = task

    def run(self):
        try:
            self.task(self.report_status, self.progress_changed.emit)
        except Exception as error:
            self.failed.emit(str(error))

    def report_status(self, text, color=""):
        self.status_changed.emit(text, color)


class FunctionPage(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self._task_thread = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(10)

        file_actions = QHBoxLayout()
        self.select_button = QPushButton("Select Files")
        self.select_button.clicked.connect(self.select_files)
        file_actions.addWidget(self.select_button)
        self.clear_button = QPushButton("Clear Files")
        self.clear_button.clicked.connect(self.clear_files)
        file_actions.addWidget(self.clear_button)
        file_actions.addStretch(1)
        layout.addLayout(file_actions)

        layout.addWidget(QLabel("Selected files"))
        self.listbox = QListWidget()
        self.listbox.setMinimumHeight(180)
        layout.addWidget(self.listbox, 1)

        output_row = QHBoxLayout()
        output_row.addWidget(QLabel("Output folder"))
        self.ent_folder = QLineEdit()
        self.ent_folder.setPlaceholderText("Choose an output folder")
        output_row.addWidget(self.ent_folder, 1)
        self.folder_button = QPushButton("Browse...")
        self.folder_button.clicked.connect(self.select_out_folder)
        output_row.addWidget(self.folder_button)
        layout.addLayout(output_row)

        self.button1 = QPushButton("Run")
        self.button1.clicked.connect(lambda checked=False: self.run_button1())
        self.button2 = QPushButton("Run")
        self.button2.clicked.connect(lambda checked=False: self.run_button2())
        process_actions = QHBoxLayout()
        process_actions.addWidget(self.button1)
        process_actions.addWidget(self.button2)
        process_actions.addStretch(1)
        layout.addLayout(process_actions)

        footer = QHBoxLayout()
        self.lbl_status = QLabel("")
        footer.addWidget(self.lbl_status, 1)
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setFixedWidth(180)
        footer.addWidget(self.progress)
        layout.addLayout(footer)

    def selected_files(self):
        return [self.listbox.item(index).text() for index in range(self.listbox.count())]

    def select_files(self):
        extensions = (
            "dat wmv 3g2 3gp 3gp2 3gpp amv asf avi bin cue divx dv flv gxf iso "
            "m1v m2v m2t m2ts m4v mkv mov mp2 mp2v mp4 mp4v mpa mpe mpeg mpeg1 "
            "mpeg2 mpeg4 mpg mpv2 mts nsv nuv ogg ogm ogv ogx ps rec rm rmvb tod "
            "ts tts vob vro webm"
        )
        patterns = " ".join(f"*.{extension}" for extension in extensions.split())
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select video files",
            "",
            f"Video files ({patterns});;All files (*)",
        )
        self.listbox.addItems(files)

    def select_out_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select output folder")
        if folder and os.path.isdir(folder):
            self.ent_folder.setText(folder)

    def clear_files(self):
        self.listbox.clear()

    def set_status_text(self, text, color=""):
        self.lbl_status.setText(text)
        color_map = {"red": "#b42318", "green": "#18794e"}
        self.lbl_status.setStyleSheet(f"color: {color_map.get(color, 'inherit')};")

    def start_task(self, initial_status, task):
        if self._task_thread is not None and self._task_thread.isRunning():
            return

        self.progress.setValue(0)
        self.set_status_text(initial_status)
        self.select_button.setEnabled(False)
        self.clear_button.setEnabled(False)
        self.listbox.setEnabled(False)
        self.ent_folder.setEnabled(False)
        self.folder_button.setEnabled(False)
        self.button1.setEnabled(False)
        self.button2.setEnabled(False)
        tabs = self.controller.centralWidget()
        if tabs is not None:
            tabs.setEnabled(False)

        self._task_thread = TaskThread(task, self)
        self._task_thread.status_changed.connect(self.set_status_text)
        self._task_thread.progress_changed.connect(self.progress.setValue)
        self._task_thread.failed.connect(self.show_task_error)
        self._task_thread.finished.connect(self.finish_task)
        self._task_thread.finished.connect(self._task_thread.deleteLater)
        self._task_thread.start()

    def show_task_error(self, message):
        self.set_status_text(f"Processing failed: {message}", "red")

    def finish_task(self):
        self.select_button.setEnabled(True)
        self.clear_button.setEnabled(True)
        self.listbox.setEnabled(True)
        self.ent_folder.setEnabled(True)
        self.folder_button.setEnabled(True)
        self.button1.setEnabled(True)
        self.button2.setEnabled(True)
        tabs = self.controller.centralWidget()
        if tabs is not None:
            tabs.setEnabled(True)
        self._task_thread = None

    def run_button1(self):
        pass

    def run_button2(self):
        pass
#!/usr/bin/env python
"""Subtitle generation and overlay page."""

import os

from PyQt6.QtWidgets import QApplication

import homevideo_tools
from gui_qt.function_page import FunctionPage


class SubtitlePage(FunctionPage):
    def __init__(self, controller):
        super().__init__(controller)
        self.button1.setText("Create Subtitles")
        self.button2.setText("Create and Overlay")

    def run_button1(self):
        files = self.selected_files()
        total = len(files)
        if total == 0:
            self.set_status_text("Select at least one video.", "red")
            return

        self.progress.setValue(0)
        self.set_status_text("Creating subtitles...")
        for index, file in enumerate(files):
            homevideo_tools.create_subtitles(file, self.controller.tsettings)
            self.progress.setValue(round((index + 1) / total * 100))
            self.set_status_text(f"{index + 1} of {total} complete")
            QApplication.processEvents()
        self.set_status_text("Finished.", "green")

    def run_button2(self):
        files = self.selected_files()
        output_folder = self.ent_folder.text()
        if not files:
            self.set_status_text("Select at least one video.", "red")
            return
        if not os.path.isdir(output_folder):
            output_folder = os.path.dirname(os.path.abspath(files[0]))
        if not os.path.isdir(output_folder):
            self.set_status_text("Choose an output folder.", "red")
            return

        total = len(files)
        self.progress.setValue(0)
        self.set_status_text("Creating subtitles and rendering video...")
        settings = self.controller.tsettings
        for index, file in enumerate(files):
            homevideo_tools.create_subtitles(file, settings)
            self.progress.setValue(round((index * 2 + 1) / (total * 2) * 100))
            QApplication.processEvents()
            homevideo_tools.write_subtitle_to_video(file, output_folder, settings)
            self.progress.setValue(round((index + 1) / total * 100))
            self.set_status_text(f"{index + 1} of {total} complete")
            QApplication.processEvents()
        self.set_status_text("Finished.", "green")
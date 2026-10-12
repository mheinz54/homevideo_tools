#!/usr/bin/env python
"""Video crossfade page."""

import os

from PyQt6.QtWidgets import QApplication

import homevideo_tools
from gui_qt.function_page import FunctionPage


class MergePage(FunctionPage):
    def __init__(self, controller):
        super().__init__(controller)
        self.button1.setText("Merge Videos")
        self.button2.hide()

    def run_button1(self):
        files = self.selected_files()
        output_folder = self.ent_folder.text()
        if len(files) < 2:
            self.set_status_text("Select at least two videos.", "red")
            return
        if not os.path.isdir(output_folder):
            output_folder = os.path.dirname(os.path.abspath(files[0]))
        if not os.path.isdir(output_folder):
            self.set_status_text("Choose an output folder.", "red")
            return

        self.progress.setValue(0)
        self.set_status_text("Merging videos...")
        QApplication.processEvents()
        homevideo_tools.crossfade_multiple(
            files,
            output_folder,
            self.controller.tsettings,
        )
        self.progress.setValue(100)
        self.set_status_text("Finished.", "green")
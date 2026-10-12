#!/usr/bin/env python
"""Subtitle generation and overlay page."""

import os

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

        settings = self.controller.tsettings

        def create_subtitle_task(set_status, set_progress):
            for index, file in enumerate(files):
                set_status(f"Creating subtitles: {index + 1} of {total}")
                homevideo_tools.create_subtitles(file, settings)
                set_progress(round((index + 1) / total * 100))
            set_status("Finished.", "green")

        self.start_task("Creating subtitles...", create_subtitle_task)

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
        settings = self.controller.tsettings

        def overlay_task(set_status, set_progress):
            for index, file in enumerate(files):
                set_status(f"Creating subtitles: {index + 1} of {total}")
                homevideo_tools.create_subtitles(file, settings)
                set_progress(round((index * 2 + 1) / (total * 2) * 100))
                set_status(f"Rendering video: {index + 1} of {total}")
                homevideo_tools.write_subtitle_to_video(file, output_folder, settings)
                set_progress(round((index + 1) / total * 100))
            set_status("Finished.", "green")

        self.start_task("Preparing subtitle overlay...", overlay_task)
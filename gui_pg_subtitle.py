#!/usr/bin/env python
""" subtitle page for the tool gui
"""

import os
import tkinter as tk
import gui_pg_function as gui_pg
import homevideo_tools

class SubtitlePage(gui_pg.FunctionPage):

    def __init__(self, parent, controller):
        gui_pg.FunctionPage.__init__(self, parent, controller)

        self.button1.configure(text = "Subtitles\nOnly", command = self.run_subtitles)
        self.button2.configure(text = "Subtitles\n+ Overlay", command = self.run_sub_overlay)


    def run_subtitles(self):
        self.progress['value'] = 0
        settings = self.controller.tsettings
        total = self.listbox.size()
        if total == 0:
            self.set_status_text("need to select files", "red")
            return

        self.set_status_text("running", "green")

        for i, f in enumerate(self.listbox.get(0, tk.END)):
            homevideo_tools.create_subtitles(f, settings)
            self.progress['value'] = (i + 1) / total * 100
            self.controller.window.update_idletasks()
        self.set_status_text("finished", "green")


    def run_sub_overlay(self):
        self.progress['value'] = 0
        settings = self.controller.tsettings
        total = self.listbox.size() * 2
        if total == 0:
            self.set_status_text("need to select files", "red")
            return

        self.set_status_text("running", "green")

        outpath = self.ent_folder.get()
        if os.path.isdir(outpath):
            for i, f in enumerate(self.listbox.get(0, tk.END)):
                homevideo_tools.create_subtitles(f, settings)
                self.progress['value'] = (i * 2 + 1) / total * 100
                self.controller.window.update_idletasks()

                homevideo_tools.write_subtitle_to_video(f, outpath, settings)
                self.progress['value'] = ((i + 1) * 2) / total * 100
                self.controller.window.update_idletasks()
            self.set_status_text("finished", "green")
        else:
            self.set_status_text("need to set folder", "red")
#!/usr/bin/env python
""" merge page for the tool gui
"""

import os
import tkinter as tk
import homevideo_tools
import gui_pg_function as gui_pg

class MergePage(gui_pg.FunctionPage):

    def __init__(self, parent, controller):
        gui_pg.FunctionPage.__init__(self, parent, controller)

        self.button1.configure(text = "Merge", command = self.run_merge)
        self.button2.grid_forget()


    def run_merge(self):
        print("run merge")
        self.progress['value'] = 0
        settings = self.controller.tsettings
        total = self.listbox.size()
        if total == 0:
            self.set_status_text("need to select files", "red")
            return

        self.set_status_text("running", "green")

        outpath = self.ent_folder.get()
        if os.path.isdir(outpath):
            for i, f in enumerate(self.listbox.get(0, tk.END)):
                #homevideo_tools.create_subtitles(f, settings)
                self.progress['value'] = (i + 1) / total * 100
                self.controller.window.update_idletasks()
            self.set_status_text("finished", "green")
        else:
            self.set_status_text("need to set folder", "red")
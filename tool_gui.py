#!/usr/bin/env python
""" gui to interact with homevideo_tools.py
"""

import tkinter as tk
import tool_settings
from gui_pg_subtitle import * 
from gui_pg_merge import * 
from gui_pg_settings import * 

class ToolsGui:

    def __init__(self, window):
        self.tsettings = tool_settings.ToolSettings()
        self.window = window

        window.title("Homevideo Tools")
        window.minsize(height=335, width=150) 

        frame_options = tk.Frame(master=window, height=50)
        frame_options.pack(fill=tk.X, side=tk.TOP, expand=False)
        frame_options.columnconfigure([0, 1, 2], weight=1)

        self.btn_subtitle = tk.Button(
            master=frame_options, 
            text="Subtitles", 
            width=30,
            command=self.btn_click_subtitle_page,
            relief="sunken"
            )
        self.btn_subtitle.grid(row=0, column=0, padx=5, pady=2, sticky="nwes")

        self.btn_merge = tk.Button(
            master=frame_options, 
            text="Merge", 
            width=30,
            command=self.btn_click_merge_page,
            relief="raised"
            )
        self.btn_merge.grid(row=0, column=1, padx=5, pady=2, sticky="nwes")

        self.btn_settings = tk.Button(
            master=frame_options, 
            text="Settings", 
            width=30,
            command=self.btn_click_settings_page,
            relief="raised"
            )
        self.btn_settings.grid(row=0, column=2, padx=5, pady=2, sticky="nwes")

        # main frame 
        self.frame_main = tk.Frame(master=window, height=100)
        self.frame_main.pack(fill=tk.BOTH, side=tk.TOP, expand=True)
        self.frame_main.grid_rowconfigure(0, weight=1)
        self.frame_main.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (SubtitlePage, MergePage, SettingsPage):
            frame = F(parent=self.frame_main, controller=self)
            self.frames[F.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("SubtitlePage")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()

    def toggle_buttons(self, button):
        if button == "subtitle":
            self.btn_subtitle.config(relief="sunken")
            self.btn_merge.config(relief="raised")
            self.btn_settings.config(relief="raised")
        elif button == "merge":
            self.btn_subtitle.config(relief="raised")
            self.btn_merge.config(relief="sunken")
            self.btn_settings.config(relief="raised")
        else:
            self.btn_subtitle.config(relief="raised")
            self.btn_merge.config(relief="raised")
            self.btn_settings.config(relief="sunken")

    def btn_click_subtitle_page(self):
        if self.btn_subtitle.config("relief")[-1] == "raised":
            self.toggle_buttons("subtitle")
            self.show_frame("SubtitlePage")

    def btn_click_merge_page(self):
        if self.btn_merge.config("relief")[-1] == "raised":
            self.toggle_buttons("merge")
            self.show_frame("MergePage")

    def btn_click_settings_page(self):
        if self.btn_settings.config("relief")[-1] == "raised":
            self.toggle_buttons("settings")
            self.show_frame("SettingsPage")
#end ToolsGui class

if __name__ == "__main__":
    window = tk.Tk()
    ToolsGui(window)
    window.mainloop()
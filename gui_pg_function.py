#!/usr/bin/env python
""" template page for the tool gui
    inherit from this class and set button text and functions
"""

import os
import tkinter as tk
from tkinter.filedialog import askopenfilenames
from tkinter import ttk

class FunctionPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        self.columnconfigure([0, 1, 3], weight=0)
        self.columnconfigure(2, weight=1)
        self.grid_rowconfigure([0, 1, 2, 3, 4, 5, 6, 7], weight=0)

        tk.Button(
            master=self, 
            text="Select Files", 
            width=15,
            command=self.select_files,
            ).grid(row=1, column=0, padx=2, pady=5, sticky="nwes")

        tk.Button(
            master=self, 
            text="Clear Files", 
            width=15,
            command=self.clear_files,
            ).grid(row=2, column=0, padx=2, pady=5, sticky="nwes")

        self.button1 = tk.Button(
            master=self, 
            text="button1", 
            width=15,
            command=self.run_button1)
        self.button1.grid(row=3, column=0, padx=2, pady=5, sticky="nwes")

        self.button2 = tk.Button(
            master=self, 
            text="button2", 
            width=15,
            command=self.run_button2)
        self.button2.grid(row=4, column=0, padx=2, pady=5, sticky="nwes")

        self.status_text = tk.StringVar()
        self.lbl_status = tk.Label(master=self, textvariable=self.status_text)
        self.lbl_status.grid(row=6, column=0, padx=5)

        tk.Label(
            master=self, 
            text="Selected Files:",
            ).grid(row=0, column=1, padx=5, columnspan=2, sticky="sw")

        self.listbox = tk.Listbox(
            master=self, 
            width=75, 
            height=12,
            borderwidth=2,
            relief=tk.RIDGE)
        self.listbox.grid(row=1, column=1, padx=5, pady=5, rowspan=4, columnspan=2, sticky="nwes")

        scroll = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.listbox.yview)
        scroll.grid(column=3, row=1, rowspan=4, sticky="ns")
        self.listbox['yscrollcommand'] = scroll.set

        tk.Label(
            master=self, 
            text="Output Folder:"
            ).grid(row=5, column=1, padx=5, columnspan=2, sticky="nw")

        tk.Button(
            master=self, 
            text="Folder", 
            width=10,
            command=self.select_out_folder,
            ).grid(row=6, column=1, padx=2, sticky="nw")

        self.ent_folder = tk.Entry(master=self, width=75)
        self.ent_folder.grid(row=6, column=2, padx=5, pady=(2,5), sticky="nwes")

        self.progress = ttk.Progressbar(
            master=self, 
            orient = tk.HORIZONTAL, 
            length = 100, 
            mode = 'determinate')
        self.progress.grid(row=7, column=0, columnspan=4, padx=5, pady=5, sticky="nwes")
    # end _init__

    def select_files(self):
        formats = ".dat .wmv .3g2 .3gp .3gp2 .3gpp .amv .asf .avi .bin .cue .divx .dv .flv .gxf .iso .m1v .m2v .m2t .m2ts .m4v" \
                  + " .mkv .mov .mp2 .mp2v .mp4 .mp4v .mpa .mpe .mpeg .mpeg1 .mpeg2 .mpeg4 .mpg .mpv2 .mts .nsv .nuv .ogg .ogm" \
                  + " .ogv .ogx .ps .rec .rm .rmvb .tod .ts .tts .vob .vro .webm"

        files = tk.filedialog.askopenfilenames(filetypes=[("All Videos Files", formats)])
        for f in files:
            self.listbox.insert(tk.END, f)

    def select_out_folder(self):
        folder = tk.filedialog.askdirectory()
        if os.path.isdir(folder):
            self.ent_folder.delete(0, tk.END)
            self.ent_folder.insert(0, folder)

    def clear_files(self):
        self.listbox.delete(0,tk.END)

    def set_status_text(self, text, color):
        self.status_text.set(text)
        self.lbl_status.config(fg=color)

    def run_button1(self):
        print("button 1")

    def run_button2(self):
        print("button 2")
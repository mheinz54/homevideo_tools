#!/usr/bin/env python
""" settings page for the tool gui
"""

import tkinter as tk

class SettingsPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        tk.Label(self, text="This is the settings page").pack(fill=tk.BOTH, side=tk.TOP)
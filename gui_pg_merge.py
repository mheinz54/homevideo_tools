#!/usr/bin/env python
""" merge page for the tool gui
"""

import tkinter as tk

class MergePage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        tk.Label(self, text="This is the merge page").pack(fill=tk.BOTH, side=tk.TOP)
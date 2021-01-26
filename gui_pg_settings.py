#!/usr/bin/env python
""" settings page for the tool gui
"""

import re
import tkinter as tk
from tkinter import ttk, colorchooser
from ttkwidgets.color import askcolor, functions
from PIL import ImageTk
import tool_settings

class SettingsPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        settings = self.controller.tsettings

        self.columnconfigure([0, 1, 2, 3], weight=0)
        self.grid_rowconfigure([0, 1, 2, 3, 4], weight=0)

        current_row = 0

        tk.Label(
            master=self,
            text="Subtitle Settings"
        ).grid(row=current_row, column=0, columnspan=2, padx=(20, 5), pady=(15, 5), sticky="nwes")

        current_row += 1

        # font button
        tk.Button(
            master=self, 
            text="Font...",
            command=self.invoke_font_diag,
            width=15
            ).grid(row=current_row, column=0, padx=(20, 5), pady=5, sticky="nwes")

        # font display
        self.font_text = tk.StringVar()
        tk.Label(
            master=self, 
            textvariable=self.font_text,
            borderwidth=2,
            relief=tk.RIDGE,
            justify="left",
            width=25
            ).grid(row=current_row, column=1, padx=5, pady=5, sticky="nwes")
        self.set_font_label(settings)

        current_row += 1

        # Font Color Button
        tk.Button(
            master=self, 
            text="Font Color",
            command=self.set_primary_color,
            width=15
            ).grid(row=current_row, column=0, padx=(20, 5), pady=5, sticky="nwes")

        # font color preview
        self.transparent_bg = functions.create_checkered_image(200, 32)
        color = Color(settings.primary_color, Color.iABGR)
        overlay = functions.overlay(self.transparent_bg, color.color_vls(Color.RGBA))
        self.im_color_prime = ImageTk.PhotoImage(overlay, master=self)
        self.lbl_primary = tk.Label(
            master=self,
            image=self.im_color_prime)
        self.lbl_primary.grid(row=current_row, column=1, padx=5, pady=5, sticky="nwes")

        current_row += 1

        # Font Outline Color Button
        tk.Button(
            master=self, 
            text="Outline Color",
            command=self.set_outline_color,
            width=15
            ).grid(row=current_row, column=0, padx=(20, 5), pady=5, sticky="nwes")

        # font outline color preview
        color = Color(settings.outline_color, Color.iABGR)
        overlay = functions.overlay(self.transparent_bg, color.color_vls(Color.RGBA))
        self.im_color_outline = ImageTk.PhotoImage(overlay, master=self)
        self.lbl_outline = tk.Label(
            master=self,
            image=self.im_color_outline)
        self.lbl_outline.grid(row=current_row, column=1, padx=5, pady=5, sticky="nwes")

        current_row += 1

        tk.Label(
            master=self,
            text="Alignment\nin Video:"
        ).grid(row=current_row, column=0, padx=(20, 5), pady=5, sticky="nwes")

        # alignment combobox
        self.cmbx_alignment = ttk.Combobox(
            master=self, 
            values=['Left', 'Center', 'Right'])
        self.cmbx_alignment.grid(row=current_row, column=1, padx=5, pady=5, sticky="nwes")
        self.cmbx_alignment.state(["readonly"])
        self.cmbx_alignment.current(settings.alignment - 1)
        self.cmbx_alignment.bind('<<ComboboxSelected>>', self.alignment_changed)

        current_row += 1

        # check box to include seconds in timestamp
        self.chk_timestamp_var = tk.IntVar(value=settings.include_seconds)
        tk.Checkbutton(
            master=self,
            text="Include seconds\nin timestamp",
            variable=self.chk_timestamp_var,
            command=self.timestamp_changed
        ).grid(row=current_row, column=0, padx=(20, 5), pady=5, sticky="news")

        # exmpale text display
        self.example_text = tk.StringVar()
        self.lbl_example = tk.Label(
            master=self, 
            textvariable=self.example_text,
            borderwidth=2,
            relief=tk.RIDGE,
            justify="left")
        self.lbl_example.grid(row=current_row, column=1, rowspan=2, padx=5, pady=5, sticky="nwes")
        self.set_example_label(settings)

        current_row += 1

        # check box to use 24 hour format
        self.chk_24_var = tk.IntVar(value=settings.use_24hour_format)
        tk.Checkbutton(
            master=self,
            text="Use 24 hour\nFormat",
            variable=self.chk_24_var,
            command=self.hour_format_changed
        ).grid(row=current_row, column=0, padx=(20, 5), pady=5, sticky="news")
    # ----------------------- end of __init__ -----------------------

    def invoke_font_diag(self):
        settings = self.controller.tsettings
        root = self.controller.window
        font = "{" + settings.font + "} " + str(settings.font_size)
        root.tk.call(
            'tk', 'fontchooser', 
            'configure', '-font', font, 
            '-command', root.register(self.font_changed))
        root.tk.call('tk', 'fontchooser', 'show')

    def font_changed(self, font):
        settings = self.controller.tsettings
        if font[0] == "{":
            font_options = re.split("\{|\}", font)
            settings.font = font_options[1]
            font_options = "".join(font_options[2:]).split(' ')
        else:
            font_options = font.split(' ')
            settings.font = font_options[0]
        settings.font_size = int(font_options[1])

        self.set_font_label(settings)
        self.set_example_label(settings)

    def set_font_label(self, settings):
        #self.lbl_font.config(font=font)
        self.font_text.set("font: {}\nsize: {}".format(settings.font, settings.font_size))

    def set_primary_color(self):
        settings = self.controller.tsettings
        selected_color = askcolor(
            color=Color(settings.primary_color, Color.iABGR).color_str(Color.RGBA, True),
            alpha=True)

        if selected_color[1] != None:
            color = Color(selected_color[1], Color.RGBA)
            ovrly = functions.overlay(self.transparent_bg, color.color_vls(Color.RGBA))
            self.im_color_prime = ImageTk.PhotoImage(ovrly, master=self)
            self.lbl_primary.configure(image=self.im_color_prime)
            settings.primary_color = color.color_str(Color.iABGR, False)
        self.set_example_label(settings)

    def set_outline_color(self):
        settings = self.controller.tsettings
        selected_color = askcolor(
            color=Color(settings.outline_color, Color.iABGR).color_str(Color.RGBA, True),
            alpha=True)

        if selected_color[1] != None:
            color = Color(selected_color[1], Color.RGBA)
            ovrly = functions.overlay(self.transparent_bg, color.color_vls(Color.RGBA))
            self.im_color_outline = ImageTk.PhotoImage(ovrly, master=self)
            self.lbl_outline.configure(image=self.im_color_outline)
            settings.outline_color = color.color_str(Color.iABGR, False)
        self.set_example_label(settings)

    def alignment_changed(self, event):
        settings = self.controller.tsettings
        settings.alignment = self.cmbx_alignment.current() + 1
        self.set_example_label(settings)

    def timestamp_changed(self):
        settings = self.controller.tsettings
        settings.include_seconds = self.chk_timestamp_var.get()
        self.set_example_label(settings)

    def hour_format_changed(self):
        settings = self.controller.tsettings
        settings.use_24hour_format = self.chk_24_var.get()
        self.set_example_label(settings)

    def set_example_label(self, settings):
        sec = ":00" if settings.include_seconds else ""
        if settings.use_24hour_format:
            self.example_text.set("20:00" + sec + "\nJan 1 1970")
        else:
            self.example_text.set("08:00" + sec + " PM\nJan 1 1970")
        if settings.alignment == 1:
            a = tk.W
        elif settings.alignment == 2:
            a = tk.CENTER
        else:
            a = tk.E
        self.lbl_example.config(
            font=(settings.font, settings.font_size),
            fg=Color(settings.primary_color, Color.iABGR).color_str(Color.RGB, True),
            bg=Color(settings.outline_color, Color.iABGR).color_str(Color.RGB, True),
            anchor=a
        )

class Color:
    RGB = 1
    BGR = 2
    RGBA = 3
    ABGR = 4
    iABGR = 5

    # Alpha FF fully opaque, 00 fully transparent
    # iAlpha 00 fully opaque, FF fully transparent
    def __init__(self, color, format):
        color = str(color).strip('#')
        if format == self.RGB or format == self.BGR:
            assert len(color) == 6, "RGB/BGR should have length of 6"
        else:
            assert len(color) == 8, "RGBA/ABGR should have length of 8"

        if format == self.RGB or format == self.BGR:
            self.a = "FF"
            self.r = color[0:2] if format == self.RGB else color[4:6]
            self.g = color[2:4]
            self.b = color[4:6] if format == self.RGB else color[0:2]
        else:
            self.r = color[0:2] if format == self.RGBA else color[6:8]
            self.g = color[2:4] if format == self.RGBA else color[4:6]
            self.b = color[4:6] if format == self.RGBA else color[2:4]
            self.a = color[6:8] if format == self.RGBA else color[0:2]

        if format == self.iABGR:
            h = int(self.a, 16)
            self.ia = self.a
            self.a = hex(int("FF", 16) - h)[2:]
            if len(self.a) == 1:
                self.a = "0" + self.a
        else:
            h = int(self.a, 16)
            self.ia = hex(int("FF", 16) - h)[2:]
            if len(self.ia) == 1:
                self.ia = "0" + self.ia

    def color_vls(self, format):
        r_v = int(self.r, 16)
        g_v = int(self.g, 16)
        b_v = int(self.b, 16)
        a_v = int(self.a, 16)
        ia_v = int(self.ia, 16)

        if format == self.RGB:
            return r_v, g_v, b_v
        elif format == self.BGR:
            return b_v, g_v, r_v
        elif format == self.ABGR:
            return a_v, b_v, g_v, r_v
        elif format == self.iABGR:
            return ia_v, b_v, g_v, r_v
        else:
            return r_v, g_v, b_v, a_v

    def color_str(self, format, use_hash):
        h = "#" if use_hash else ""
        if format == self.RGB:
            return h + self.r + self.g + self.b
        elif format == self.BGR:
            return h + self.b + self.g + self.r
        elif format == self.ABGR:
            return h + self.a + self.b + self.g + self.r
        elif format == self.iABGR:
            return h + self.ia + self.b + self.g + self.r
        else:
            return h + self.r + self.g + self.b + self.a



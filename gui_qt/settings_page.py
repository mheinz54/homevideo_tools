#!/usr/bin/env python
"""Subtitle settings page using native Qt controls."""

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtWidgets import (
    QCheckBox,
    QColorDialog,
    QComboBox,
    QFontDialog,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class SettingsPage(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        settings = controller.tsettings

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        heading = QLabel("Subtitle Settings")
        heading.setStyleSheet("font-size: 18px; font-weight: 600;")
        layout.addWidget(heading)

        form = QFormLayout()
        form.setHorizontalSpacing(18)
        form.setVerticalSpacing(12)

        font_row = QHBoxLayout()
        self.font_button = QPushButton("Choose font...")
        self.font_button.clicked.connect(self.invoke_font_dialog)
        font_row.addWidget(self.font_button)
        self.font_text = QLabel()
        font_row.addWidget(self.font_text, 1)
        form.addRow("Font", font_row)

        primary_row, self.lbl_primary = self._color_row(
            "Choose text color...", self.set_primary_color
        )
        form.addRow("Text color", primary_row)

        outline_row, self.lbl_outline = self._color_row(
            "Choose outline color...", self.set_outline_color
        )
        form.addRow("Outline color", outline_row)

        self.cmbx_alignment = QComboBox()
        self.cmbx_alignment.addItems(["Left", "Center", "Right"])
        self.cmbx_alignment.setCurrentIndex(settings.alignment - 1)
        self.cmbx_alignment.currentIndexChanged.connect(self.alignment_changed)
        form.addRow("Video alignment", self.cmbx_alignment)
        layout.addLayout(form)

        self.chk_timestamp_var = QCheckBox("Include seconds in timestamp")
        self.chk_timestamp_var.setChecked(settings.include_seconds)
        self.chk_timestamp_var.toggled.connect(self.timestamp_changed)
        layout.addWidget(self.chk_timestamp_var)

        self.chk_24_var = QCheckBox("Use 24-hour time")
        self.chk_24_var.setChecked(settings.use_24hour_format)
        self.chk_24_var.toggled.connect(self.hour_format_changed)
        layout.addWidget(self.chk_24_var)

        self.chk_yadif = QCheckBox("Use camcorder deinterlacing (yadif)")
        self.chk_yadif.setChecked(settings.camcorder_yadif_filter)
        self.chk_yadif.toggled.connect(self.yadif_filter_changed)
        layout.addWidget(self.chk_yadif)

        self.lbl_example = QLabel()
        self.lbl_example.setFrameShape(QFrame.Shape.StyledPanel)
        self.lbl_example.setMinimumHeight(58)
        self.lbl_example.setMargin(10)
        layout.addWidget(self.lbl_example)

        bottom = QHBoxLayout()
        self.save_status = QLabel("Changes apply immediately.")
        bottom.addWidget(self.save_status, 1)
        save_button = QPushButton("Save Settings")
        save_button.clicked.connect(self.save_settings)
        bottom.addWidget(save_button)
        layout.addLayout(bottom)
        layout.addStretch(1)

        self.set_font_label(settings)
        self.set_color_preview(self.lbl_primary, self._setting_to_qcolor(settings.primary_color))
        self.set_color_preview(self.lbl_outline, self._setting_to_qcolor(settings.outline_color))
        self.set_example_label(settings)

    def _color_row(self, button_text, callback):
        row = QHBoxLayout()
        button = QPushButton(button_text)
        button.clicked.connect(callback)
        row.addWidget(button)
        preview = QLabel()
        preview.setFixedSize(96, 30)
        preview.setFrameShape(QFrame.Shape.StyledPanel)
        row.addWidget(preview)
        row.addStretch(1)
        return row, preview

    @staticmethod
    def _setting_to_qcolor(value):
        value = value.strip().lstrip("#")
        alpha = 255 - int(value[0:2], 16)
        blue = int(value[2:4], 16)
        green = int(value[4:6], 16)
        red = int(value[6:8], 16)
        return QColor(red, green, blue, alpha)

    @staticmethod
    def _qcolor_to_setting(color):
        return "{:02X}{:02X}{:02X}{:02X}".format(
            255 - color.alpha(), color.blue(), color.green(), color.red()
        )

    @staticmethod
    def set_color_preview(label, color):
        label.setStyleSheet(
            "background-color: rgba({}, {}, {}, {});".format(
                color.red(), color.green(), color.blue(), color.alpha()
            )
        )

    def save_settings(self):
        self.controller.tsettings.save_settings()
        self.save_status.setText("Settings saved.")

    def invoke_font_dialog(self):
        settings = self.controller.tsettings
        initial_font = QFont(settings.font, settings.font_size)
        font, accepted = QFontDialog.getFont(initial_font, self, "Subtitle font")
        if accepted:
            settings.font = font.family()
            settings.font_size = max(font.pointSize(), 1)
            self.set_font_label(settings)
            self.set_example_label(settings)

    def set_font_label(self, settings):
        self.font_text.setText(f"{settings.font}, {settings.font_size} pt")

    def set_primary_color(self):
        settings = self.controller.tsettings
        color = QColorDialog.getColor(
            self._setting_to_qcolor(settings.primary_color),
            self,
            "Subtitle text color",
            QColorDialog.ColorDialogOption.ShowAlphaChannel,
        )
        if color.isValid():
            settings.primary_color = self._qcolor_to_setting(color)
            self.set_color_preview(self.lbl_primary, color)
            self.set_example_label(settings)

    def set_outline_color(self):
        settings = self.controller.tsettings
        color = QColorDialog.getColor(
            self._setting_to_qcolor(settings.outline_color),
            self,
            "Subtitle outline color",
            QColorDialog.ColorDialogOption.ShowAlphaChannel,
        )
        if color.isValid():
            settings.outline_color = self._qcolor_to_setting(color)
            self.set_color_preview(self.lbl_outline, color)
            self.set_example_label(settings)

    def alignment_changed(self, index):
        self.controller.tsettings.alignment = index + 1
        self.set_example_label(self.controller.tsettings)

    def timestamp_changed(self, checked):
        self.controller.tsettings.include_seconds = checked
        self.set_example_label(self.controller.tsettings)

    def hour_format_changed(self, checked):
        self.controller.tsettings.use_24hour_format = checked
        self.set_example_label(self.controller.tsettings)

    def yadif_filter_changed(self, checked):
        self.controller.tsettings.camcorder_yadif_filter = checked
        self.set_example_label(self.controller.tsettings)

    def set_example_label(self, settings):
        seconds = ":00" if settings.include_seconds else ""
        if settings.use_24hour_format:
            text = "20:00" + seconds + "\nJan 1 1970"
        else:
            text = "08:00" + seconds + " PM\nJan 1 1970"
        alignment = {
            1: Qt.AlignmentFlag.AlignLeft,
            2: Qt.AlignmentFlag.AlignHCenter,
            3: Qt.AlignmentFlag.AlignRight,
        }[settings.alignment]
        self.lbl_example.setText(text)
        self.lbl_example.setAlignment(alignment | Qt.AlignmentFlag.AlignVCenter)
        self.lbl_example.setFont(QFont(settings.font, settings.font_size))
        primary = self._setting_to_qcolor(settings.primary_color)
        outline = self._setting_to_qcolor(settings.outline_color)
        self.lbl_example.setStyleSheet(
            "color: rgba({}, {}, {}, {}); background-color: rgba({}, {}, {}, {});".format(
                primary.red(), primary.green(), primary.blue(), primary.alpha(),
                outline.red(), outline.green(), outline.blue(), outline.alpha(),
            )
        )
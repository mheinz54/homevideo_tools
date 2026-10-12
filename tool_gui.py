#!/usr/bin/env python
"""Qt GUI entry point."""

import sys

from PyQt6.QtWidgets import QApplication, QMainWindow, QTabWidget

from gui_qt import MergePage, SettingsPage, SubtitlePage
import tool_settings


class ToolsGui(QMainWindow):
    def __init__(self):
        super().__init__()
        self.tsettings = tool_settings.ToolSettings()
        self.setWindowTitle("Homevideo Tools")

        screen = QApplication.primaryScreen()
        if screen is None:
            self.setMinimumSize(760, 500)
            self.resize(960, 640)
        else:
            available = screen.availableGeometry()
            width = min(960, available.width())
            height = min(640, available.height())
            self.setMinimumSize(min(760, width), min(500, height))
            self.resize(width, height)
            frame = self.frameGeometry()
            frame.moveCenter(available.center())
            self.move(frame.topLeft())

        tabs = QTabWidget()
        tabs.setDocumentMode(True)
        tabs.addTab(SubtitlePage(self), "Subtitles")
        tabs.addTab(MergePage(self), "Merge")
        tabs.addTab(SettingsPage(self), "Settings")
        self.setCentralWidget(tabs)


def main():
    app = QApplication(sys.argv)
    window = ToolsGui()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
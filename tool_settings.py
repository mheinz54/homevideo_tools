#!/usr/bin/env python
""" read and write to settings ini file
"""

import configparser
import re

# SETTINGS
INI_SEC_SUBTITLES = "SUBTITLES"
INI_INCLUDE_SECONDS = "include_seconds"
INI_ALIGNMENT = "alignment"
INI_PRIMARY_COLOR = "primary_color"
INI_OUTLINE_COLOR = "outline_color"
INI_FONT_SIZE = "font_size"
INI_FONT = "font"
INI_DELETE_AFTER_IMPRINT = "delete_after_imprint"
INI_SEC_CROSSFADE = "CROSSFADE"
INI_DURATION = "durration"
INI_SEC_TESTING = "TESTING"
INI_IN_TEST = "in_test"

SETTINGS_FILE = 'settings.ini'

class ToolSettings:
    def __init__(self):
        self.__config = configparser.ConfigParser()
        self.__config.read(SETTINGS_FILE)
        self.__sub_settings = self.__config[INI_SEC_SUBTITLES]
        self.__test_settings = self.__config[INI_SEC_TESTING]

    def __boolean_value(self, value):
        accepted_values = ['yes', 'no', 'on', 'off', 'true', 'false', '1', '0']
        x = str(value).lower()
        if x in accepted_values:
            return x
        else:
            raise ValueError("not one of 'yes'/'no', 'on'/'off', 'true'/'false', or '1'/'0'")

    def __int_value(self, value):
        if isinstance(value, int):
            return str(value)
        else:
            raise ValueError("value is not an int")

    def __color_value(self, value):
        if re.compile("[A-F0-9]{8}").match(value) is not None:
            return value
        else:
            raise ValueError("value is not a color, ABGR 8 characters hex")

    def save_settings(self):
        with open(SETTINGS_FILE, 'w') as f:
            self.__config.write(f)

    # in_test getter/setter
    @property
    def in_test(self):
        return self.__test_settings.getboolean(INI_IN_TEST)

    @in_test.setter
    def in_test(self, value):
        self.__config.set(INI_SEC_TESTING, INI_IN_TEST, self.__boolean_value(value))

    # include_seconds getter/setter
    @property
    def include_seconds(self):
        return self.__sub_settings.getboolean(INI_INCLUDE_SECONDS)

    @include_seconds.setter
    def include_seconds(self, value):
        self.__config.set(INI_SEC_SUBTITLES, INI_INCLUDE_SECONDS, self.__boolean_value(value))

    # alignment getter/setter
    @property
    def alignment(self):
        return self.__sub_settings.getint(INI_ALIGNMENT)

    @alignment.setter
    def alignment(self, value):
        self.__config.set(INI_SEC_SUBTITLES, INI_ALIGNMENT, self.__int_value(value))

    # primary_color getter/setter
    @property
    def primary_color(self):
        return self.__sub_settings.get(INI_PRIMARY_COLOR)

    @primary_color.setter
    def primary_color(self, value):
        self.__config.set(INI_SEC_SUBTITLES, INI_PRIMARY_COLOR, self.__color_value(value))

    # outline_color getter/setter
    @property
    def outline_color(self):
        return self.__sub_settings.get(INI_OUTLINE_COLOR)

    @outline_color.setter
    def outline_color(self, value):
        self.__config.set(INI_SEC_SUBTITLES, INI_OUTLINE_COLOR, self.__color_value(value))

    # font_size getter/setter
    @property
    def font_size(self):
        return self.__sub_settings.getint(INI_FONT_SIZE)

    @font_size.setter
    def font_size(self, value):
        self.__config.set(INI_SEC_SUBTITLES, INI_FONT_SIZE, self.__int_value(value))

    # font getter/setter
    @property
    def font(self):
        return self.__sub_settings.get(INI_FONT)

    @font.setter
    def delete_after_imprint(self, value):
        self.__config.set(INI_SEC_SUBTITLES, INI_FONT, value)

    # delete_after_imprint getter/setter
    @property
    def delete_after_imprint(self):
        return self.__sub_settings.getboolean(INI_DELETE_AFTER_IMPRINT)

    @delete_after_imprint.setter
    def delete_after_imprint(self, value):
        self.__config.set(INI_SEC_SUBTITLES, INI_DELETE_AFTER_IMPRINT, self.__boolean_value(value))

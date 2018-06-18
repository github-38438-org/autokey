# Copyright (C) 2011 Chris Dekter
# Copyright (C) 2018 Thomas Hess <thomas.hess@udo.edu>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import logging

from .. import common
from ..common import inherits_from_ui_file_with_name

from ... import iomediator
from ... import model
from ...iomediator.key import Key

logger = common.logger.getChild("Hotkey Settings Dialog")  # type: logging.Logger


class HotkeySettingsDialog(*inherits_from_ui_file_with_name("hotkeysettings")):

    KEY_MAP = {
               ' ': "<space>",
               }

    REVERSE_KEY_MAP = {}
    for key, value in KEY_MAP.items():
        REVERSE_KEY_MAP[value] = key

    def __init__(self, parent):
        super(HotkeySettingsDialog, self).__init__(parent)
        self.setupUi(self)
        self.key = None
        self.target_item = None
        self.grabber = None

    def on_setButton_pressed(self):
        self.setButton.setEnabled(False)
        self.keyLabel.setText("Press a key or combination...")  # TODO: i18n
        logger.debug("User starts to record a key combination.")
        self.grabber = iomediator.KeyGrabber(self)
        self.grabber.start()

    def load(self, item):
        self.target_item = item
        self.setButton.setEnabled(True)
        if model.TriggerMode.HOTKEY in item.modes:
            self.controlButton.setChecked(Key.CONTROL in item.modifiers)
            self.altButton.setChecked(Key.ALT in item.modifiers)
            self.shiftButton.setChecked(Key.SHIFT in item.modifiers)
            self.superButton.setChecked(Key.SUPER in item.modifiers)
            self.hyperButton.setChecked(Key.HYPER in item.modifiers)
            self.metaButton.setChecked(Key.META in item.modifiers)

            key = item.hotKey
            if key in self.KEY_MAP:
                key_text = self.KEY_MAP[key]
            else:
                key_text = key
            self._setKeyLabel(key_text)
            self.key = key_text
            logger.debug("Loaded item {}, key: {}, modifiers: {}".format(item, key_text, item.modifiers))
        else:
            self.reset()

    def save(self, item):
        item.modes.append(model.TriggerMode.HOTKEY)

        # Build modifier list
        modifiers = self.build_modifiers()

        key_text = self.key
        if key_text in self.REVERSE_KEY_MAP:
            key = self.REVERSE_KEY_MAP[key_text]
        else:
            key = key_text

        assert key is not None, "Attempt to set hotkey with no key"
        logger.info("Item {} updated with hotkey {} and modifiers {}".format(item, key, modifiers))
        item.set_hotkey(modifiers, key)

    def reset(self):
        self.controlButton.setChecked(False)
        self.altButton.setChecked(False)
        self.shiftButton.setChecked(False)
        self.superButton.setChecked(False)
        self.hyperButton.setChecked(False)
        self.metaButton.setChecked(False)

        self._setKeyLabel("(None)")  # TODO: i18n
        self.key = None
        self.setButton.setEnabled(True)

    def set_key(self, key, modifiers: list=None):
        if modifiers is None:
            modifiers = []
        if key in self.KEY_MAP:
            key = self.KEY_MAP[key]
        self._setKeyLabel(key)
        self.key = key
        self.controlButton.setChecked(Key.CONTROL in modifiers)
        self.altButton.setChecked(Key.ALT in modifiers)
        self.shiftButton.setChecked(Key.SHIFT in modifiers)
        self.superButton.setChecked(Key.SUPER in modifiers)
        self.hyperButton.setChecked(Key.HYPER in modifiers)
        self.metaButton.setChecked(Key.META in modifiers)

        self.setButton.setEnabled(True)

    def cancel_grab(self):
        logger.debug("User canceled hotkey recording.")
        self.setButton.setEnabled(True)
        self._setKeyLabel(self.key)

    def build_modifiers(self):
        modifiers = []
        if self.controlButton.isChecked():
            modifiers.append(Key.CONTROL)
        if self.altButton.isChecked():
            modifiers.append(Key.ALT)
        if self.shiftButton.isChecked():
            modifiers.append(Key.SHIFT)
        if self.superButton.isChecked():
            modifiers.append(Key.SUPER)
        if self.hyperButton.isChecked():
            modifiers.append(Key.HYPER)
        if self.metaButton.isChecked():
            modifiers.append(Key.META)

        modifiers.sort()
        return modifiers

    def accept(self):
        if self.__valid():
            super().accept()

    def reject(self):
        self.load(self.target_item)
        super().reject()

    def _setKeyLabel(self, key):
        self.keyLabel.setText("Key: " + key)  # TODO: i18n

    def __valid(self):
        if not common.validate(
                self.key is not None,
                "You must specify a key for the hotkey.",
                None,
                self):
            return False

        return True


class GlobalHotkeyDialog(HotkeySettingsDialog):

    def load(self, item):
        self.target_item = item
        if item.enabled:
            self.controlButton.setChecked(Key.CONTROL in item.modifiers)
            self.altButton.setChecked(Key.ALT in item.modifiers)
            self.shiftButton.setChecked(Key.SHIFT in item.modifiers)
            self.superButton.setChecked(Key.SUPER in item.modifiers)
            self.hyperButton.setChecked(Key.HYPER in item.modifiers)
            self.metaButton.setChecked(Key.META in item.modifiers)

            key = item.hotKey
            if key in self.KEY_MAP:
                key_text = self.KEY_MAP[key]
            else:
                key_text = key
            self._setKeyLabel(key_text)
            self.key = key_text

        else:
            self.reset()

    def save(self, item):
        # Build modifier list
        modifiers = self.build_modifiers()

        key_text = self.key
        if key_text in self.REVERSE_KEY_MAP:
            key = self.REVERSE_KEY_MAP[key_text]
        else:
            key = key_text

        assert key is not None, "Attempt to set hotkey with no key"
        item.set_hotkey(modifiers, key)
import sys
from qtpy import QtWidgets, uic, QtCore

from tools.parser import Parser


class PreferencesWindow(QtWidgets.QDialog):
    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.loaded = False
        self.m_settings = QtCore.QSettings('The B1 Project', 'Racing Game Telemetry', parent)

    @staticmethod
    def init_from_ui(parent):
        ui_file = "ui/preferences_window.ui"
        if getattr(sys, 'frozen', False):
            # noinspection PyUnresolvedReferences,PyProtectedMember
            ui_file = sys._MEIPASS + '/' + ui_file
        file = QtCore.QFile(ui_file)
        file.open(QtCore.QFile.ReadOnly)
        preferences_window = uic.loadUi(file, PreferencesWindow(parent))
        file.close()
        preferences_window.treeWidget.setCurrentItem(preferences_window.treeWidget.topLevelItem(0))
        preferences_window.load_preferences()
        return preferences_window

    def change_preferences_panel(self):
        selected_items = self.treeWidget.selectedItems()
        if len(selected_items) > 0:
            selected_item = selected_items[0]
            index = self.treeWidget.indexOfTopLevelItem(selected_item)
            self.stacked_widget.setCurrentIndex(index)

    def on_preferences_updated(self):
        if not self.loaded:
            return
        udp_host = self.udp_host.text()
        if udp_host == '':
            udp_host = Parser.UDP_IP
        self.m_settings.setValue('udp_host', udp_host)
        self.m_settings.setValue('udp_port', self.udp_port.value())
        self.m_settings.setValue('game', self.gamesComboBox.currentData())
        self.m_settings.setValue('autostart', self.autostart.isChecked())
        self.m_settings.setValue('arduino_com_port', self.arduino_com_port.text())
        self.m_settings.setValue('arduino_baud_rate', self.arduino_baud_rate.value())
        self.m_settings.setValue('arduino_autostart', self.arduino_autostart.isChecked())
        self.m_settings.sync()

    def load_preferences(self):
        self.udp_host.setText(self.m_settings.value('udp_host', '', str))
        self.udp_port.setValue(self.m_settings.value('udp_port', 20777, int))
        game = self.m_settings.value('game', None, dict)
        index = 0
        if game is not None:
            index = self.gamesComboBox.findData(game)
        if index == -1:
            index = 0
        self.gamesComboBox.setCurrentIndex(index)
        self.autostart.setChecked(self.m_settings.value('autostart', False, bool))
        self.arduino_com_port.setText(self.m_settings.value('arduino_com_port', '', str))
        self.arduino_baud_rate.setValue(self.m_settings.value('arduino_baud_rate', 115200, int))
        self.arduino_autostart.setChecked(self.m_settings.value('arduino_autostart', False, bool))

    def fill_games_list(self, games, current):
        for game in games:
            self.gamesComboBox.addItem(game['name'], game)
        self.gamesComboBox.setCurrentIndex(
            self.gamesComboBox.findData(current))
        self.loaded = True

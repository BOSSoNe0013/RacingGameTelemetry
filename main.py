# -*- coding: utf-8 -*-
import argparse
import signal
import sys

from qtpy import QtWidgets, QtGui, QtCore

from tools.parser import Parser, ParserListener
from tools.games import Games
from tools.debug import Debug, LogLevel
from tools.telemetry import Telemetry
from ui.main_window import MainWindow
from ui.preferences_window import PreferencesWindow

DEBUG = False
app = None

argument_parser = argparse.ArgumentParser()
argument_parser.add_argument('--debug', '-d', default=False, action='store_true')
argument_parser.add_argument(
    '--log_level',
    '-V',
    type=int,
    default=LogLevel.warn,
    help='Set debug verbosity from 0 (only errors) to 2 (full output)',
    choices=range(0, 3))
flags = argument_parser.parse_args()
if flags.debug:
    DEBUG = True
if flags.log_level is not None:
    Debug.set_log_level(LogLevel(flags.log_level))

Debug.toggle(DEBUG)


# noinspection PyUnusedLocal
def exit_gracefully(signum, frame):
    Debug.warn('Process killed (%s). Exiting gracefully' % signum)
    app.stop()
    sys.exit(0)


class MainApp(MainWindow.Listener):
    style_low = "QProgressBar::chunk {background: QLinearGradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 #00FF00, " \
                "stop: 1 #FFFF00); border: .px solid #FF3410;}"
    style_safe = "QProgressBar::chunk {background: QLinearGradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 #00FF00, " \
                 "stop: 0.625 #FFFF00, stop: 0.9 #FF3410, stop: 1 #0000FF); border: .px solid #FF3410;}"
    style_danger = "QProgressBar::chunk {background: QLinearGradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 #00FF00, " \
                   "stop: 0.4375 #FFFF00, stop: 0.625 #FF3410, stop: 1 #0000FF); border: .px solid #FF3410;}"

    def __init__(self):
        self.m_parser = None
        self.m_window = None
        self.m_connected = False
        self.m_game = Games.DIRT_RALLY
        qt_app = QtWidgets.QApplication(sys.argv)
        qt_app.quitOnLastWindowClosed()
        self.m_window = MainWindow.init_from_ui(self)
        self.fill_games_menu()
        self.clear_ui()
        self.m_window.show()
        self.m_parser = Parser(ParserListener(self.update_ui, self.update_connection_status), self.m_game)
        if DEBUG is True:
            self.m_parser.enable_parser_debug(flags.log_level)
        sys.exit(qt_app.exec_())

    def start(self):
        if self.m_connected:
            return
        Debug.notice('Start UDP socket')
        self.m_parser.open_socket()

    def stop(self):
        if not self.m_connected:
            return
        Debug.notice('Closing UDP socket')
        self.m_parser.close_socket()

    def on_close(self):
        Debug.notice('Main window closed')
        self.stop()

    def on_toggle_connection(self):
        if self.m_connected:
            self.stop()
        else:
            self.start()

    def fill_games_menu(self):
        games_menu = self.m_window.menu_settings.addMenu('&Game')
        games_group = QtWidgets.QActionGroup(games_menu)
        for game in Games():
            act = QtWidgets.QAction(game['name'], games_group)
            act.setCheckable(True)
            act.setData(game)
            games_menu.addAction(act)
            if game is self.m_game:
                Debug.notice('Current game: %s' % self.m_game['name'])
                act.setChecked(True)
        games_group.triggered.connect(self.game_changed)
        games_group.setExclusive(True)

    def game_changed(self, action):
        game = action.data()
        if game:
            Debug.notice('Game changed: %s' % game['name'])
            self.m_game = game
            if self.m_connected:
                self.stop()
            self.m_parser.game = game
            self.clear_ui()

    def clear_ui(self):
        self.m_window.setWindowTitle('Racing Telemetry [%s]' % self.m_game['name'])
        self.m_window.progressBar.setStyleSheet(self.style_low)
        self.m_window.rpmChanged.emit(0)
        self.m_window.gear_view.setText('N')
        self.m_window.speed_view.setText('0')
        self.m_window.track_length_view.display('0')
        self.m_window.distance_view.display(0)
        self.m_window.car_view.setText('Unknown')
        self.m_window.track_view.setText('Unknown')

    def update_ui(self, data):
        gear = "%d" % data['gear']
        if data['gear'] == Telemetry.GEAR_NEUTRAL:
            gear = "N"
        elif data['gear'] == Telemetry.GEAR_REVERSE:
            gear = "R"
        self.m_window.gear_view.setText(gear)
        self.m_window.speed_view.setText("%d" % data['speed'])
        self.m_window.track_length_view.display(data['track_length'])
        self.m_window.distance_view.display(data['distance'])
        car_name = "Unknown"
        if data['car']:
            car_name = data['car']['name']
        self.m_window.car_view.setText(car_name)
        track_name = "Unknown"
        if data['track']:
            track_name = data['track']['name']
        self.m_window.track_view.setText(track_name)
        rpm_percent = 0
        if data['max_rpm'] > 0:
            rpm_percent = int(data['rpm']/data['max_rpm']*100)
        style = self.style_low
        if rpm_percent >= 75:
            style = self.style_danger
        elif rpm_percent >= 30:
            style = self.style_safe
        self.m_window.progressBar.setStyleSheet(style)
        self.m_window.rpmChanged.emit(rpm_percent)

    def update_connection_status(self, status):
        self.m_connected = status
        self.m_window.centralWidget().setEnabled(self.m_connected)
        if self.m_connected:
            Debug.notice("Socket opened")
            self.m_window.menu_action_connect.setText("Dis&connect")
            self.m_window.action_Connect.setIconText("Dis&connect")
            self.m_window.action_Connect.setToolTip("Disconnect")
            self.m_window.action_Connect.setIcon(QtGui.QIcon.fromTheme("offline"))
            self.m_window.statusbar.showMessage("Listening for data on %s:%d " % (Parser.UDP_IP, Parser.UDP_PORT))
        else:
            Debug.notice("Socket closed")
            self.m_window.menu_action_connect.setText("&Connect")
            self.m_window.action_Connect.setIconText("&Connect")
            self.m_window.action_Connect.setToolTip("Connect")
            self.m_window.action_Connect.setIcon(QtGui.QIcon.fromTheme("online"))
            self.m_window.statusbar.clearMessage()

    def show_preferences(self):
        preferences_window = PreferencesWindow.init_from_ui(self.m_window)
        for game in Games():
            preferences_window.gamesComboBox.addItem(game['name'], game)
        preferences_window.show()


if __name__ == '__main__':
    Debug.notice('Starting application')
    signal.signal(signal.SIGINT, exit_gracefully)
    signal.signal(signal.SIGTERM, exit_gracefully)
    signal.signal(signal.SIGABRT, exit_gracefully)
    app = MainApp()



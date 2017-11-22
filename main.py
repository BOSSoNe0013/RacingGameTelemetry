# -*- coding: utf-8 -*-
import argparse
import signal
import sys

from qtpy import QtWidgets, QtGui, QtCore

from tools.serial_output import ArduiDash, start_data
from tools.parser import Parser, ParserListener
from tools.games import Games
from tools.debug import Debug, LogLevel
from tools.telemetry import Telemetry
from ui.main_window import MainWindow
from ui.preferences_window import PreferencesWindow
from ui.scanner_window import ScannerWindow
from ui.scanner_window import Types as scanTypes

DEBUG = False
GUI = True
app = None

argument_parser = argparse.ArgumentParser()
argument_parser.add_argument('--debug', '-d', default=False, action='store_true')
argument_parser.add_argument(
    '--gui',
    dest='gui',
    action='store_true',
    help='Display graphical user interface (default)')
argument_parser.add_argument('--no-gui', dest='gui', action='store_false', help='Console mode')
argument_parser.set_defaults(gui=True)
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
if flags.gui is not None:
    if flags.gui is False:
        Debug.notice('No gui')
        DEBUG = True
        Debug.set_log_level(LogLevel(2))
    GUI = flags.gui

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
        self.m_settings = None
        self.m_parser = None
        self.m_window = None
        self.m_connected = False
        self.m_auto_start = False
        self.m_full_screen = False
        self.clutch_pedal_effect = None
        self.brake_pedal_effect = None
        self.throttle_pedal_effect = None
        self.m_udp_host = Parser.UDP_IP
        self.m_udp_port = Parser.UDP_PORT
        self.m_game = Games.DIRT_RALLY
        self.ardui_dash = None
        self.arduino_com_port = None
        self.arduino_baud_rate = None
        self.arduino_auto_start = False

        qt_app = QtWidgets.QApplication(sys.argv)
        qt_app.quitOnLastWindowClosed()
        self.m_window = MainWindow.init_from_ui(self)
        self.load_preferences()

        prefix_path = ''
        if getattr(sys, 'frozen', False):
            # noinspection PyUnresolvedReferences,PyProtectedMember
            prefix_path = sys._MEIPASS + '/'
        self.m_window.clutch_label.setPixmap(QtGui.QPixmap(prefix_path + 'res/images/clutch.png'))
        self.m_window.brake_label.setPixmap(QtGui.QPixmap(prefix_path + 'res/images/brake.png'))
        self.m_window.throttle_label.setPixmap(QtGui.QPixmap(prefix_path + 'res/images/throttle.png'))

        self.fill_games_menu()
        self.clear_ui()

        self.ardui_dash = ArduiDash()

        if GUI is True:
            if self.m_full_screen is True:
                self.m_window.showFullScreen()
                self.m_window.toolBar.hide()
            else:
                self.m_window.show()
            if DEBUG is True:
                self.m_parser.enable_parser_debug(flags.log_level)
                self.ardui_dash.enable_debug(flags.log_level)
            if self.m_auto_start is True:
                self.start()
            sys.exit(qt_app.exec_())
        else:
            self.m_parser.enable_parser_debug(2)
            self.ardui_dash.enable_debug(2)
            self.start()

    def create_pedal_effects(self):
        foreground = self.m_window.palette().windowText().color()

        self.clutch_pedal_effect = QtWidgets.QGraphicsColorizeEffect()
        self.clutch_pedal_effect.setStrength(0)
        self.clutch_pedal_effect.setColor(foreground)

        self.brake_pedal_effect = QtWidgets.QGraphicsColorizeEffect()
        self.brake_pedal_effect.setStrength(0)
        self.brake_pedal_effect.setColor(foreground)

        self.throttle_pedal_effect = QtWidgets.QGraphicsColorizeEffect()
        self.throttle_pedal_effect.setStrength(0)
        self.throttle_pedal_effect.setColor(foreground)

        self.m_window.clutch_label.setGraphicsEffect(self.clutch_pedal_effect)
        self.m_window.brake_label.setGraphicsEffect(self.brake_pedal_effect)
        self.m_window.throttle_label.setGraphicsEffect(self.throttle_pedal_effect)

    def toggle_clutch_state(self, status):
        self.toggle_label_tint(self.clutch_pedal_effect, status)

    def toggle_brake_state(self, status):
        self.toggle_label_tint(self.brake_pedal_effect, status)

    def toggle_throttle_state(self, status):
        self.toggle_label_tint(self.throttle_pedal_effect, status)
        
    @staticmethod
    def toggle_label_tint(pedal_effect, status):
        if pedal_effect is None:
            return
        if status:
            pedal_effect.setStrength(1.0)
        else:
            pedal_effect.setStrength(0.0)

    def start(self):
        if self.m_connected:
            return
        if self.arduino_auto_start is True:
            self.ardui_dash.start(self.arduino_com_port, self.arduino_baud_rate)
        Debug.notice('Start UDP socket')
        self.m_parser.open_socket()

    def stop(self):
        if self.ardui_dash is not None:
            self.ardui_dash.stop()
        self.clear_ui()
        if self.m_connected:
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
            if game == self.m_game:
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
        if GUI is False:
            return
        self.m_window.setWindowTitle('Racing Telemetry [%s]' % self.m_game['name'])
        self.m_window.progressBar.setStyleSheet(self.style_low)
        self.m_window.rpmChanged.emit(0)
        self.m_window.gear_view.setText('N')
        self.m_window.speed_view.setText('0')
        self.m_window.track_length_view.display('0')
        self.m_window.distance_view.display(0)
        self.m_window.car_view.setText('Unknown')
        self.m_window.track_view.setText('Unknown')
        self.toggle_brake_state(False)
        self.toggle_clutch_state(False)
        self.toggle_throttle_state(False)

    def update_ui(self, data):
        self.ardui_dash.telemetry_out(data)
        if GUI is False:
            return
        gear = "%d" % data['gear']
        if data['gear'] == Telemetry.GEAR_NEUTRAL:
            gear = "N"
        elif data['gear'] == Telemetry.GEAR_REVERSE:
            gear = "R"
        self.m_window.gear_view.setText(gear)
        self.toggle_brake_state(data['brake'] > 0.0)
        self.toggle_clutch_state(data['clutch'] > 0.0)
        self.toggle_throttle_state(data['throttle'] > 0.0)
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
            self.m_window.statusbar\
                .showMessage("Listening for data on %s:%d " % (self.m_parser.UDP_IP, self.m_parser.UDP_PORT))
            self.ardui_dash.setup(2)
            self.ardui_dash.change_mode(1)
        else:
            Debug.notice("Socket closed")
            self.m_window.menu_action_connect.setText("&Connect")
            self.m_window.action_Connect.setIconText("&Connect")
            self.m_window.action_Connect.setToolTip("Connect")
            self.m_window.action_Connect.setIcon(QtGui.QIcon.fromTheme("online"))
            self.m_window.statusbar.clearMessage()

    def show_preferences(self):
        preferences_window = PreferencesWindow.init_from_ui(self.m_window)
        try:
            current_game = self.m_settings.value('game', Games.DIRT_RALLY, dict)
        except TypeError:
            current_game = Games.DIRT_RALLY
        preferences_window.fill_games_list(Games(), current_game)
        preferences_window.finished.connect(self.load_preferences)
        preferences_window.show()

    def load_preferences(self):
        self.m_settings = QtCore.QSettings('The B1 Project', 'Racing Game Telemetry', self.m_window)
        self.create_pedal_effects()
        self.stop()
        try:
            self.m_game = self.m_settings.value('game', Games.DIRT_RALLY, dict)
        except TypeError:
            self.m_game = Games.DIRT_RALLY
        self.m_udp_host = self.m_settings.value('udp_host', Parser.UDP_IP, str)
        self.m_udp_port = self.m_settings.value('udp_port', Parser.UDP_PORT, int)
        self.m_auto_start = self.m_settings.value('autostart', False, bool)
        self.m_full_screen = self.m_settings.value('fullscreen', False, bool)
        self.arduino_com_port = self.m_settings.value('arduino_com_port', '/dev/ttyUSB0', str)
        self.arduino_baud_rate = self.m_settings.value('arduino_baud_rate', 115200, int)
        self.arduino_auto_start = self.m_settings.value('arduino_autostart', False, bool)
        self.m_parser = Parser(
            ParserListener(self.update_ui, self.update_connection_status),
            self.m_game,
            self.m_udp_host,
            self.m_udp_port
        )
        self.clear_ui()

    def show_track_scanner(self):
        self.stop()
        scanner_window = ScannerWindow.init_from_ui(self.m_window)
        scanner_window.setWindowTitle('Track Scanner')
        scanner_window.show()
        scanner_window.start_scanner()

    def show_car_scanner(self):
        self.stop()
        scanner_window = ScannerWindow.init_from_ui(self.m_window, scanTypes.CARS)
        scanner_window.setWindowTitle('Car Scanner')
        scanner_window.show()
        scanner_window.start_scanner()


if __name__ == '__main__':
    Debug.notice('Starting application')
    signal.signal(signal.SIGINT, exit_gracefully)
    signal.signal(signal.SIGTERM, exit_gracefully)
    signal.signal(signal.SIGABRT, exit_gracefully)
    signal.signal(signal.SIGTSTP, exit_gracefully)
    app = MainApp()



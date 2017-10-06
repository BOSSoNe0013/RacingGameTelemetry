# -*- coding: utf-8 -*-
import argparse
import signal
import sys

from qtpy import QtWidgets, uic, QtGui, QtCore

from tools import parser
from tools.games import Games
from tools.debug import Debug
from tools.debug import LogLevel
from tools.telemetry import Telemetry

DEBUG = False

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
    stop()
    sys.exit(0)


class MainWindow(QtWidgets.QMainWindow):
    rpmChanged = QtCore.Signal(int)

    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)

    def closeEvent(self, *args, **kwargs):
        Debug.notice('Main window closed')
        stop()

    # noinspection PyMethodMayBeStatic
    def toggle_connection(self):
        if m_connected:
            stop()
        else:
            start()


class Listener:
    def __init__(self, data_callback=None, connection_callback=None):
        self.data_callback = data_callback
        self.connection_callback = connection_callback

    def data_received(self, data):
        if not self.data_callback:
            return
        self.data_callback(data)

    def connection_status_changed(self, status):
        if not self.connection_callback:
            return
        self.connection_callback(status)


def main():
    global m_parser, m_window, style_low
    app = QtWidgets.QApplication(sys.argv)
    app.quitOnLastWindowClosed()
    m_window = setup_ui("main.ui")
    m_window.setWindowTitle('Racing Telemetry [%s]' % Games.DIRT_RALLY['name'])
    m_window.rpmChanged.connect(m_window.progressBar.setValue)
    style = style_low
    m_window.progressBar.setStyleSheet(style)
    m_window.show()
    m_parser = parser.Parser(Listener(update_ui, update_connection_status), Games.DIRT_RALLY)
    if DEBUG is True:
        m_parser.enable_parser_debug(flags.log_level)
    sys.exit(app.exec_())


def start():
    global m_parser, m_connected
    if m_connected:
        return
    Debug.notice('Start UPD socket')
    m_parser.open_socket()


def stop():
    global m_parser, m_connected
    if not m_connected:
        return
    Debug.notice('Closing UDP socket')
    m_parser.close_socket()


def setup_ui(ui_file):
    if getattr(sys, 'frozen', False):
        # noinspection PyUnresolvedReferences,PyProtectedMember
        ui_file = sys._MEIPASS + '/' + ui_file
    file = QtCore.QFile(ui_file)
    file.open(QtCore.QFile.ReadOnly)
    ui = uic.loadUi(file, MainWindow())
    file.close()
    return ui


def update_ui(data):
    global m_window, style_danger, style_safe, style_low
    gear = "%d" % data['gear']
    if data['gear'] == Telemetry.GEAR_NEUTRAL:
        gear = "N"
    elif data['gear'] == Telemetry.GEAR_REVERSE:
        gear = "R"
    m_window.gear_view.setText(gear)
    m_window.speed_view.setText("%d" % data['speed'])
    m_window.track_length_view.display(data['track_length'])
    m_window.distance_view.display(data['distance'])
    car_name = "Unknown"
    if data['car']:
        car_name = data['car']['name']
    m_window.car_view.setText(car_name)
    track_name = "Unknown"
    if data['track']:
        track_name = data['track']['name']
    m_window.track_view.setText(track_name)
    rpm_percent = 0
    if data['max_rpm'] > 0:
        rpm_percent = int(data['rpm']/data['max_rpm']*100)
    style = style_low
    if rpm_percent >= 75:
        style = style_danger
    elif rpm_percent >= 30:
        style = style_safe
    m_window.progressBar.setStyleSheet(style)
    m_window.rpmChanged.emit(rpm_percent)


def update_connection_status(status):
    global m_connected, m_window
    m_connected = status
    m_window.centralWidget().setEnabled(m_connected)
    if m_connected:
        Debug.notice("Socket opened")
        m_window.menu_action_connect.setText("Dis&connect")
        m_window.action_Connect.setIconText("Dis&connect")
        m_window.action_Connect.setIcon(QtGui.QIcon.fromTheme("offline"))
        m_window.statusbar.showMessage("Listening for data on %s:%d " % (parser.UDP_IP, parser.UDP_PORT))
    else:
        Debug.notice("Socket closed")
        m_window.menu_action_connect.setText("&Connect")
        m_window.action_Connect.setIconText("&Connect")
        m_window.action_Connect.setIcon(QtGui.QIcon.fromTheme("online"))
        m_window.statusbar.clearMessage()


if __name__ == '__main__':
    Debug.notice('Starting application')
    signal.signal(signal.SIGINT, exit_gracefully)
    signal.signal(signal.SIGTERM, exit_gracefully)
    signal.signal(signal.SIGABRT, exit_gracefully)
    m_parser = None
    m_connected = False
    m_window = None
    style_low = "QProgressBar::chunk {background: QLinearGradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 #00FF00, " \
                "stop: 1 #FFFF00); border: .px solid #FF3410;}"
    style_safe = "QProgressBar::chunk {background: QLinearGradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 #00FF00, " \
                 "stop: 0.625 #FFFF00, stop: 0.9 #FF3410, stop: 1 #0000FF); border: .px solid #FF3410;}"
    style_danger = "QProgressBar::chunk {background: QLinearGradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 #00FF00, " \
                   "stop: 0.4375 #FFFF00, stop: 0.625 #FF3410, stop: 1 #0000FF); border: .px solid #FF3410;}"
    main()



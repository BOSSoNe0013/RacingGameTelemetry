import sys
from qtpy import QtWidgets, QtCore, uic

from tools.games import Games
from tools.track_scanner import Scan as trackScan
from tools.car_scanner import Scan as carScan


class Types:
    CARS = 0
    TRACKS = 1


class ScannerWindow(QtWidgets.QDialog):
    onScanOutput = QtCore.Signal(str)

    def __init__(self, parent=None, scan_type=Types.TRACKS):
        QtWidgets.QDialog.__init__(self, parent)
        self.track_scanner = None
        self.car_scanner = None
        self.type = scan_type

    @staticmethod
    def init_from_ui(parent, scan_type=Types.TRACKS):
        ui_file = "ui/scanner_window.ui"
        if getattr(sys, 'frozen', False):
            # noinspection PyUnresolvedReferences,PyProtectedMember
            ui_file = sys._MEIPASS + '/' + ui_file
        file = QtCore.QFile(ui_file)
        file.open(QtCore.QFile.ReadOnly)
        scanner_window = uic.loadUi(file, ScannerWindow(parent, scan_type))
        scanner_window.onScanOutput.connect(scanner_window.output_view.appendPlainText)
        file.close()
        return scanner_window

    def closeEvent(self, *args, **kwargs):
        if self.track_scanner is not None:
            self.track_scanner.finish()
        if self.car_scanner is not None:
            self.car_scanner.finish()

    def handle_output(self, data):
        self.onScanOutput.emit(data)

    def start_scanner(self):
        if self.type is Types.TRACKS:
            self.track_scanner = trackScan(
                Games.DIRT_RALLY,
                '127.0.0.1',
                20777,
                self.handle_output
            )
            self.track_scanner.start()
        elif self.type is Types.CARS:
            self.car_scanner = carScan(
                Games.DIRT_RALLY,
                '127.0.0.1',
                20777,
                self.handle_output
            )
            self.car_scanner.start()

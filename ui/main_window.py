import sys
from abc import ABC, abstractmethod
from qtpy import QtWidgets, uic, QtCore


class MainWindow(QtWidgets.QMainWindow):
    rpmChanged = QtCore.Signal(int)

    class Listener(ABC):
        @abstractmethod
        def on_close(self):
            pass

        @abstractmethod
        def on_toggle_connection(self):
            pass

    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, None)
        self.listener = parent

    def closeEvent(self, *args, **kwargs):
        self.listener.on_close()

    def toggle_connection(self):
        self.listener.on_toggle_connection()

    def show_preferences(self):
        self.listener.show_preferences()

    @staticmethod
    def init_from_ui(parent):
        ui_file = "ui/main_window.ui"
        if getattr(sys, 'frozen', False):
            # noinspection PyUnresolvedReferences,PyProtectedMember
            ui_file = sys._MEIPASS + '/' + ui_file
        file = QtCore.QFile(ui_file)
        file.open(QtCore.QFile.ReadOnly)
        main_window = uic.loadUi(file, MainWindow(parent))
        main_window.rpmChanged.connect(main_window.progressBar.setValue)
        file.close()
        return main_window

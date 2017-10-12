import sys
from qtpy import QtWidgets, uic, QtCore


class PreferencesWindow(QtWidgets.QDialog):
    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self, parent)

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
        return preferences_window

    def change_preferences_panel(self):
        selected_item = None
        selected_items = self.treeWidget.selectedItems()
        if len(selected_items) > 0:
            selected_item = selected_items[0]
            index = self.treeWidget.indexOfTopLevelItem(selected_item)
            self.stacked_widget.setCurrentIndex(index)

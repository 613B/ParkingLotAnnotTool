import cv2

from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

from ParkingLotAnnotTool.public.signals import global_signals
from ParkingLotAnnotTool.utils.resource import read_icon
from ParkingLotAnnotTool.utils.trace import traceback_and_exit
from ..general.action import new_action
from ..general.canvas import CanvasPicture, CanvasScroll
from .conditionsdata import ConditionsData, ConditionsDataInfoWidget
from .seekbar import SeekBarWidget


class ClassifyConditionsWidget(QWidget):
    def __init__(self):
        super(ClassifyConditionsWidget, self).__init__()

        self.conditions_data = ConditionsData()
        self.conditions_data_info = ConditionsDataInfoWidget(self.conditions_data)
        self.conditions_data.current_frame_changed.connect(self.conditions_data_info.update)
        self.setting_dialog = SettingsDialog(self.conditions_data)

        self.canvas_picture = CanvasPicture()
        self.canvas_scroll = CanvasScroll(self, self.canvas_picture)
        self.seekbar = SeekBarWidget()
        self.seekbar.valueChanged.connect(self.on_seekbar_value_changed)

        self.open_action = new_action(self, 'Open', icon=read_icon('open_file.png'), slot=self.click_open)
        self.save_action = new_action(self, 'Save', icon=read_icon('save.png'), slot=self.click_save, shortcut=QKeySequence("Ctrl+S"))
        # TODO setshortcut
        self.sunny_action = new_action(self, 'Sunny', icon_text='Sunny', slot=self.click_sunny)
        self.rainy_action = new_action(self, 'Rainy', icon_text='Rainy', slot=self.click_rainy)
        self.undo_action = new_action(self, 'Undo', icon_text='Undo', slot=self.click_undo)
        self.view_zoom_fit_action = new_action(self, 'Zoom Fit', icon=read_icon('zoom_fit.png'), slot=self.press_view_zoom_fit)
        self.view_zoom_1_action = new_action(self, 'Zoom 100%', icon=read_icon('zoom_1.png'), slot=self.press_view_zoom_1)
        self.settings_action = new_action(self, 'Settings', icon=read_icon('gear.png'), slot=self.click_settings)
        self.toolbar = QToolBar()
        self.toolbar.setOrientation(Qt.Orientation.Vertical)
        self.toolbar.addAction(self.open_action)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.save_action)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.rainy_action)
        self.toolbar.addAction(self.sunny_action)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.undo_action)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.view_zoom_fit_action)
        self.toolbar.addAction(self.view_zoom_1_action)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.settings_action)

        self.conditions_list = QListWidget(self)
        self.conditions_list.setMaximumWidth(200)
        self.conditions_list.itemSelectionChanged.connect(self.on_conditionslist_itemselection_changed)

        layout = QGridLayout(self)
        layout.addWidget(self.toolbar, 0, 0, 2, 1)  # (widget, row, col, row_size, col_size)
        layout.addWidget(self.canvas_scroll, 0, 1, 1, 1)
        layout.addWidget(self.conditions_data_info, 0, 2, 1, 1)
        layout.addWidget(self.seekbar, 1, 1, 1, 2)
        layout.addWidget(self.conditions_list, 0, 3, 2, 1)
        self.setLayout(layout)

    def changed_zoom(self):
        traceback_and_exit(self.changed_zoom_impl)
    def changed_zoom_impl(self):
        self.canvas_picture.set_zoom(100)

    def click_open(self) -> None:
        traceback_and_exit(self.click_open_impl)
    def click_open_impl(self) -> None:
        file_path = QFileDialog.getOpenFileName(self, "Open File", "", "conditions.json (conditions.json)")
        if file_path == ('', ''):
            return
        self.conditions_data.set_json_path(file_path[0])
        self.conditions_data.load()
        global_signals.print(f"[{self.__class__.__name__}] open: {file_path[0]}")
        self.seekbar.set_maxvalue(self.conditions_data.len_frames()-1)
        self.canvas_picture.set_picture(self.conditions_data.current_img())
        self.canvas_scroll.fit_window()

    def click_save(self) -> None:
        traceback_and_exit(self.click_save_impl)
    def click_save_impl(self) -> None:
        global_signals.print(f"[{self.__class__.__name__}] save.")
        self.conditions_data.save()

    def click_rainy(self) -> None:
        traceback_and_exit(self.click_rainy_impl)
    def click_rainy_impl(self) -> None:
        if self.conditions_list.findItems(self.seekbar.get_value_str(), Qt.MatchFlag.MatchContains):
            return
        self.sunny_action.setEnabled(True)
        self.rainy_action.setEnabled(False)
        self.seekbar.add_rainy_condition()
        self.conditions_list.addItem(f'rainy, {self.seekbar.get_value_str()}')
        self.conditions_data.add_label("rainy")

    def click_sunny(self) -> None:
        traceback_and_exit(self.click_sunny_impl)
    def click_sunny_impl(self) -> None:
        if self.conditions_list.findItems(self.seekbar.get_value_str(), Qt.MatchFlag.MatchContains):
            return
        self.sunny_action.setEnabled(False)
        self.rainy_action.setEnabled(True)
        self.seekbar.add_sunny_condition()
        self.conditions_list.addItem(f'sunny, {self.seekbar.get_value_str()}')
        self.conditions_data.add_label("sunny")

    def click_undo(self) -> None:
        traceback_and_exit(self.click_undo_impl)
    def click_undo_impl(self) -> None:
        if self.conditions_list.count() <= 0:
            return
        last_item = self.conditions_list.takeItem(self.conditions_list.count() - 1)
        parts = last_item.text().split(", ")
        label = parts[0]
        frame = parts[1]
        if   label == "sunny":
            self.seekbar.remove_sunny_conditions(int(frame))
            self.sunny_action.setEnabled(True)
            self.rainy_action.setEnabled(False)
            self.conditions_data.remove_conditions(
                key=self.conditions_list.selectedItems()[0].text(),
                conditions={"label": "sunny", "frame": frame})
        elif label == "rainy":
            self.seekbar.remove_rainy_conditions(int(frame))
            self.sunny_action.setEnabled(False)
            self.rainy_action.setEnabled(True)
            self.conditions_data.remove_conditions(
                key=self.conditions_list.selectedItems()[0].text(),
                conditions={"label": "rainy", "frame": frame})
        if self.conditions_list.count() == 0:
            self.sunny_action.setEnabled(True)
            self.rainy_action.setEnabled(True)

    def press_view_zoom_fit(self) -> None:
        traceback_and_exit(self.press_view_zoom_fit_impl)
    def press_view_zoom_fit_impl(self) -> None:
        self.canvas_scroll.fit_window()

    def press_view_zoom_1(self) -> None:
        traceback_and_exit(self.press_view_zoom_1_impl)
    def press_view_zoom_1_impl(self) -> None:
        self.canvas_scroll.set_zoom(100)

    def click_settings(self) -> None:
        traceback_and_exit(self.click_settings_impl)
    def click_settings_impl(self) -> None:
        self.setting_dialog.popup()

    def on_seekbar_value_changed(self, value):
        self.canvas_picture.set_picture(self.conditions_data.current_img())
        self.conditions_data.update_current_frame(self.seekbar.get_value_str())

    def on_conditionslist_itemselection_changed(self):
        selected_items = self.conditions_list.selectedItems()
        if not selected_items:
            return
        parts = selected_items[0].text().split(", ")
        label = parts[0]
        frame = parts[1]
        self.canvas_picture.set_picture(self.conditions_data.current_img())
        self.seekbar.set_value(int(frame))
        if   label == "sunny":
            self.sunny_action.setEnabled(False)
            self.rainy_action.setEnabled(True)
        elif label == "rainy":
            self.sunny_action.setEnabled(True)
            self.rainy_action.setEnabled(False)


class SettingsDialog(QDialog):

    def __init__(self, conditions_data: ConditionsData, parent=None):
        super(SettingsDialog, self).__init__(parent)
        self.conditions_data = conditions_data
        self.setWindowTitle('Setting')
        self.setWindowFlags(
            self.windowFlags() &
            ~Qt.WindowType.WindowContextHelpButtonHint)

        self.label_initial_time = QLabel('Initial Time [hh:mm:ss]')
        self.ledit_initial_time = QLineEdit()
        self.ledit_initial_time.setText(self.conditions_data.initial_time())

        self.label_day_start_time = QLabel('Day Start Time [hh:mm:ss]')
        self.ledit_day_start_time = QLineEdit()
        self.ledit_day_start_time.setText(self.conditions_data.day_start_time())

        self.label_night_start_time = QLabel('Night Start Time [hh:mm:ss]')
        self.ledit_night_start_time = QLineEdit()
        self.ledit_night_start_time.setText(self.conditions_data.night_start_time())

        self.bb = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok, self)
        self.bb.accepted.connect(self.accept)

        layout = QVBoxLayout()
        gl = QGridLayout()
        gl.addWidget(self.label_initial_time, 0, 0)
        gl.addWidget(self.ledit_initial_time, 0, 1)
        gl.addWidget(self.label_day_start_time, 1, 0)
        gl.addWidget(self.ledit_day_start_time, 1, 1)
        gl.addWidget(self.label_night_start_time, 2, 0)
        gl.addWidget(self.ledit_night_start_time, 2, 1)
        layout.addLayout(gl)
        layout.addWidget(self.bb)
        self.setLayout(layout)

    def popup(self):
        if self.exec() == 0:
            return
        if not self.conditions_data.loaded():
            return
        self.conditions_data.set_initial_time(self.ledit_initial_time.text())
        self.conditions_data.set_day_start_time(self.ledit_day_start_time.text())
        self.conditions_data.set_night_start_time(self.ledit_night_start_time.text())

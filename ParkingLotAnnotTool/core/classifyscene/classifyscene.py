import cv2

from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

from ParkingLotAnnotTool.utils.resource import read_icon
from ParkingLotAnnotTool.utils.signal import *
from ParkingLotAnnotTool.utils.trace import traceback_and_exit
from ..general.action import new_action
from ..general.canvas import CanvasPicture, CanvasScroll
from .scenedata import SceneData

epsilon = 16.0
area_init_size = 100.0
point_size = 8

lot_default_fill_color       = QColor(  0, 128, 255, 155)
lot_highlighted_fill_color   = QColor(  0,   0, 255, 200)
lot_selected_fill_color      = QColor(  0,   0, 255, 128)
point_default_fill_color     = QColor(255,   0,   0, 128)
point_highlighted_fill_color = QColor(255, 153,   0, 255)

CANVASTOOL_NONE = 0
CANVASTOOL_DRAW = 1

class ClassifySceneWidget(QWidget):

    def __init__(self):
        super(ClassifySceneWidget, self).__init__()

        self.editable = True
        self.scene_data = SceneData()

        self.canvas_picture = CanvasPicture()
        self.canvas_scroll = CanvasScroll(self, self.canvas_picture)
        self.seekbar = SeekBarWidget()
        self.seekbar.valueChanged.connect(self.on_seekbar_value_changed)

        self.open_action = new_action(self, 'Open', icon=read_icon('open_file.png'), slot=self.click_open)
        self.save_action = new_action(self, 'Save', icon=read_icon('save.png'), slot=self.click_save)
        # TODO setshortcut
        self.busy_action = new_action(self, 'Busy', icon_text='Busy', slot=self.click_busy)
        self.free_action = new_action(self, 'Free', icon_text='Free', slot=self.click_free)
        self.undo_action = new_action(self, 'Undo', icon_text='Undo', slot=self.click_undo)
        self.view_zoom_fit_action = new_action(self, 'Zoom Fit', icon=read_icon('zoom_fit.png'), slot=self.press_view_zoom_fit)
        self.view_zoom_1_action = new_action(self, 'Zoom 100%', icon=read_icon('zoom_1.png'), slot=self.press_view_zoom_1)
        self.toolbar = QToolBar()
        self.toolbar.setOrientation(Qt.Orientation.Vertical)
        self.toolbar.addAction(self.open_action)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.save_action)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.free_action)
        self.toolbar.addAction(self.busy_action)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.undo_action)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.view_zoom_fit_action)
        self.toolbar.addAction(self.view_zoom_1_action)

        self.lot_list = QListWidget(self)
        self.lot_list.itemSelectionChanged.connect(self.on_lotlist_itemselection_changed)
        self.scene_list = QListWidget(self)
        self.scene_list.itemSelectionChanged.connect(self.on_scenelist_itemselection_changed)

        layout = QGridLayout(self)
        layout.addWidget(self.toolbar, 0, 0, 2, 1)  # (widget, row, col, row_size, col_size)
        layout.addWidget(self.canvas_scroll, 0, 1, 1, 1)
        layout.addWidget(self.seekbar, 1, 1, 1, 1)
        layout.addWidget(self.scene_list, 0, 2, 2, 1)
        layout.addWidget(self.lot_list, 0, 3, 2, 1)
        self.setLayout(layout)

    def enable_add_preset(self) -> None:
        self.editable = False
        self.set_action.setEnabled(False)
        self.save_action.setEnabled(False)
        self.free_action.setEnabled(False)
        self.busy_action.setEnabled(False)
        self.undo_action.setEnabled(False)
        self.view_zoom_fit_action.setEnabled(False)
        self.view_zoom_1_action.setEnabled(False)

    def disable_add_preset(self) -> None:
        self.editable = True
        self.set_action.setEnabled(True)
        self.save_action.setEnabled(True)
        self.free_action.setEnabled(True)
        self.busy_action.setEnabled(True)
        self.undo_action.setEnabled(True)
        self.view_zoom_fit_action.setEnabled(True)
        self.view_zoom_1_action.setEnabled(True)

    def changed_zoom(self):
        traceback_and_exit(self.changed_zoom_impl)
    def changed_zoom_impl(self):
        self.canvas_picture.set_zoom(100)

    def click_open(self) -> None:
        traceback_and_exit(self.click_open_impl)
    def click_open_impl(self) -> None:
        file_path = QFileDialog.getOpenFileName(self, "Open File", "", "scene.json (scene.json)")
        print(file_path)
        if file_path == ('', ''):
            return
        self.scene_data.set_json_path(file_path[0])
        self.scene_data.load()
        self.seekbar.set_maxvalue(self.scene_data.len_frames-1)
        img = cv2.imread(self.scene_data.lot_dirs[0] / self.scene_data.frame_names[0], cv2.IMREAD_COLOR)
        self.canvas_picture.set_picture(img)
        self.canvas_scroll.fit_window()
        self.lot_list.addItems([lot['id'] for lot in self.scene_data.get_lots()])
        self.lot_list.setCurrentRow(0)

    def click_save(self) -> None:
        traceback_and_exit(self.click_save_impl)
    def click_save_impl(self) -> None:
        self.scene_data.save()

    def click_free(self) -> None:
        traceback_and_exit(self.click_free_impl)
    def click_free_impl(self) -> None:
        if self.scene_list.findItems(self.seekbar.get_value_str(), Qt.MatchFlag.MatchContains):
            return
        self.busy_action.setEnabled(True)
        self.free_action.setEnabled(False)
        self.seekbar.add_free_scene()
        self.scene_list.addItem(f'F: {self.seekbar.get_value_str()}')
        self.scene_data.scenes[self.lot_list.selectedItems()[0].text()].append(
            {"label": "free", "frame": self.seekbar.get_value_str()})

    def click_busy(self) -> None:
        traceback_and_exit(self.click_busy_impl)
    def click_busy_impl(self) -> None:
        if self.scene_list.findItems(self.seekbar.get_value_str(), Qt.MatchFlag.MatchContains):
            return
        self.busy_action.setEnabled(False)
        self.free_action.setEnabled(True)
        self.seekbar.add_busy_scene()
        self.scene_list.addItem(f'B: {self.seekbar.get_value_str()}')
        self.scene_data.scenes[self.lot_list.selectedItems()[0].text()].append(
            {"label": "busy", "frame": self.seekbar.get_value_str()})

    def click_undo(self) -> None:
        traceback_and_exit(self.click_undo_impl)
    def click_undo_impl(self) -> None:
        if self.scene_list.count() <= 0:
            return
        last_item = self.scene_list.takeItem(self.scene_list.count() - 1)
        parts = last_item.text().split(": ")
        label = parts[0]
        frame = parts[1]
        if   label == "B":
            self.seekbar.remove_busy_scene(int(frame))
            self.busy_action.setEnabled(True)
            self.free_action.setEnabled(False)
            self.scene_data.scenes[self.lot_list.selectedItems()[0].text()].remove(
                {"label": "busy", "frame": frame})
        elif label == "F":
            self.seekbar.remove_free_scene(int(frame))
            self.busy_action.setEnabled(False)
            self.free_action.setEnabled(True)
            self.scene_data.scenes[self.lot_list.selectedItems()[0].text()].remove(
                {"label": "free", "frame": frame})
        if self.scene_list.count() == 0:
            self.busy_action.setEnabled(True)
            self.free_action.setEnabled(True) 

    def press_view_zoom_fit(self) -> None:
        traceback_and_exit(self.press_view_zoom_fit_impl)
    def press_view_zoom_fit_impl(self) -> None:
        self.canvas_scroll.fit_window()

    def press_view_zoom_1(self) -> None:
        traceback_and_exit(self.press_view_zoom_1_impl)
    def press_view_zoom_1_impl(self) -> None:
        self.canvas_scroll.set_zoom(100)

    def on_seekbar_value_changed(self, value):
        selected_items = self.lot_list.selectedItems()
        if not selected_items:
            return
        img = cv2.imread(self.scene_data.parent_dir / selected_items[0].text() / self.scene_data.frame_names[value], cv2.IMREAD_COLOR)
        self.canvas_picture.set_picture(img)
    
    def on_lotlist_itemselection_changed(self):
        selected_items = self.lot_list.selectedItems()
        frame_idx = self.seekbar.get_value()
        img = cv2.imread(self.scene_data.parent_dir / selected_items[0].text() / self.scene_data.frame_names[frame_idx], cv2.IMREAD_COLOR)
        self.canvas_picture.set_picture(img)
        self.scene_list.clear()
        self.seekbar.reset_scenes()
        scenes = self.scene_data.scenes[selected_items[0].text()]
        self.busy_action.setEnabled(True)
        self.free_action.setEnabled(True)
        if scenes:
            if   scenes[-1]["label"] == "busy":
                self.busy_action.setEnabled(False)
            elif scenes[-1]["label"] == "free":
                self.free_action.setEnabled(False)
        for scene in scenes:
            self.seekbar.set_value(int(scene["frame"]))
            if   scene["label"] == "busy":
                self.seekbar.add_busy_scene()
                self.scene_list.addItem(f'B: {scene["frame"]}')
            elif scene["label"] == "free":
                self.seekbar.add_free_scene()
                self.scene_list.addItem(f'F: {scene["frame"]}')

    def on_scenelist_itemselection_changed(self):
        selected_items = self.scene_list.selectedItems()
        if not selected_items:
            return
        current_lot = self.lot_list.currentItem()
        parts = selected_items[0].text().split(": ")
        label = parts[0]
        frame = parts[1]
        img = cv2.imread(self.scene_data.parent_dir / current_lot.text() / (frame + ".jpg"), cv2.IMREAD_COLOR)
        self.canvas_picture.set_picture(img)
        self.seekbar.set_value(int(frame))
        if   label == "B":
            self.busy_action.setEnabled(False)
            self.free_action.setEnabled(True)
        elif label == "F":
            self.busy_action.setEnabled(True)
            self.free_action.setEnabled(False)

    def refresh(self) -> None:
        self.lot_list.refresh()

class SeekBarWidget(QWidget):
    valueChanged = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(100)
        self.slider.setValue(0)
        self.slider.valueChanged.connect(self.emit_value_changed)

        self.scenes = {'busy': set([]), 'free': set([])}

        self.prev_button = QPushButton("◀")
        self.next_button = QPushButton("▶")

        self.prev_button.pressed.connect(self.start_prev_timer)
        self.prev_button.released.connect(self.stop_timer_and_update)
        self.next_button.pressed.connect(self.start_next_timer)
        self.next_button.released.connect(self.stop_timer_and_update)

        self.timer = QTimer(self)
        self.timer.setInterval(100)  # msec
        self.timer.timeout.connect(self.update_index)

        self.increment = 0
        self.long_press_detected = False

        layout = QHBoxLayout()
        layout.addWidget(self.prev_button)
        layout.addWidget(self.slider)
        layout.addWidget(self.next_button)

        self.setLayout(layout)

    def start_next_timer(self):
        self.increment = 1
        self.long_press_detected = False
        self.timer.start()

    def start_prev_timer(self):
        self.increment = -1
        self.long_press_detected = False
        self.timer.start()

    def stop_timer_and_update(self):
        self.timer.stop()
        if not self.long_press_detected:
            value = self.slider.value()
            self.slider.setValue(max(value + self.increment, self.slider.minimum()))
    
    def update_index(self):
        self.long_press_detected = True
        value = self.slider.value()
        self.slider.setValue(max(value + self.increment, self.slider.minimum()))
    
    def reset_scenes(self):
        self.scenes = {'busy': set([]), 'free': set([])}
        self.repaint()

    def emit_value_changed(self, value):
        self.valueChanged.emit(value)
    
    def set_maxvalue(self, value):
        self.slider.setMaximum(value)
    
    def get_value(self):
        return self.slider.value()
    
    def get_value_str(self):
        return f"{self.slider.value():05d}"
    
    def set_value(self, value):
        self.slider.setValue(value)
    
    def add_busy_scene(self):
        self.scenes['busy'].add(self.slider.value())

    def add_free_scene(self):
        self.scenes['free'].add(self.slider.value())
    
    def remove_busy_scene(self, value):
        self.scenes['busy'].remove(value)

    def remove_free_scene(self, value):
        self.scenes['free'].remove(value)
    
    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)

        slider_rect = self.slider.geometry()
        slider_min = self.slider.minimum()
        slider_max = self.slider.maximum()
        pen_free = QPen(QColor("green"), 2)
        pen_busy = QPen(QColor("red"), 2)

        for key, scenes_set in self.scenes.items():
            if key == 'free':
                painter.setPen(pen_free)
            if key == 'busy':
                painter.setPen(pen_busy)
            for scene in scenes_set:
                marker = slider_rect.left() + slider_rect.width() * (scene - slider_min) / (slider_max - slider_min)
                marker = int(marker)
                painter.drawLine(marker, slider_rect.top(), marker, slider_rect.bottom())

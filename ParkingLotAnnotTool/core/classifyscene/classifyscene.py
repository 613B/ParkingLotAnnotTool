import cv2

from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

from ParkingLotAnnotTool.utils.resource import read_icon
from ParkingLotAnnotTool.utils.signal import *
from ParkingLotAnnotTool.utils.trace import traceback_and_exit
from .action import new_action
from .canvas import CanvasPicture, CanvasScroll
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
        self.busy_action = new_action(self, 'Busy', icon_text='Busy', slot=self.click_busy, checkable=True)
        self.free_action = new_action(self, 'Free', icon_text='Free', slot=self.click_free, checkable=True)
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
        self.toolbar.addAction(self.view_zoom_fit_action)
        self.toolbar.addAction(self.view_zoom_1_action)

        self.lot_list = QListWidget(self)
        self.lot_list.itemSelectionChanged.connect(self.on_lotlist_itemselection_changed)
        self.scene_list = QListWidget(self)

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
        self.view_zoom_fit_action.setEnabled(False)
        self.view_zoom_1_action.setEnabled(False)

    def disable_add_preset(self) -> None:
        self.editable = True
        self.set_action.setEnabled(True)
        self.save_action.setEnabled(True)
        self.free_action.setEnabled(True)
        self.busy_action.setEnabled(True)
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
        self.scene_list.addItems(self.scene_data.get_frame_names())

    def click_save(self) -> None:
        traceback_and_exit(self.click_save_impl)
    def click_save_impl(self) -> None:
        self.scene_data.save()

    def click_free(self) -> None:
        traceback_and_exit(self.click_free_impl)
    def click_free_impl(self) -> None:
        self.seekbar.add_free_scene()

    def click_busy(self) -> None:
        traceback_and_exit(self.click_busy_impl)
    def click_busy_impl(self) -> None:
        self.seekbar.add_busy_scene()

    def press_view_zoom_fit(self) -> None:
        traceback_and_exit(self.press_view_zoom_fit_impl)
    def press_view_zoom_fit_impl(self) -> None:
        self.canvas_scroll.fit_window()

    def press_view_zoom_1(self) -> None:
        traceback_and_exit(self.press_view_zoom_1_impl)
    def press_view_zoom_1_impl(self) -> None:
        self.canvas_scroll.set_zoom(100)

    def on_seekbar_value_changed(self, value):
        img = cv2.imread(self.scene_data.lot_dirs[0] / self.scene_data.frame_names[value], cv2.IMREAD_COLOR)
        self.canvas_picture.set_picture(img)
    
    def on_lotlist_itemselection_changed(self):
        selected_items = self.lot_list.selectedItems()
        frame_idx = self.seekbar.get_value()
        img = cv2.imread(self.scene_data.parent_dir / selected_items[0].text() / self.scene_data.frame_names[frame_idx], cv2.IMREAD_COLOR)
        self.canvas_picture.set_picture(img)

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

        self.prev_button.clicked.connect(self.step_backward)
        self.next_button.clicked.connect(self.step_forward)

        layout = QHBoxLayout()
        layout.addWidget(self.prev_button)
        layout.addWidget(self.slider)
        layout.addWidget(self.next_button)

        self.setLayout(layout)

    def emit_value_changed(self, value):
        self.valueChanged.emit(value)

    def step_backward(self):
        value = self.slider.value()
        self.slider.setValue(max(value - 1, self.slider.minimum()))

    def step_forward(self):
        value = self.slider.value()
        self.slider.setValue(min(value + 1, self.slider.maximum()))
    
    def set_maxvalue(self, value):
        self.slider.setMaximum(value)
    
    def get_value(self):
        return self.slider.value()
    
    def set_value(self, value):
        self.slider.setValue(value)
    
    def add_busy_scene(self):
        self.scenes['busy'].add(self.slider.value())

    def add_free_scene(self):
        self.scenes['free'].add(self.slider.value())
    
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

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
        self.draw_action = new_action(self, 'Busy', icon_text='Busy', slot=self.click_draw, checkable=True)
        self.none_action = new_action(self, 'Free', icon_text='Free', slot=self.click_none, checkable=True)
        self.view_zoom_fit_action = new_action(self, 'Zoom Fit', icon=read_icon('zoom_fit.png'), slot=self.press_view_zoom_fit)
        self.view_zoom_1_action = new_action(self, 'Zoom 100%', icon=read_icon('zoom_1.png'), slot=self.press_view_zoom_1)
        self.toolbar = QToolBar()
        self.toolbar.setOrientation(Qt.Orientation.Vertical)
        self.toolbar.addAction(self.open_action)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.save_action)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.none_action)
        self.toolbar.addAction(self.draw_action)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.view_zoom_fit_action)
        self.toolbar.addAction(self.view_zoom_1_action)

        self.lot_list = LotList(self)
        self.scene_list = SceneList(self)

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
        self.none_action.setEnabled(False)
        self.draw_action.setEnabled(False)
        self.view_zoom_fit_action.setEnabled(False)
        self.view_zoom_1_action.setEnabled(False)

    def disable_add_preset(self) -> None:
        self.editable = True
        self.set_action.setEnabled(True)
        self.save_action.setEnabled(True)
        self.none_action.setEnabled(True)
        self.draw_action.setEnabled(True)
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

    def click_save(self) -> None:
        traceback_and_exit(self.click_save_impl)
    def click_save_impl(self) -> None:
        self.scene_data.save()

    def click_none(self) -> None:
        traceback_and_exit(self.click_none_impl)
    def click_none_impl(self) -> None:
        self.check_canvastool(CANVASTOOL_NONE)

    def click_draw(self) -> None:
        traceback_and_exit(self.click_draw_impl)
    def click_draw_impl(self) -> None:
        self.check_canvastool(CANVASTOOL_DRAW)

    def press_view_zoom_fit(self) -> None:
        traceback_and_exit(self.press_view_zoom_fit_impl)
    def press_view_zoom_fit_impl(self) -> None:
        self.canvas_scroll.fit_window()

    def press_view_zoom_1(self) -> None:
        traceback_and_exit(self.press_view_zoom_1_impl)
    def press_view_zoom_1_impl(self) -> None:
        self.canvas_scroll.set_zoom(100)

    def clear_canvastool(self) -> None:
        self.none_action.setChecked(False)
        self.draw_action.setChecked(False)

    def check_canvastool(self, tool) -> None:
        self.clear_canvastool()
        if   tool == CANVASTOOL_NONE:
            self.none_action.setChecked(True)
        elif tool == CANVASTOOL_DRAW:
            self.draw_action.setChecked(True)
        else:
            raise RuntimeError(f'tool={tool}')

    def get_canvastool(self) -> None:
        if self.none_action.isChecked():
            return CANVASTOOL_NONE
        if self.draw_action.isChecked():
            return CANVASTOOL_DRAW
        raise RuntimeError('no tool is checked')

    def on_seekbar_value_changed(self, value):
        img = cv2.imread(self.scene_data.lot_dirs[0] / self.scene_data.frame_names[value], cv2.IMREAD_COLOR)
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

class DisableChangedSignal:

    def __init__(self, custom_list):
        self.l = custom_list
        self.enable = custom_list.connect_changed_flag

    def __enter__(self):
        if self.enable:
            self.l.disconnect_changed()

    def __exit__(self, exc_type, exc_value, traceback):
        if self.enable:
            self.l.connect_changed()


class LotList(QListWidget):

    def __init__(self, parent: ClassifySceneWidget):
        super(LotList, self).__init__(parent)

        self.p = parent

        self.connect_changed_flag: bool = False
        self.connect_changed()

        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setMaximumWidth(200)
    
    def connect_changed(self):
        qt_connect_signal_safely(
            self.currentItemChanged, self.changed)
        self.connect_changed_flag = True
    
    def disconnect_changed(self) -> None:
        qt_disconnect_signal_safely(
            self.currentItemChanged, self.changed)
        self.connect_changed_flag = False

    def get_selected_lidx(self):
        idx = self.currentRow()
        return idx if (0 <= idx) else None

    def set_selected_lidx(self, idx):
        with DisableChangedSignal(self):
            if idx is None:
                self.setCurrentRow(-1)
                return
            self.setCurrentRow(idx)

    def refresh(self) -> None:
        with DisableChangedSignal(self):

            self.clear()
            lots = self.p.scene_data.get_lots()
            for _, lot in enumerate(lots):
                self.addItem(f"{lot['id']}")
            select_idx = self.get_selected_lidx()
            if (select_idx is not None) and \
               (select_idx < self.count()):
                self.setCurrentRow(select_idx)
            else:
                self.setCurrentRow(-1)

            self.changed_impl()

    def changed(self) -> None:
        traceback_and_exit(self.changed_impl)
    def changed_impl(self) -> None:
        self.p.canvas.set_selected_lidx(self.get_selected_lidx())

    def clear_list(self):
        if self.count() == 0:
            return
        self.clear()
        self.changed_impl()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key.Key_Escape:
            self.set_selected_lidx(None)


class SceneList(QListWidget):

    def __init__(self, parent: ClassifySceneWidget):
        super(SceneList, self).__init__(parent)

        self.p = parent

        self.connect_changed_flag: bool = False
        self.connect_changed()

        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setMaximumWidth(200)
    
    def connect_changed(self):
        qt_connect_signal_safely(
            self.currentItemChanged, self.changed)
        self.connect_changed_flag = True
    
    def disconnect_changed(self) -> None:
        qt_disconnect_signal_safely(
            self.currentItemChanged, self.changed)
        self.connect_changed_flag = False

    def get_selected_lidx(self):
        idx = self.currentRow()
        return idx if (0 <= idx) else None

    def set_selected_lidx(self, idx):
        with DisableChangedSignal(self):
            if idx is None:
                self.setCurrentRow(-1)
                return
            self.setCurrentRow(idx)

    def refresh(self) -> None:
        pass
        # with DisableChangedSignal(self):

        #     self.clear()
        #     lots = self.p.lots_data.get_lots()
        #     for _, lot in enumerate(lots):
        #         self.addItem(f"{lot['id']}")
        #     select_idx = self.get_selected_lidx()
        #     if (select_idx is not None) and \
        #        (select_idx < self.count()):
        #         self.setCurrentRow(select_idx)
        #     else:
        #         self.setCurrentRow(-1)

        #     self.changed_impl()

    def changed(self) -> None:
        traceback_and_exit(self.changed_impl)
    def changed_impl(self) -> None:
        self.p.canvas.set_selected_lidx(self.get_selected_lidx())

    def clear_list(self):
        if self.count() == 0:
            return
        self.clear()
        self.changed_impl()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        pass
        # if event.key() == Qt.Key.Key_Escape:
        #     self.set_selected_lidx(None)
        #     self.p.canvas.set_selected_lidx(None)
        # elif event.key() == Qt.Key.Key_Delete:
        #     lots_data = self.p.lots_data
        #     if not lots_data.loaded():
        #         return
        #     if self.p.editable is False:
        #         return
        #     if self.get_selected_lidx() is None:
        #         return
        #     lots_data.delete_area(self.get_selected_lidx())
        #     self.set_selected_lidx(None)
        #     self.p.canvas.set_selected_lidx(None)
        #     self.refresh()

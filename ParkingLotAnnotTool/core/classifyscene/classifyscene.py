import cv2

from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

from ParkingLotAnnotTool.public.signals import global_signals
from ParkingLotAnnotTool.utils.resource import read_icon
from ParkingLotAnnotTool.utils.trace import traceback_and_exit
from ..general.action import new_action
from ..general.canvas import CanvasPicture, CanvasScroll
from .scenedata import SceneData, SceneDataInfoWidget
from .seekbar import SeekBarWidget


class ClassifySceneWidget(QWidget):
    def __init__(self):
        super(ClassifySceneWidget, self).__init__()

        self.editable = True
        self.scene_data = SceneData()
        self.scene_data_info = SceneDataInfoWidget(self.scene_data)
        self.scene_data.current_frame_changed.connect(self.refresh)
        self.scene_data.data_changed.connect(self.refresh)
        self.scene_data.selected_lot_idx_changed.connect(self.refresh)
        self.scene_data.selected_scene_idx_changed.connect(self.refresh)

        self.canvas_picture = CanvasPicture()
        self.canvas_scroll = CanvasScroll(self, self.canvas_picture)
        self.seekbar = SeekBarWidget(self.scene_data)

        self.open_action = new_action(self, 'Open', icon=read_icon('open_file.png'), slot=self.click_open)
        self.save_action = new_action(self, 'Save', icon=read_icon('save.png'), slot=self.click_save, shortcut=QKeySequence("Ctrl+S"))
        self.free_action = new_action(self, 'Free', icon_text='Free', slot=self.click_free, shortcut=QKeySequence("1"))
        self.busy_action = new_action(self, 'Busy', icon_text='Busy', slot=self.click_busy, shortcut=QKeySequence("2"))
        self.occluded_action = new_action(self, 'Occluded', icon_text='Occluded', slot=self.click_occluded, shortcut=QKeySequence("3"))
        self.person_action = new_action(self, 'Person', icon_text='Person', slot=self.click_person, shortcut=QKeySequence("4"))
        self.ambiguous_action = new_action(self, 'Ambiguous', icon_text='Ambiguous', slot=self.click_ambiguous, shortcut=QKeySequence("5"))
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
        self.toolbar.addAction(self.occluded_action)
        self.toolbar.addAction(self.person_action)
        self.toolbar.addAction(self.ambiguous_action)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.view_zoom_fit_action)
        self.toolbar.addAction(self.view_zoom_1_action)

        self.lot_list = LotList(self.scene_data)
        self.scene_list = SceneList(self.scene_data)

        layout = QGridLayout(self)
        layout.addWidget(self.toolbar, 0, 0, 2, 1)  # (widget, row, col, row_size, col_size)
        layout.addWidget(self.canvas_scroll, 0, 1, 1, 1)
        layout.addWidget(self.scene_data_info, 0, 2, 1, 1)
        layout.addWidget(self.seekbar, 1, 1, 1, 2)
        layout.addWidget(self.scene_list, 0, 3, 2, 1)
        layout.addWidget(self.lot_list, 0, 4, 2, 1)
        self.setLayout(layout)

    def changed_zoom(self):
        traceback_and_exit(self.changed_zoom_impl)
    def changed_zoom_impl(self):
        self.canvas_picture.set_zoom(100)

    def click_open(self) -> None:
        traceback_and_exit(self.click_open_impl)
    def click_open_impl(self) -> None:
        file_path = QFileDialog.getOpenFileName(self, "Open File", "", "scene.json (scene.json)")
        if file_path == ('', ''):
            return
        self.scene_data.set_json_path(file_path[0])
        self.scene_data.load()
        global_signals.print(f"[{self.__class__.__name__}] open: {file_path[0]}")
        self.seekbar.set_maxvalue(self.scene_data.len_frames()-1)
        self.canvas_picture.set_picture(self.scene_data.current_lot_img())
        self.canvas_scroll.fit_window()

    def click_save(self) -> None:
        traceback_and_exit(self.click_save_impl)
    def click_save_impl(self) -> None:
        global_signals.print(f"[{self.__class__.__name__}] save.")
        self.scene_data.save()

    def click_free(self) -> None:
        traceback_and_exit(self.click_free_impl)
    def click_free_impl(self) -> None:
        self.scene_data.add_scene("free")

    def click_busy(self) -> None:
        traceback_and_exit(self.click_busy_impl)
    def click_busy_impl(self) -> None:
        self.scene_data.add_scene("busy")

    def click_occluded(self) -> None:
        traceback_and_exit(self.click_occluded_impl)
    def click_occluded_impl(self) -> None:
        self.scene_data.add_occluded_flag()

    def click_person(self) -> None:
        traceback_and_exit(self.click_person_impl)
    def click_person_impl(self) -> None:
        self.scene_data.add_person_flag()

    def click_ambiguous(self) -> None:
        traceback_and_exit(self.click_ambiguous_impl)
    def click_ambiguous_impl(self) -> None:
        self.scene_data.add_ambiguous_flag()

    def press_view_zoom_fit(self) -> None:
        traceback_and_exit(self.press_view_zoom_fit_impl)
    def press_view_zoom_fit_impl(self) -> None:
        self.canvas_scroll.fit_window()

    def press_view_zoom_1(self) -> None:
        traceback_and_exit(self.press_view_zoom_1_impl)
    def press_view_zoom_1_impl(self) -> None:
        self.canvas_scroll.set_zoom(100)

    def refresh(self):
        self.canvas_picture.set_picture(self.scene_data.current_lot_img())
        prev_scene = self.scene_data.prev_scene()
        if prev_scene is None:
            return
        prev_label = prev_scene["label"]
        prev_flags = prev_scene["flags"]
        if   prev_label is None:
            self.busy_action.setEnabled(True)
            self.free_action.setEnabled(True)
        elif prev_label == "free":
            self.busy_action.setEnabled(True)
            self.free_action.setEnabled(False)
        elif prev_label == "busy":
            self.busy_action.setEnabled(False)
            self.free_action.setEnabled(True)

        if not prev_flags:
            self.occluded_action.setEnabled(True)
            self.person_action.setEnabled(True)
            self.ambiguous_action.setEnabled(True)
            return
        for prev_flag in prev_flags:
            if prev_flag == "occluded":
                self.occluded_action.setEnabled(False)
            if prev_flag == "person":
                self.person_action.setEnabled(False)
            if prev_flag == "ambiguous":
                self.ambiguous_action.setEnabled(False)

class SignalBlocker:
    def __init__(self, widget):
        self.widget = widget

    def __enter__(self):
        self.widget.blockSignals(True)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.widget.blockSignals(False)


class LotList(QListWidget):

    def __init__(self, scene_data: SceneData, parent=None):
        super(LotList, self).__init__(parent)
        self._scene_data = scene_data
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setMaximumWidth(200)
        self.currentRowChanged.connect(self.on_current_row_changed)
        self._scene_data.data_loaded.connect(self.update)

    # Callback
    def update(self) -> None:
        with SignalBlocker(self):
            for lot_id in self._scene_data.lot_ids():
                self.addItem(lot_id)
                self.setCurrentRow(self._scene_data.selected_lot_idx())

    def keyPressEvent(self, event: QKeyEvent) -> None:
        pass

    def on_current_row_changed(self):
        self._scene_data.set_selected_lot_idx(self.currentRow())


class SceneList(QListWidget):

    def __init__(self, scene_data: SceneData, parent=None):
        super(SceneList, self).__init__(parent)
        self._scene_data = scene_data
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setMaximumWidth(200)
        self.currentRowChanged.connect(self.on_current_row_changed)
        self._scene_data.selected_lot_idx_changed.connect(self.update)
        self._scene_data.data_loaded.connect(self.update)
        self._scene_data.data_changed.connect(self.update)

    # Callback
    def update(self) -> None:
        with SignalBlocker(self):
            self.clear()
            for scene in self._scene_data.scenes_with_current_lot_id():
                self.addItem(f'{scene["label"]}, {scene["frame"]}')
            if self._scene_data.selected_scene_idx() is None:
                self.setCurrentRow(-1)
            else:
                self.setCurrentRow(self._scene_data.selected_scene_idx())

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key.Key_Escape:
            self._scene_data.set_selected_scene_idx(None)
        elif event.key() == Qt.Key.Key_Delete:
            self._scene_data.remove_selected_scene()

    def on_current_row_changed(self):
        self._scene_data.set_selected_scene_idx(self.currentRow())

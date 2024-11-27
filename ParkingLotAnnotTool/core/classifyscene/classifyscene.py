import cv2

from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

from ParkingLotAnnotTool.utils.resource import read_icon
from ParkingLotAnnotTool.utils.signal import *
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
        self.scene_data.current_frame_changed.connect(self.scene_data_info.update)
        self.scene_data.current_lot_id_changed.connect(self.scene_data_info.update)

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
        print(file_path)
        if file_path == ('', ''):
            return
        self.scene_data.set_json_path(file_path[0])
        self.scene_data.load()
        self.seekbar.set_maxvalue(self.scene_data.len_frames()-1)
        img = cv2.imread(self.scene_data.lot_dirs()[0] / self.scene_data.frame_names()[0], cv2.IMREAD_COLOR)
        self.canvas_picture.set_picture(img)
        self.canvas_scroll.fit_window()
        self.lot_list.addItems([lot['id'] for lot in self.scene_data.lots()])
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
        self.scene_list.addItem(f'free, {self.seekbar.get_value_str()}')
        self.scene_data.add_scene(
            key=self.lot_list.selectedItems()[0].text(),
            scene={"label": "free", "frame": self.seekbar.get_value_str()})

    def click_busy(self) -> None:
        traceback_and_exit(self.click_busy_impl)
    def click_busy_impl(self) -> None:
        if self.scene_list.findItems(self.seekbar.get_value_str(), Qt.MatchFlag.MatchContains):
            return
        self.busy_action.setEnabled(False)
        self.free_action.setEnabled(True)
        self.seekbar.add_busy_scene()
        self.scene_list.addItem(f'busy, {self.seekbar.get_value_str()}')
        self.scene_data.add_scene(
            key=self.lot_list.selectedItems()[0].text(),
            scene={"label": "busy", "frame": self.seekbar.get_value_str()})

    def click_undo(self) -> None:
        traceback_and_exit(self.click_undo_impl)
    def click_undo_impl(self) -> None:
        if self.scene_list.count() <= 0:
            return
        last_item = self.scene_list.takeItem(self.scene_list.count() - 1)
        parts = last_item.text().split(", ")
        label = parts[0]
        frame = parts[1]
        if   label == "busy":
            self.seekbar.remove_busy_scene(int(frame))
            self.busy_action.setEnabled(True)
            self.free_action.setEnabled(False)
            self.scene_data.remove_scene(
                key=self.lot_list.selectedItems()[0].text(),
                scene={"label": "busy", "frame": frame})
        elif label == "free":
            self.seekbar.remove_free_scene(int(frame))
            self.busy_action.setEnabled(False)
            self.free_action.setEnabled(True)
            self.scene_data.remove_scene(
                key=self.lot_list.selectedItems()[0].text(),
                scene={"label": "free", "frame": frame})
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
        img = cv2.imread(self.scene_data.parent_dir() / selected_items[0].text() / self.scene_data.frame_names()[value], cv2.IMREAD_COLOR)
        self.canvas_picture.set_picture(img)
        self.scene_data.update_current_frame(self.seekbar.get_value_str())

    def on_lotlist_itemselection_changed(self):
        selected_items = self.lot_list.selectedItems()
        frame_idx = self.seekbar.get_value()
        lot_id = selected_items[0].text()
        self.scene_data.update_current_lot_id(lot_id)
        img = cv2.imread(self.scene_data.parent_dir() / lot_id / self.scene_data.frame_names()[frame_idx], cv2.IMREAD_COLOR)
        self.canvas_picture.set_picture(img)
        self.scene_list.clear()
        self.seekbar.reset_scenes()
        scenes = self.scene_data.scenes()[lot_id]
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
                self.scene_list.addItem(f'busy, {scene["frame"]}')
            elif scene["label"] == "free":
                self.seekbar.add_free_scene()
                self.scene_list.addItem(f'free, {scene["frame"]}')

    def on_scenelist_itemselection_changed(self):
        selected_items = self.scene_list.selectedItems()
        if not selected_items:
            return
        current_lot = self.lot_list.currentItem()
        parts = selected_items[0].text().split(", ")
        label = parts[0]
        frame = parts[1]
        img = cv2.imread(self.scene_data.parent_dir() / current_lot.text() / (frame + ".jpg"), cv2.IMREAD_COLOR)
        self.canvas_picture.set_picture(img)
        self.seekbar.set_value(int(frame))
        if   label == "busy":
            self.busy_action.setEnabled(False)
            self.free_action.setEnabled(True)
        elif label == "free":
            self.busy_action.setEnabled(True)
            self.free_action.setEnabled(False)

    def refresh(self) -> None:
        self.lot_list.refresh()

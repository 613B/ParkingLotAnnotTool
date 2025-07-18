import cv2
import json
from pathlib import Path

from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6.QtWidgets import QDialogButtonBox as QDBB

from ParkingLotAnnotTool.public.signals import global_signals
from ParkingLotAnnotTool.utils.geometry import is_polygon_convex
from ParkingLotAnnotTool.utils.resource import read_icon
from ParkingLotAnnotTool.utils.trace import traceback_and_exit
from ..general.canvas import CanvasPicture, CanvasScroll
from ..general.action import new_action
from .lotsdata import LotsData, LotsDataInfoWidget
from .imgcrop import ImageCropWorker
from .videoextract import VideoExtractWorker

epsilon = 16.0
area_init_size = 100.0
point_size = 8

lot_default_fill_color       = QColor(  0, 128, 255, 155)
lot_highlighted_fill_color   = QColor(  0,   0, 255, 200)
lot_selected_fill_color      = QColor(  0,   0, 255, 128)
lot_cropped_fill_color       = QColor(  0, 255,   0, 128)
point_default_fill_color     = QColor(255,   0,   0, 128)
point_highlighted_fill_color = QColor(255, 153,   0, 255)

class DefineQuadWidget(QWidget):

    def __init__(self):
        super(DefineQuadWidget, self).__init__()

        self.editable = True
        self.lots_data = LotsData()
        self.lots_data_info = LotsDataInfoWidget(self.lots_data)

        self.canvas = Canvas(self.lots_data)
        self.canvas_picture = CanvasPicture()
        self.canvas_picture.key_press_event_sig.connect(self.canvas.key_press_event)
        self.canvas_picture.mouse_double_click_sig.connect(self.canvas.mouse_double_click_event)
        self.canvas_picture.mouse_move_event_sig.connect(self.canvas.mouse_move_event)
        self.canvas_picture.mouse_press_event_sig.connect(self.canvas.mouse_press_event)
        self.canvas_picture.mouse_release_event_sig.connect(self.canvas.mouse_release_event)
        self.canvas_picture.paint_event_sig.connect(self.canvas.paint_event)
        self.canvas_scroll = CanvasScroll(self, self.canvas_picture)

        self.open_action = new_action(self, 'Open', icon=read_icon('open_file.png'), slot=self.click_open)
        self.save_action = new_action(self, 'Save', icon=read_icon('save.png'), slot=self.click_save, shortcut=QKeySequence("Ctrl+S"))
        self.draw_action = new_action(self, 'Draw', icon=read_icon('draw.png'), slot=self.click_draw, checkable=True)
        self.none_action = new_action(self, 'None', icon=read_icon('arrow.png'), slot=self.click_none, checkable=True)
        self.extract_frames_action = new_action(self, 'Extract frames', icon=read_icon('film.png'), slot=self.click_extract_frames)
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
        self.toolbar.addAction(self.extract_frames_action)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.view_zoom_fit_action)
        self.toolbar.addAction(self.view_zoom_1_action)

        self.lot_list = LotList(self.lots_data)
        layout = QHBoxLayout(self)
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas_scroll)
        layout.addWidget(self.lots_data_info)
        layout.addWidget(self.lot_list)
        self.setLayout(layout)

        self.click_none_impl()

    def changed_zoom(self):
        traceback_and_exit(self.changed_zoom_impl)
    def changed_zoom_impl(self):
        self.canvas_picture.set_zoom(100)

    def click_open(self) -> None:
        traceback_and_exit(self.click_open_impl)
    def click_open_impl(self) -> None:
        file_filter_img = "images (*.png *.PNG *.jpg *.jpeg *.JPG *.JPEG)"
        file_filter_json = "json (*.json *.JSON)"
        file_filter = f'{file_filter_img};;{file_filter_json}'
        file_path = QFileDialog.getOpenFileName(self, "Open File", "", file_filter)
        print(file_path)
        if file_path == ('', ''):
            return
        if   file_path[1] == file_filter_img:
            image_path = file_path[0]
            self.lots_data.set_image_path(image_path)
        elif file_path[1] == file_filter_json:
            self.lots_data.set_json_path(file_path[0])
            self.lots_data.load()
            image_path = self.lots_data.image_path()
        global_signals.print(f"[{self.__class__.__name__}] open: {image_path}")
        img = cv2.imread(image_path, cv2.IMREAD_COLOR)
        self.canvas_picture.set_picture(img)
        self.canvas_scroll.fit_window()

    def click_save(self) -> None:
        traceback_and_exit(self.click_save_impl)
    def click_save_impl(self) -> None:
        global_signals.print(f"[{self.__class__.__name__}] save.")
        if self.lots_data.json_path() is None:
            file_path, _ = QFileDialog.getSaveFileName(self, "Save File", "", "Json File (*.json)")
            self.lots_data.set_json_path(file_path)
        else:
            self.lots_data.save()

    def clear_canvastool(self) -> None:
        self.none_action.setChecked(False)
        self.draw_action.setChecked(False)

    def click_none(self) -> None:
        traceback_and_exit(self.click_none_impl)
    def click_none_impl(self) -> None:
        self.clear_canvastool()
        self.none_action.setChecked(True)
        self.lots_data.set_addable(False)
        self.lots_data.set_editable(True)

    def click_draw(self) -> None:
        traceback_and_exit(self.click_draw_impl)
    def click_draw_impl(self) -> None:
        self.clear_canvastool()
        self.draw_action.setChecked(True)
        self.lots_data.set_addable(True)
        self.lots_data.set_editable(False)

    def video_extraction_start(self, video_path: Path, outdir_path: Path, interval):
        self.progress_dialog = QProgressDialog("Extracting frames...", "Cancel", 0, 100, self)
        self.videoextract_worker = VideoExtractWorker(video_path, outdir_path, interval)

        self.progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
        self.progress_dialog.canceled.connect(self.videoextract_worker.cancel)
        self.progress_dialog.show()
        self.videoextract_worker.progress.connect(self.progress_dialog.setValue)
        self.videoextract_worker.finished.connect(self.image_cropping_start)
        self.videoextract_worker.canceled.connect(self.progress_dialog.close)
        if outdir_path.exists():
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Icon.Question)
            msg_box.setWindowTitle('Skip?')
            msg_box.setText('Your video may have already been extracted. Do you want to skip this step?')
            msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            msg_box.setDefaultButton(QMessageBox.StandardButton.Yes)
            result = msg_box.exec()
            if result == QMessageBox.StandardButton.Yes:
                self.videoextract_worker.finished.emit()
            else:
                self.videoextract_worker.start()
        else:
            self.videoextract_worker.start()

    def image_cropping_start(self):
        self.imagecrop_worker = ImageCropWorker(self.scene_json_path)

        self.progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
        self.progress_dialog.canceled.connect(self.imagecrop_worker.cancel)
        self.progress_dialog.setLabelText("Cropping images...")
        self.progress_dialog.show()
        self.imagecrop_worker.progress.connect(self.progress_dialog.setValue)
        self.imagecrop_worker.finished.connect(self.progress_dialog.close)
        self.imagecrop_worker.canceled.connect(self.progress_dialog.close)
        self.imagecrop_worker.start()

    def click_extract_frames(self) -> None:
        traceback_and_exit(self.click_extract_frames_impl)
    def click_extract_frames_impl(self) -> None:
        self.lots_data.may_save()
        if not self.lots_data.loaded():
            QMessageBox.information(
                self, "Info",
                "Image is not loaded. Or it has never been saved.")
            return
        lots = self.lots_data.get_crop_lots()
        if lots == []:
            QMessageBox.information(
                self, "Info",
                "Lots are not set. Set them with 'Draw' mode.")
            return
        path = QFileDialog.getOpenFileName(self, "Open Video File", "", "video (*.mp4)")
        if path == ('', ''):
            return
        video_path = Path(path[0])
        path = QFileDialog.getExistingDirectory(self, "Output Directory", "")
        if path == '':
            return
        outdir_path = Path(path)
        interval, ok = QInputDialog.getInt(self, "Extract Interval", "Enter the interval[sec]:", 60, 0, 100, 1)
        if not ok:
            return

        self.scene_json_path = outdir_path / "scene.json"
        if self.scene_json_path.exists():
            with open(self.scene_json_path, 'r', encoding='utf-8') as file:
                scenes_data = json.load(file)
            scenes_data["lots"] = self.lots_data.get_crop_lots()
        else:
            scenes_data = {
                "version": "0.3",
                "video_path": str(video_path),
                "lots": self.lots_data.get_crop_lots(),
                "scenes": {},
                "difficult_frames": {}
            }

        for lot in self.lots_data.get_crop_lots():
            if lot["id"] not in scenes_data["scenes"]:
                scenes_data["scenes"][lot["id"]] = []
            if lot["id"] not in scenes_data["difficult_frames"]:
                scenes_data["difficult_frames"][lot["id"]] = []

        with open(self.scene_json_path, 'w', encoding='utf-8') as file:
            json.dump(scenes_data, file, ensure_ascii=False, indent=4)

        conditions_json_path = outdir_path / "conditions.json"
        conditions_data = {
            "version": "0.3",
            "video_path": str(video_path),
            "conditions": [],
            "initial_time": None,
            "day_start_time": None,
            "night_start_time": None,
            "interval": str(interval),
        }
        with open(conditions_json_path, 'w', encoding='utf-8') as file:
            json.dump(conditions_data, file, ensure_ascii=False, indent=4)

        raw_dir_path = outdir_path / "raw"
        self.video_extraction_start(video_path, raw_dir_path, interval)

    def press_view_zoom_fit(self) -> None:
        traceback_and_exit(self.press_view_zoom_fit_impl)
    def press_view_zoom_fit_impl(self) -> None:
        self.canvas_scroll.fit_window()

    def press_view_zoom_1(self) -> None:
        traceback_and_exit(self.press_view_zoom_1_impl)
    def press_view_zoom_1_impl(self) -> None:
        self.canvas_scroll.set_zoom(100)


class AddLotDialog(QDialog):

    def __init__(self, lots_data: LotsData, parent=None):
        super(AddLotDialog, self).__init__(parent)
        self.lots_data = lots_data
        self.setWindowTitle('Add Lot')
        self.setWindowFlags(
            self.windowFlags() &
            ~Qt.WindowType.WindowContextHelpButtonHint)

        self.label_id = QLabel('ID')
        self.ledit_id = QLineEdit()

        self.bb = QDBB(QDBB.StandardButton.Ok, self)
        self.bb.accepted.connect(self.accept)

        layout = QVBoxLayout()
        gl = QGridLayout()
        gl.addWidget(self.label_id, 0, 0)
        gl.addWidget(self.ledit_id, 0, 1)
        layout.addLayout(gl)
        layout.addWidget(self.bb)
        self.setLayout(layout)

    def popup(self,
              mouse_pressed_x,
              mouse_pressed_y,
              mouse_x,
              mouse_y):
        try:
            if self.exec() == 0:
                return
            lot_id = self.ledit_id.text()
            xmin = min(mouse_pressed_x, mouse_x)
            ymin = min(mouse_pressed_y, mouse_y)
            xmax = max(mouse_pressed_x, mouse_x)
            ymax = max(mouse_pressed_y, mouse_y)
            self.lots_data.add_lot(
                lot_id,
                xmin, ymin,
                xmax, ymin,
                xmax, ymax,
                xmin, ymax)
        except RuntimeError:
            # signals.print(f'Add Lot failed. {e}.')
            pass


class Canvas:

    def __init__(self, lots_data: LotsData, parent=None):

        self.lots_data = lots_data
        self.add_lot_dialog = AddLotDialog(self.lots_data)
        self.highlighted_lidx = None
        self.highlighted_pidx = None
        self.mouse_x = None
        self.mouse_y = None
        self.mouse_pressed = False
        self.mouse_pressed_x = None
        self.mouse_pressed_y = None
        self.mouse_pressed_on_lot = False
        self.mouse_pressed_on_point = False

    def key_press_event(self, event: QKeyEvent):
        traceback_and_exit(self.key_press_event_impl, event=event)
    def key_press_event_impl(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Escape:
            self.lots_data.set_selected_idx(None)
        elif event.key() == Qt.Key.Key_Delete:
            self.lots_data.delete_selected_area()

    def mouse_double_click_event(self, event: QMouseEvent, pos: QPointF, scale: float) -> None:
        traceback_and_exit(self.mouse_double_click_event_impl, event=event, pos=pos, scale=scale)
    def mouse_double_click_event_impl(self, event: QMouseEvent, pos: QPointF, scale: float) -> None:
        pass

    def mouse_move_event(self, event: QMouseEvent, pos: QPointF, scale: float) -> None:
        traceback_and_exit(self.mouse_move_event_impl, event=event, pos=pos, scale=scale)
    def mouse_move_event_impl(self, event: QMouseEvent, pos: QPointF, scale: float) -> None:
        mouse_x = pos.x()
        mouse_y = pos.y()

        if self.mouse_pressed_on_point:
            points = self.lots_data.get_points_by_idx(self.highlighted_lidx)
            points[self.highlighted_pidx] = [mouse_x, mouse_y]
            quad_is_convex = is_polygon_convex(
                [points[0][0], points[1][0], points[2][0], points[3][0]],
                [points[0][1], points[1][1], points[2][1], points[3][1]])
            if not quad_is_convex:
                return
            self.lots_data.set_point_by_idx(
                self.highlighted_lidx,
                self.highlighted_pidx,
                mouse_x,
                mouse_y)
        elif (self.lots_data.is_editable()) and \
             (self.mouse_pressed_on_lot) and \
             (not self.mouse_pressed_on_point):
            self.lots_data.move_lot_by_idx(
                self.highlighted_lidx,
                mouse_x - self.mouse_x,
                mouse_y - self.mouse_y)
        else:
            self.highlighted_lidx = None
            self.highlighted_pidx = None
            lidx_in = self.lots_data.is_point_in_quad(pos.x(), pos.y())
            dist, lidx, pidx = self.lots_data.nearest_point(pos.x(), pos.y())
            if dist is not None:
                if dist < epsilon / scale:
                    self.highlighted_lidx = lidx
                    self.highlighted_pidx = pidx
                else:
                    if lidx_in is not None:
                        self.highlighted_lidx = lidx_in
                        self.highlighted_pidx = None

        self.mouse_x = pos.x()
        self.mouse_y = pos.y()

    def mouse_press_event(self, event: QMouseEvent, pos: QPointF, scale: float) -> None:
        traceback_and_exit(self.mouse_press_event_impl, event=event, pos=pos, scale=scale)
    def mouse_press_event_impl(self, event: QMouseEvent, pos: QPointF, scale: float) -> None:

        if event.button() == Qt.MouseButton.LeftButton:
            self.mouse_pressed = True
            if (self.highlighted_lidx is not None):
                self.mouse_pressed_on_lot = True
            if (self.highlighted_pidx is not None):
                self.mouse_pressed_on_point = True

        self.mouse_pressed_x = pos.x()
        self.mouse_pressed_y = pos.y()

        if (event.button() == Qt.MouseButton.LeftButton) and \
           (self.mouse_pressed_on_lot):
            self.lots_data.set_selected_idx(self.highlighted_lidx)

    def mouse_release_event(self, event: QMouseEvent, pos: QPointF, scale: float) -> None:
        traceback_and_exit(self.mouse_release_event_impl, event=event, pos=pos, scale=scale)
    def mouse_release_event_impl(self, event: QMouseEvent, pos: QPointF, scale: float) -> None:
        if (self.lots_data.is_addable()) and \
           (event.button() == Qt.MouseButton.LeftButton) and \
           (self.mouse_pressed_x is not None) and \
           (self.mouse_pressed_y is not None) and \
           (not self.mouse_pressed_on_lot) and \
           (not self.mouse_pressed_on_point):
            self.add_lot_dialog.popup(
                self.mouse_pressed_x, self.mouse_pressed_y,
                pos.x(), pos.y())

        if event.button() == Qt.MouseButton.LeftButton:
            self.mouse_pressed = False
            self.mouse_pressed_on_lot = False
            self.mouse_pressed_on_point = False

    def paint_event(self, event: QPaintEvent, painter: QPainter, scale: float) -> None:
        traceback_and_exit(self.paint_event_impl, event=event, painter=painter, scale=scale)
    def paint_event_impl(self, event: QPaintEvent, painter: QPainter, scale: float) -> None:
        scale = scale
        p = painter

        lots = self.lots_data.lots()

        p.setPen(QPen(QColor(0, 0, 0, 0)))
        for lidx, lot in enumerate(lots):
            if lot['crop']:
                lot_fill_color = lot_cropped_fill_color
            else:
                lot_fill_color = lot_default_fill_color
            if   lidx == self.lots_data.selected_idx():
                lot_fill_color = lot_selected_fill_color
            elif lidx == self.highlighted_lidx:
                lot_fill_color = lot_highlighted_fill_color
            points = self.lots_data.get_points_by_idx(lidx)
            poly = QPolygonF([
                QPointF(points[0][0], points[0][1]),
                QPointF(points[1][0], points[1][1]),
                QPointF(points[2][0], points[2][1]),
                QPointF(points[3][0], points[3][1])])
            p.setBrush(QBrush(lot_fill_color))
            p.drawPolygon(poly)

        pen = QPen()
        pen.setWidth(max(1, int(round(2.0 / scale))))
        p.setPen(pen)
        for lidx, _ in enumerate(lots):
            points = self.lots_data.get_points_by_idx(lidx)
            for pidx, point in enumerate(points):
                point_fill_color = point_default_fill_color
                if (lidx == self.highlighted_lidx) and \
                   (pidx == self.highlighted_pidx):
                    point_fill_color = point_highlighted_fill_color
                point_path = QPainterPath()
                point_path.addEllipse(
                    point[0] - (point_size / scale) / 2.0,
                    point[1] - (point_size / scale) / 2.0,
                    point_size / scale,
                    point_size / scale)
                p.fillPath(point_path, point_fill_color)

        if (self.lots_data.is_addable()) and \
           (self.mouse_x is not None) and \
           (self.mouse_y is not None) and \
           (self.mouse_pressed) and \
           (self.mouse_pressed_x is not None) and \
           (self.mouse_pressed_y is not None) and \
           (not self.mouse_pressed_on_lot) and \
           (not self.mouse_pressed_on_point):
            p.setPen(QPen(QColor(0, 0, 0, 0)))
            xmin = min(self.mouse_x, self.mouse_pressed_x)
            ymin = min(self.mouse_y, self.mouse_pressed_y)
            xmax = max(self.mouse_x, self.mouse_pressed_x)
            ymax = max(self.mouse_y, self.mouse_pressed_y)
            poly = QPolygonF([
                QPointF(xmin, ymin),
                QPointF(xmax, ymin),
                QPointF(xmax, ymax),
                QPointF(xmin, ymax)])
            p.setBrush(QBrush(lot_default_fill_color))
            p.drawPolygon(poly)


class SignalBlocker:
    def __init__(self, widget):
        self.widget = widget

    def __enter__(self):
        self.widget.blockSignals(True)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.widget.blockSignals(False)


class LotListWidgetItem(QWidget):
    checkbox_state_changed = pyqtSignal(int, int)

    def __init__(self, id, idx, checked=False):
        super().__init__()
        self.idx = idx
        layout = QHBoxLayout()
        self.checkbox = QCheckBox()
        self.checkbox.setChecked(checked)
        self.label = QLabel(id)
        layout.addWidget(self.checkbox)
        layout.addWidget(self.label)
        layout.addStretch()
        left, top, right, bottom = layout.getContentsMargins()
        layout.setContentsMargins(left, int(top * 0.5), right, int(bottom * 0.5))
        self.setLayout(layout)

        self.checkbox.stateChanged.connect(
            self.emit_checkbox_state_changed)

    def emit_checkbox_state_changed(self, state):
        self.checkbox_state_changed.emit(self.idx, state)

class LotList(QListWidget):

    def __init__(self, lots_data: LotsData, parent=None):
        super(LotList, self).__init__(parent)
        self._lots_data = lots_data
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setMaximumWidth(200)
        self.currentRowChanged.connect(self.on_current_row_changed)
        self._lots_data.data_changed.connect(self.update)

    # Callback
    def update(self) -> None:
        with SignalBlocker(self):
            self.clear()
            for lidx, lot in enumerate(self._lots_data.lots()):
                row = LotListWidgetItem(f"{lot['id']}", lidx, lot['crop'])
                row.checkbox_state_changed.connect(self.handle_checkbox_state_changed)
                item = QListWidgetItem(self)
                item.setSizeHint(row.minimumSizeHint())
                self.setItemWidget(item, row)
            if self._lots_data.selected_idx() is None:
                self.setCurrentRow(-1)
            else:
                self.setCurrentRow(self._lots_data.selected_idx())

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key.Key_Escape:
            self._lots_data.set_selected_idx(None)
        elif event.key() == Qt.Key.Key_Delete:
            self._lots_data.delete_selected_area()

    def on_current_row_changed(self):
        self._lots_data.set_selected_idx(self.currentRow())

    def handle_checkbox_state_changed(self, idx, state):
        crop_flag = True
        if   state == Qt.CheckState.Checked.value:
            crop_flag = True
        elif state == Qt.CheckState.Unchecked.value:
            crop_flag = False
        self._lots_data.set_crop_flag_by_idx(idx, crop_flag)

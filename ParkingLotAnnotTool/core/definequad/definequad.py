import cv2
import json
from pathlib import Path

from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6.QtWidgets import QDialogButtonBox as QDBB

from ParkingLotAnnotTool.utils.geometry import is_polygon_convex
from ParkingLotAnnotTool.utils.resource import read_icon
from ParkingLotAnnotTool.utils.signal import *
from ParkingLotAnnotTool.utils.trace import traceback_and_exit
from .canvas import CanvasPicture, CanvasScroll
from .action import new_action
from .lotsdata import LotsData
from .imgcrop import ImageCropWorker
from .videoextract import VideoExtractWorker

CANVASTOOL_NONE = 0
CANVASTOOL_DRAW = 1

epsilon = 16.0
area_init_size = 100.0
point_size = 8

lot_default_fill_color       = QColor(  0, 128, 255, 155)
lot_highlighted_fill_color   = QColor(  0,   0, 255, 200)
lot_selected_fill_color      = QColor(  0,   0, 255, 128)
point_default_fill_color     = QColor(255,   0,   0, 128)
point_highlighted_fill_color = QColor(255, 153,   0, 255)

class DefineQuadWidget(QWidget):

    def __init__(self):
        super(DefineQuadWidget, self).__init__()

        self.editable = True
        self.lots_data = LotsData()
        self.add_lot_dialog = AddLotDialog(self)

        self.canvas = Canvas(self)
        self.canvas_picture = CanvasPicture()
        self.canvas_picture.key_press_event_sig.connect(self.canvas.key_press_event)
        self.canvas_picture.mouse_double_click_sig.connect(self.canvas.mouse_double_click_event)
        self.canvas_picture.mouse_move_event_sig.connect(self.canvas.mouse_move_event)
        self.canvas_picture.mouse_press_event_sig.connect(self.canvas.mouse_press_event)
        self.canvas_picture.mouse_release_event_sig.connect(self.canvas.mouse_release_event)
        self.canvas_picture.paint_event_sig.connect(self.canvas.paint_event)
        self.canvas_scroll = CanvasScroll(self, self.canvas_picture)

        self.open_action = new_action(self, 'Open', icon=read_icon('open_file.png'), slot=self.click_open)
        self.save_action = new_action(self, 'Save', icon=read_icon('save.png'), slot=self.click_save)
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

        self.lot_list = LotList(self)
        layout = QHBoxLayout(self)
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas_scroll)
        layout.addWidget(self.lot_list)
        self.setLayout(layout)

        self.check_canvastool(CANVASTOOL_NONE)

    def enable_add_preset(self) -> None:
        self.editable = False
        self.set_action.setEnabled(False)
        self.save_action.setEnabled(False)
        self.none_action.setEnabled(False)
        self.draw_action.setEnabled(False)
        self.extract_frames_action.setEnabled(False)
        self.view_zoom_fit_action.setEnabled(False)
        self.view_zoom_1_action.setEnabled(False)

    def disable_add_preset(self) -> None:
        self.editable = True
        self.set_action.setEnabled(True)
        self.save_action.setEnabled(True)
        self.none_action.setEnabled(True)
        self.draw_action.setEnabled(True)
        self.extract_frames_action.setEnabled(True)
        self.view_zoom_fit_action.setEnabled(True)
        self.view_zoom_1_action.setEnabled(True)

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
            self.lots_data.json_path = file_path[0]
            self.lots_data.load()
            image_path = self.lots_data.get_image_path()
        img = cv2.imread(image_path, cv2.IMREAD_COLOR)
        self.canvas_picture.set_picture(img)
        self.canvas_scroll.fit_window()

    def click_save(self) -> None:
        traceback_and_exit(self.click_save_impl)
    def click_save_impl(self) -> None:
        if self.lots_data.json_path is None:
            file_path, _ = QFileDialog.getSaveFileName(self, "Save File", "", "Json File (*.json)")
            self.lots_data.json_path = file_path
        if self.lots_data.is_dirty() and self.lots_data.loaded():
            self.lots_data.may_save()
        else:
            self.lots_data.save()

    def click_none(self) -> None:
        traceback_and_exit(self.click_none_impl)
    def click_none_impl(self) -> None:
        self.check_canvastool(CANVASTOOL_NONE)

    def click_draw(self) -> None:
        traceback_and_exit(self.click_draw_impl)
    def click_draw_impl(self) -> None:
        self.check_canvastool(CANVASTOOL_DRAW)

    def video_extraction_start(self, video_path, outdir_path, interval):
        self.progress_dialog = QProgressDialog("Extracting frames...", "Cancel", 0, 100, self)
        self.videoextract_worker = VideoExtractWorker(video_path, outdir_path, interval)

        self.progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
        self.progress_dialog.canceled.connect(self.videoextract_worker.cancel)
        self.progress_dialog.show()
        self.videoextract_worker.progress.connect(self.progress_dialog.setValue)
        self.videoextract_worker.finished.connect(self.image_cropping_start)
        self.videoextract_worker.canceled.connect(self.progress_dialog.close)
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
        lots = self.lots_data.get_lots()
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

        data = {
            "version": "0.1",
            "video_path": str(video_path),
            "lots": self.lots_data.get_lots(),
            "scenes": {}
        }
        for lot in self.lots_data.get_lots():
            data["scenes"][lot["id"]] = []
        self.scene_json_path = outdir_path / "scene.json"
        with open(self.scene_json_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        
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

    def refresh(self) -> None:
        self.lot_list.refresh()


class AddLotDialog(QDialog):

    def __init__(self, parent: DefineQuadWidget):
        super(AddLotDialog, self).__init__(parent)
        self.p = parent

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
            lots_data = self.p.lots_data
            lot_id = self.ledit_id.text()
            xmin = min(mouse_pressed_x, mouse_x)
            ymin = min(mouse_pressed_y, mouse_y)
            xmax = max(mouse_pressed_x, mouse_x)
            ymax = max(mouse_pressed_y, mouse_y)
            lots_data.add_lot(
                lot_id,
                int(xmin), int(ymin),
                int(xmax), int(ymin),
                int(xmax), int(ymax),
                int(xmin), int(ymax))
        except RuntimeError:
            # signals.print(f'Add Lot failed. {e}.')
            pass

class Canvas:

    def __init__(self, parent: DefineQuadWidget):
        self.p = parent  # CanvasPane

        self.highlighted_lidx = None
        self.highlighted_pidx = None
        self.selected_lidx = None
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
            self.selected_lidx = None
            self.p.lot_list.set_selected_lidx(self.selected_lidx)
        elif event.key() == Qt.Key.Key_Delete:
            lots_data = self.p.lots_data
            if not lots_data.loaded():
                return
            if self.p.editable is False:
                return
            if self.selected_lidx is None:
                return
            lots_data.delete_area(self.selected_lidx)
            self.selected_lidx = None
            self.p.lot_list.set_selected_lidx(self.selected_lidx)
            self.p.lot_list.refresh()

    def mouse_double_click_event(self, event: QMouseEvent, pos: QPoint, scale: float) -> None:
        traceback_and_exit(self.mouse_double_click_event_impl, event=event, pos=pos, scale=scale)
    def mouse_double_click_event_impl(self, event: QMouseEvent, pos: QPoint, scale: float) -> None:
        lots_data = self.p.lots_data
        if not lots_data.loaded():
            return
        if self.p.editable is False:
            return

    def mouse_move_event(self, event: QMouseEvent, pos: QPoint, scale: float) -> None:
        traceback_and_exit(self.mouse_move_event_impl, event=event, pos=pos, scale=scale)
    def mouse_move_event_impl(self, event: QMouseEvent, pos: QPoint, scale: float) -> None:
        lots_data = self.p.lots_data
        if self.p.editable is False:
            return
        canvastool = self.p.get_canvastool()

        mouse_x = pos.x()
        mouse_y = pos.y()

        if self.mouse_pressed_on_point:
            points = lots_data.get_points(self.highlighted_lidx)
            points[self.highlighted_pidx] = [mouse_x, mouse_y]
            quad_is_convex = is_polygon_convex(
                [points[0][0], points[1][0], points[2][0], points[3][0]],
                [points[0][1], points[1][1], points[2][1], points[3][1]])
            if not quad_is_convex:
                return
            lots_data.set_point(
                self.highlighted_lidx,
                self.highlighted_pidx,
                mouse_x,
                mouse_y)
        elif (canvastool == CANVASTOOL_NONE) and \
             (self.mouse_pressed_on_lot) and \
             (not self.mouse_pressed_on_point):
            lots_data.move_lot(
                self.highlighted_lidx,
                mouse_x - self.mouse_x,
                mouse_y - self.mouse_y)
        else:
            self.highlighted_lidx = None
            self.highlighted_pidx = None
            lidx_in = lots_data.is_point_in_quad(pos.x(), pos.y())
            dist, lidx, pidx = lots_data.nearest_point(pos.x(), pos.y())
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

    def mouse_press_event(self, event: QMouseEvent, pos: QPoint, scale: float) -> None:
        traceback_and_exit(self.mouse_press_event_impl, event=event, pos=pos, scale=scale)
    def mouse_press_event_impl(self, event: QMouseEvent, pos: QPoint, scale: float) -> None:
        if self.p.editable is False:
            return

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
            self.selected_lidx = self.highlighted_lidx
            self.p.lot_list.set_selected_lidx(self.selected_lidx)

    def mouse_release_event(self, event: QMouseEvent, pos: QPoint, scale: float) -> None:
        traceback_and_exit(self.mouse_release_event_impl, event=event, pos=pos, scale=scale)
    def mouse_release_event_impl(self, event: QMouseEvent, pos: QPoint, scale: float) -> None:
        if self.p.editable is False:
            return
        canvastool = self.p.get_canvastool()

        if (canvastool == CANVASTOOL_DRAW) and \
           (event.button() == Qt.MouseButton.LeftButton) and \
           (self.mouse_pressed_x is not None) and \
           (self.mouse_pressed_y is not None) and \
           (not self.mouse_pressed_on_lot) and \
           (not self.mouse_pressed_on_point):
            self.p.add_lot_dialog.popup(
                self.mouse_pressed_x, self.mouse_pressed_y,
                pos.x(), pos.y())
            self.p.lot_list.refresh()
            self.p.update()

        if event.button() == Qt.MouseButton.LeftButton:
            self.mouse_pressed = False
            self.mouse_pressed_on_lot = False
            self.mouse_pressed_on_point = False

    def paint_event(self, event: QPaintEvent, painter: QPainter, scale: float) -> None:
        traceback_and_exit(self.paint_event_impl, event=event, painter=painter, scale=scale)
    def paint_event_impl(self, event: QPaintEvent, painter: QPainter, scale: float) -> None:
        lots_data = self.p.lots_data
        if not self.p.editable:
            return
        canvastool = self.p.get_canvastool()

        scale = scale
        p = painter

        lots = lots_data.get_lots()

        p.setPen(QPen(QColor(0, 0, 0, 0)))
        for lidx, lot in enumerate(lots):
            lot_fill_color = lot_default_fill_color
            if   lidx == self.selected_lidx:
                lot_fill_color = lot_selected_fill_color
            elif lidx == self.highlighted_lidx:
                lot_fill_color = lot_highlighted_fill_color
            points = lots_data.get_points(lidx)
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
            points = lots_data.get_points(lidx)
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

        if (canvastool == CANVASTOOL_DRAW) and \
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

    def get_selected_lidx(self):
        return self.selected_lidx

    def set_selected_lidx(self, selected_lidx):
        self.selected_lidx = selected_lidx


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

    def __init__(self, parent: DefineQuadWidget):
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
            lots = self.p.lots_data.get_lots()
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
            self.p.canvas.set_selected_lidx(None)
        elif event.key() == Qt.Key.Key_Delete:
            lots_data = self.p.lots_data
            if not lots_data.loaded():
                return
            if self.p.editable is False:
                return
            if self.get_selected_lidx() is None:
                return
            lots_data.delete_area(self.get_selected_lidx())
            self.set_selected_lidx(None)
            self.p.canvas.set_selected_lidx(None)
            self.refresh()

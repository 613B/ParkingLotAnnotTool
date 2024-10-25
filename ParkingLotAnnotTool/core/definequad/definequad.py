import math
import os.path as osp
import cv2

from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6.QtWidgets import QDialogButtonBox as QDBB

from ParkingLotAnnotTool.utils.trace import traceback_and_exit
from ParkingLotAnnotTool.utils.resource import read_icon
from ParkingLotAnnotTool.utils.signal import *
from ParkingLotAnnotTool.utils.filedialog import FileDialog
from .canvas import CanvasPicture, CanvasScroll
from .action import new_action

CANVASTOOL_NONE = 0
CANVASTOOL_QUADRANGLE = 1

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
        self.get_action = new_action(self, 'Save', icon=read_icon('save.png'), slot=self.click_get)
        self.none_action = new_action(self, 'Draw', icon=read_icon('draw.png'), slot=self.click_none, checkable=True)
        self.quadrangle_action = new_action(self, 'None', icon=read_icon('arrow.png'), slot=self.click_quadrangle, checkable=True)
        self.capture_action = new_action(self, 'Split', icon=read_icon('film.png'), slot=self.click_capture)
        self.view_zoom_fit_action = new_action(self, 'Zoom Fit', icon=read_icon('zoom_fit.png'), slot=self.press_view_zoom_fit)
        self.view_zoom_1_action = new_action(self, 'Zoom 100%', icon=read_icon('zoom_1.png'), slot=self.press_view_zoom_1)

        self.toolbar = QToolBar()
        self.toolbar.setOrientation(Qt.Orientation.Vertical)
        self.toolbar.addAction(self.open_action)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.get_action)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.none_action)
        self.toolbar.addAction(self.quadrangle_action)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.capture_action)
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
        self.get_action.setEnabled(False)
        self.none_action.setEnabled(False)
        self.quadrangle_action.setEnabled(False)
        self.capture_action.setEnabled(False)
        self.view_zoom_fit_action.setEnabled(False)
        self.view_zoom_1_action.setEnabled(False)

    def disable_add_preset(self) -> None:
        self.editable = True
        self.set_action.setEnabled(True)
        self.get_action.setEnabled(True)
        self.none_action.setEnabled(True)
        self.quadrangle_action.setEnabled(True)
        self.capture_action.setEnabled(True)
        self.view_zoom_fit_action.setEnabled(True)
        self.view_zoom_1_action.setEnabled(True)

    def changed_zoom(self):
        traceback_and_exit(self.changed_zoom_impl)
    def changed_zoom_impl(self):
        self.canvas_picture.set_zoom(100)

    def click_open(self) -> None:
        traceback_and_exit(self.click_open_impl)
    def click_open_impl(self) -> None:
        file_filter = "images (*.png *.PNG *.jpg *.jpeg *.JPG *.JPEG);;json (*.json *.JSON)"
        file_path = QFileDialog.getOpenFileName(self, "Open File", "", file_filter)
        print(file_path)
        if file_path == ('', ''):
            return
        self.file_path = file_path
        img = cv2.imread(file_path[0], cv2.IMREAD_COLOR)
        self.canvas_picture.set_picture(img)
        self.canvas_scroll.fit_window()

    def click_get(self) -> None:
        traceback_and_exit(self.click_get_impl)
    def click_get_impl(self) -> None:
        self.lot_list.refresh()
        self.canvas_picture.update()

    def click_none(self) -> None:
        traceback_and_exit(self.click_none_impl)
    def click_none_impl(self) -> None:
        self.check_canvastool(CANVASTOOL_NONE)

    def click_quadrangle(self) -> None:
        traceback_and_exit(self.click_quadrangle_impl)
    def click_quadrangle_impl(self) -> None:
        self.check_canvastool(CANVASTOOL_QUADRANGLE)

    def click_capture(self) -> None:
        traceback_and_exit(self.click_capture_impl)
    def click_capture_impl(self) -> None:
        # dcp: DCP = query.dcp()
        # if not check_camera_is_valid(dcp):
        #     return
        # try:
        #     dcp.preset_name = query.preset_parkinglot().get_preset_name()
        #     preset_dir = device_preset_dir(dcp)
        #     config_preset_file = device_config_preset_file(dcp)
        #     preset_timestamp_file = device_preset_timestamp_file(dcp)
        #     preset_img_file = device_preset_img_file(dcp)
        #     preset_img_tmp_file = osp.join(CAPTURE_CAMERA_TMP_DIR, dcp.camera_name + '.jpg')
        #     capture_camera_img_file = CAPTURE_CAMERA_DIR + '/' + dcp.camera_name + '.jpg'

        #     if not dcp.device.sftp_exists(capture_camera_img_file):
        #         raise RuntimeError(f'{capture_camera_img_file} does not exists')

        #     dcp.device.sftp_mkdir_p(preset_dir)
        #     if not dcp.device.sftp_exists(config_preset_file):
        #         with open(CONFIG_PRESET_TMP_FILE, 'w') as f:
        #             json.dump({
        #                 'type': 'parkinglot',
        #                 'lots': []},
        #                 f, indent=4)
        #         dcp.device.sftp_put(
        #             CONFIG_PRESET_TMP_FILE,
        #             config_preset_file)
        #     if not dcp.device.sftp_exists(preset_timestamp_file):
        #         with open(PRESET_TIMESTAMP_TMP_FILE, 'w') as f:
        #             f.write(datetime.datetime.now().strftime("%Y%m%d%H%M%S%f"))
        #         dcp.device.sftp_put(
        #             PRESET_TIMESTAMP_TMP_FILE,
        #             preset_timestamp_file)

        #     mkdir_if_not_exists(CAPTURE_CAMERA_TMP_DIR)
        #     dcp.device.sftp_get(
        #         capture_camera_img_file,
        #         preset_img_tmp_file)
        #     dcp.device.sftp_put(
        #         preset_img_tmp_file,
        #         preset_img_file)
            
        #     signals.mainwindow_refresh(dcp, download=True)
        # except RuntimeError as e:
        #     signals.print(f'faliled. {e}.')
        #     return
        # img = cv2.imread(preset_img_tmp_file, cv2.IMREAD_COLOR)
        # self.canvas_picture.set_picture(img)
        self.canvas_scroll.fit_window()

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
        self.quadrangle_action.setChecked(False)

    def check_canvastool(self, tool) -> None:
        self.clear_canvastool()
        if   tool == CANVASTOOL_NONE:
            self.none_action.setChecked(True)
        elif tool == CANVASTOOL_QUADRANGLE:
            self.quadrangle_action.setChecked(True)
        else:
            raise RuntimeError(f'tool={tool}')

    def get_canvastool(self) -> None:
        if self.none_action.isChecked():
            return CANVASTOOL_NONE
        if self.quadrangle_action.isChecked():
            return CANVASTOOL_QUADRANGLE
        raise RuntimeError('no tool is checked')

    def refresh(self) -> None:
        # dcp = query.dcp()
        # preset = query.preset_parkinglot()
        # preset.load(dcp)
        # settings.set_selected_preset_name(dcp.device.name, dcp.camera_name, dcp.preset_name)
        # settings.save()
        # self.lot_list.refresh()
        # self.canvas_picture.set_picture(preset.get_img())
        self.canvas_scroll.fit_window()


class AddLotDialog(QDialog):

    def __init__(self, parent: DefineQuadWidget):
        super(AddLotDialog, self).__init__(parent)

        self.setWindowTitle('Add Lot')
        self.setWindowFlags(
            self.windowFlags() &
            ~Qt.WindowType.WindowContextHelpButtonHint)

        self.label_id = QLabel('ID')
        self.ledit_id = QLineEdit()

        self.label_block_num = QLabel('BLOCK NUM')
        self.cb_block_num = QComboBox()
        self.cb_block_num.currentIndexChanged.connect(self.update_cb_lot_num)

        self.label_lot_num = QLabel('LOT NUM')
        self.cb_lot_num = QComboBox()

        self.bb = QDBB(QDBB.StandardButton.Ok, self)
        self.bb.accepted.connect(self.accept)

        layout = QVBoxLayout()
        gl = QGridLayout()
        gl.addWidget(self.label_id, 0, 0)
        gl.addWidget(self.ledit_id, 0, 1)
        gl.addWidget(self.label_block_num, 1, 0)
        gl.addWidget(self.cb_block_num, 1, 1)
        gl.addWidget(self.label_lot_num, 2, 0)
        gl.addWidget(self.cb_lot_num, 2, 1)
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
            # preset = query.preset_parkinglot()
            # lot_id = self.ledit_id.text()
            # block_num = self.cb_block_num.currentText()
            # lot_num = self.cb_lot_num.currentText()
            # xmin = min(mouse_pressed_x, mouse_x)
            # ymin = min(mouse_pressed_y, mouse_y)
            # xmax = max(mouse_pressed_x, mouse_x)
            # ymax = max(mouse_pressed_y, mouse_y)
            # preset.add_lot(
            #     lot_id,
            #     int(block_num),
            #     int(lot_num),
            #     int(xmin), int(ymin),
            #     int(xmax), int(ymin),
            #     int(xmax), int(ymax),
            #     int(xmin), int(ymax))
        except RuntimeError:
            # signals.print(f'Add Lot failed. {e}.')
            pass
    
    def showEvent(self, event):
        pass
        # preset = query.preset_parkinglot()
        # self.cb_block_num.clear()
        # for block in preset.shared_lots.keys():
        #     if preset.shared_lots[block]:
        #         self.cb_block_num.addItem(str(block))

    def update_cb_lot_num(self, index):
        pass
        # preset = query.preset_parkinglot()
        # current_text = self.cb_block_num.currentText()
        # if not current_text:
        #     return
        # self.cb_lot_num.clear()
        # for lot_num in preset.shared_lots[int(current_text, 0)]:
        #     self.cb_lot_num.addItem(str(lot_num))


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
            pass
            # preset = query.preset_parkinglot()
            # if not preset.loaded():
            #     return
            # if self.p.editable is False:
            #     return
            # if self.selected_lidx is None:
            #     return
            # preset.delete_area(self.selected_lidx)
            # self.selected_lidx = None
            # self.p.lot_list.set_selected_lidx(self.selected_lidx)
            # self.p.lot_list.refresh()

    def mouse_double_click_event(self, event: QMouseEvent, pos: QPoint, scale: float) -> None:
        traceback_and_exit(self.mouse_double_click_event_impl, event=event, pos=pos, scale=scale)
    def mouse_double_click_event_impl(self, event: QMouseEvent, pos: QPoint, scale: float) -> None:
        # preset = query.preset_parkinglot()
        # if not preset.loaded():
        #     return
        # if self.p.editable is False:
        #     return
        pass

    def mouse_move_event(self, event: QMouseEvent, pos: QPoint, scale: float) -> None:
        traceback_and_exit(self.mouse_move_event_impl, event=event, pos=pos, scale=scale)
    def mouse_move_event_impl(self, event: QMouseEvent, pos: QPoint, scale: float) -> None:
        # preset = query.preset_parkinglot()
        # if not preset.loaded():
        #     dcp = query.dcp()
        #     if not preset.load(dcp):
        #         return
        # if self.p.editable is False:
        #     return
        # toolbar = self.p.toolbar
        # tool = self.p.get_canvastool()

        mouse_x = pos.x()
        mouse_y = pos.y()

        # if self.mouse_pressed_on_point:
        #     points = preset.get_points(self.highlighted_lidx)
        #     points[self.highlighted_pidx] = [mouse_x, mouse_y]
        #     quad = Quadrangle2d(
        #         points[0][0], points[0][1],
        #         points[1][0], points[1][1],
        #         points[2][0], points[2][1],
        #         points[3][0], points[3][1])
        #     if not quad.is_convex():
        #         return
        #     preset.set_point(
        #         self.highlighted_lidx,
        #         self.highlighted_pidx,
        #         mouse_x,
        #         mouse_y)
        # elif (tool == CANVASTOOL_NONE) and \
        #      (self.mouse_pressed_on_lot) and \
        #      (not self.mouse_pressed_on_point):
        #     preset.move_lot(
        #         self.highlighted_lidx,
        #         mouse_x - self.mouse_x,
        #         mouse_y - self.mouse_y)
        # else:
        #     self.highlighted_lidx = None
        #     self.highlighted_pidx = None
        #     lidx_in = preset.is_point_in_quad(pos.x(), pos.y())
        #     dist, lidx, pidx = preset.nearest_point(pos.x(), pos.y())
        #     if dist is not None:
        #         if dist < epsilon / scale:
        #             self.highlighted_lidx = lidx
        #             self.highlighted_pidx = pidx
        #         else:
        #             if lidx_in is not None:
        #                 self.highlighted_lidx = lidx_in
        #                 self.highlighted_pidx = None

        self.mouse_x = pos.x()
        self.mouse_y = pos.y()

    def mouse_press_event(self, event: QMouseEvent, pos: QPoint, scale: float) -> None:
        traceback_and_exit(self.mouse_press_event_impl, event=event, pos=pos, scale=scale)
    def mouse_press_event_impl(self, event: QMouseEvent, pos: QPoint, scale: float) -> None:
        pass
    #     preset = query.preset_parkinglot()
    #     if not preset.loaded():
    #         return
    #     if self.p.editable is False:
    #         return

    #     if event.button() == Qt.MouseButton.LeftButton:
    #         self.mouse_pressed = True
    #         if (self.highlighted_lidx is not None):
    #             self.mouse_pressed_on_lot = True
    #         if (self.highlighted_pidx is not None):
    #             self.mouse_pressed_on_point = True

    #     self.mouse_pressed_x = pos.x()
    #     self.mouse_pressed_y = pos.y()

    #     if (event.button() == Qt.MouseButton.LeftButton) and \
    #        (self.mouse_pressed_on_lot):
    #         self.selected_lidx = self.highlighted_lidx
    #         self.p.lot_list.set_selected_lidx(self.selected_lidx)

    def mouse_release_event(self, event: QMouseEvent, pos: QPoint, scale: float) -> None:
        traceback_and_exit(self.mouse_release_event_impl, event=event, pos=pos, scale=scale)
    def mouse_release_event_impl(self, event: QMouseEvent, pos: QPoint, scale: float) -> None:
        pass
        # preset = query.preset_parkinglot()
        # if not preset.loaded():
        #     dcp = query.dcp()
        #     if not preset.load(dcp):
        #         return
        # if self.p.editable is False:
        #     return
        # toolbar = self.p.toolbar
        # tool = self.p.get_canvastool()

        # if (tool == CANVASTOOL_QUADRANGLE) and \
        #    (event.button() == Qt.MouseButton.LeftButton) and \
        #    (self.mouse_pressed_x is not None) and \
        #    (self.mouse_pressed_y is not None) and \
        #    (not self.mouse_pressed_on_lot) and \
        #    (not self.mouse_pressed_on_point):
        #     self.p.add_lot_dialog.popup(
        #         self.mouse_pressed_x, self.mouse_pressed_y,
        #         pos.x(), pos.y())
        #     self.p.lot_list.refresh()
        #     self.p.update()

        if event.button() == Qt.MouseButton.LeftButton:
            self.mouse_pressed = False
            self.mouse_pressed_on_lot = False
            self.mouse_pressed_on_point = False

    def paint_event(self, event: QPaintEvent, painter: QPainter, scale: float) -> None:
        traceback_and_exit(self.paint_event_impl, event=event, painter=painter, scale=scale)
    def paint_event_impl(self, event: QPaintEvent, painter: QPainter, scale: float) -> None:
        # preset = query.preset_parkinglot()
        # if not preset.loaded():
        #     dcp = query.dcp()
        #     if not preset.load(dcp):
        #         return
        # if not self.p.editable:
        #     return
        # toolbar = self.p.toolbar
        # tool = self.p.get_canvastool()

        # scale = scale
        # p = painter

        # lots = preset.get_lots()

        # p.setPen(QPen(QColor(0, 0, 0, 0)))
        # for lidx, lot in enumerate(lots):
        #     lot_fill_color = lot_default_fill_color
        #     if   lidx == self.selected_lidx:
        #         lot_fill_color = lot_selected_fill_color
        #     elif lidx == self.highlighted_lidx:
        #         lot_fill_color = lot_highlighted_fill_color
        #     points = preset.get_points(lidx)
        #     poly = QPolygonF([
        #         QPointF(points[0][0], points[0][1]),
        #         QPointF(points[1][0], points[1][1]),
        #         QPointF(points[2][0], points[2][1]),
        #         QPointF(points[3][0], points[3][1])])
        #     p.setBrush(QBrush(lot_fill_color))
        #     p.drawPolygon(poly)

        # pen = QPen()
        # pen.setWidth(max(1, int(round(2.0 / scale))))
        # p.setPen(pen)
        # for lidx, _ in enumerate(lots):
        #     points = preset.get_points(lidx)
        #     for pidx, point in enumerate(points):
        #         point_fill_color = point_default_fill_color
        #         if (lidx == self.highlighted_lidx) and \
        #            (pidx == self.highlighted_pidx):
        #             point_fill_color = point_highlighted_fill_color
        #         point_path = QPainterPath()
        #         point_path.addEllipse(
        #             point[0] - (point_size / scale) / 2.0,
        #             point[1] - (point_size / scale) / 2.0,
        #             point_size / scale,
        #             point_size / scale)
        #         p.fillPath(point_path, point_fill_color)

        # if (tool == CANVASTOOL_QUADRANGLE) and \
        #    (self.mouse_x is not None) and \
        #    (self.mouse_y is not None) and \
        #    (self.mouse_pressed) and \
        #    (self.mouse_pressed_x is not None) and \
        #    (self.mouse_pressed_y is not None) and \
        #    (not self.mouse_pressed_on_lot) and \
        #    (not self.mouse_pressed_on_point):
        #     p.setPen(QPen(QColor(0, 0, 0, 0)))
        #     xmin = min(self.mouse_x, self.mouse_pressed_x)
        #     ymin = min(self.mouse_y, self.mouse_pressed_y)
        #     xmax = max(self.mouse_x, self.mouse_pressed_x)
        #     ymax = max(self.mouse_y, self.mouse_pressed_y)
        #     poly = QPolygonF([
        #         QPointF(xmin, ymin),
        #         QPointF(xmax, ymin),
        #         QPointF(xmax, ymax),
        #         QPointF(xmin, ymax)])
        #     p.setBrush(QBrush(lot_default_fill_color))
        #     p.drawPolygon(poly)
        pass

    def get_selected_lidx(self):
        return self.selected_lidx

    def set_selected_lidx(self, selected_lidx):
        self.selected_lidx = selected_lidx

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
        # with DisableChangedSignal(self):
        #     if idx == None:
        #         self.setCurrentRow(-1)
        #         return
        #     self.setCurrentRow(idx)
        pass

    def refresh(self) -> None:
        pass
        # with DisableChangedSignal(self):

        #     if not check_camera_is_valid(query.dcp(), show_mbox=False):
        #         self.clear_list()
        #         return

        #     self.clear()
        #     preset = query.preset_parkinglot()
        #     lots = preset.get_lots()
        #     for _, lot in enumerate(lots):
        #         self.addItem(f"{lot['id']} (block {lot['block_num']}, lot {lot['lot_num']})")
        #     select_idx = self.get_selected_lidx()
        #     if (select_idx is not None) and \
        #        (select_idx < self.count()):
        #         self.setCurrentRow(select_idx)
        #     else:
        #         self.setCurrentRow(-1)

            # self.changed_impl()

    def changed(self) -> None:
        traceback_and_exit(self.changed_impl)
    def changed_impl(self) -> None:
        self.p.canvas.set_selected_lidx(self.get_selected_lidx())

    def clear_list(self):
        if self.count() == 0:
            return
        self.clear()
        # query.dcp().clear_preset()
        self.changed_impl()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        pass
        # if event.key() == Qt.Key.Key_Escape:
        #     self.set_selected_lidx(None)
        #     self.p.canvas.set_selected_lidx(None)
        # elif event.key() == Qt.Key.Key_Delete:
        #     preset = query.preset_parkinglot()
        #     if not preset.loaded():
        #         return
        #     if self.p.editable is False:
        #         return
        #     if self.get_selected_lidx() is None:
        #         return
        #     preset.delete_area(self.get_selected_lidx())
        #     self.set_selected_lidx(None)
        #     self.p.canvas.set_selected_lidx(None)
        #     self.refresh()

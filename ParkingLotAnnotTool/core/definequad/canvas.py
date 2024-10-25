from typing import Optional
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
import numpy as np
from ParkingLotAnnotTool.utils.trace import traceback_and_exit


class CanvasPicture(QWidget):

    zoom_request_sig   = pyqtSignal(int)
    scroll_request_sig = pyqtSignal(int, object)

    enter_event_sig         = pyqtSignal(QEnterEvent)
    focus_out_event_sig     = pyqtSignal(QFocusEvent)
    key_press_event_sig     = pyqtSignal(QKeyEvent)
    leave_event_sig         = pyqtSignal(QEvent)
    mouse_double_click_sig  = pyqtSignal(QMouseEvent, QPoint, float)
    mouse_move_event_sig    = pyqtSignal(QMouseEvent, QPoint, float)
    mouse_press_event_sig   = pyqtSignal(QMouseEvent, QPoint, float)
    mouse_release_event_sig = pyqtSignal(QMouseEvent, QPoint, float)
    paint_event_sig         = pyqtSignal(QPaintEvent, QPainter, float)

    def __init__(self):
        super(CanvasPicture, self).__init__()

        self.scale: float = 1.0
        self.painter = QPainter()
        self.pixmap: Optional[QPixmap] = None

        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setFocus()

    def enterEvent(self, event: QEnterEvent) -> None:
        traceback_and_exit(self.enterEvent_impl, event=event)
    def enterEvent_impl(self, event: QEnterEvent) -> None:
        self.enter_event_sig.emit(event)
        self.update()

    def focusOutEvent(self, event: QFocusEvent) -> None:
        traceback_and_exit(self.focusOutEvent_impl, event=event)
    def focusOutEvent_impl(self, event: QFocusEvent) -> None:
        self.focus_out_event_sig.emit(event)
        self.update()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        traceback_and_exit(self.keyPressEvent_impl, event=event)
    def keyPressEvent_impl(self, event: QKeyEvent) -> None:
        self.key_press_event_sig.emit(event)
        self.update()

    def leaveEvent(self, event: QEvent) -> None:
        traceback_and_exit(self.leaveEvent_impl, event=event)
    def leaveEvent_impl(self, event: QEvent) -> None:
        self.leave_event_sig.emit(event)
        self.update()

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        traceback_and_exit(self.mouseDoubleClickEvent_impl, event=event)
    def mouseDoubleClickEvent_impl(self, event: QMouseEvent) -> None:
        if self.pixmap is None:
            return
        self.mouse_double_click_sig.emit(
            event,
            self.__transform_pos(event.pos()),
            self.scale)
        self.update()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        traceback_and_exit(self.mouseMoveEvent_impl, event=event)
    def mouseMoveEvent_impl(self, event: QMouseEvent) -> None:
        if self.pixmap is None:
            return
        self.mouse_move_event_sig.emit(
            event,
            self.__transform_pos(event.pos()),
            self.scale)
        self.update()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        traceback_and_exit(self.mousePressEvent_impl, event=event)
    def mousePressEvent_impl(self, event: QMouseEvent) -> None:
        if self.pixmap is None:
            return
        self.mouse_press_event_sig.emit(
            event,
            self.__transform_pos(event.pos()),
            self.scale)
        self.update()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        traceback_and_exit(self.mouseReleaseEvent_impl, event=event)
    def mouseReleaseEvent_impl(self, event: QMouseEvent) -> None:
        if self.pixmap is None:
            return
        self.mouse_release_event_sig.emit(
            event,
            self.__transform_pos(event.pos()),
            self.scale)
        self.update()

    def paintEvent(self, event: QPaintEvent) -> None:
        traceback_and_exit(self.paintEvent_impl, event=event)
    def paintEvent_impl(self, event: QPaintEvent) -> None:
        if self.pixmap is None:
            return super(CanvasPicture, self).paintEvent(event)
        
        p = self.painter

        p.begin(self)

        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        p.scale(self.scale, self.scale)
        p.translate(self.__offset_to_center())
        p.drawPixmap(0, 0, self.pixmap)

        self.paint_event_sig.emit(event, p, self.scale)

        p.end()

        self.setAutoFillBackground(True)
        pal = self.palette()
        pal.setColor(self.backgroundRole(), QColor(232, 232, 232, 255))
        self.setPalette(pal)

        self.update()

    def wheelEvent(self, event: QWheelEvent) -> None:
        traceback_and_exit(self.wheelEvent_impl, event=event)
    def wheelEvent_impl(self, event: QWheelEvent) -> None:
        delta = event.angleDelta()
        h_delta = delta.x()
        v_delta = delta.y()
        if (Qt.KeyboardModifier.ControlModifier == event.modifiers()) and v_delta:
            self.zoom_request_sig.emit(v_delta)
        else:
            v_delta and self.scroll_request_sig.emit(v_delta, Qt.Orientation.Vertical)
            h_delta and self.scroll_request_sig.emit(h_delta, Qt.Orientation.Horizontal)
        event.accept()
        self.update()

    def sizeHint(self) -> QSize:
        return traceback_and_exit(self.sizeHint_impl)
    def sizeHint_impl(self) -> QSize:
        return self.minimumSizeHint()

    def minimumSizeHint(self) -> QSize:
        return traceback_and_exit(self.minimumSizeHint_impl)
    def minimumSizeHint_impl(self) -> QSize:
        if self.pixmap:
            return self.scale * self.pixmap.size()
        return super(CanvasPicture, self).minimumSizeHint()

    def set_picture(self, img: Optional[np.ndarray]):
        if img is None:
            qimg = QImage(1920, 1080, QImage.Format.Format_BGR888)
            qimg.fill(QColor(232, 232, 232))
            self.pixmap = QPixmap.fromImage(qimg)
        else:
            qimg = QImage(img.flatten(), img.shape[1], img.shape[0], QImage.Format.Format_BGR888)
            self.pixmap = QPixmap.fromImage(qimg)
        self.update()

    def set_zoom(self, value: int) -> None:
        self.scale = 0.01 * value
        self.adjustSize()
        self.update()

    def __transform_pos(self, point):
        """Convert from widget-logical coordinates to painter-logical coordinates."""
        return point / self.scale - self.__offset_to_center()

    def __offset_to_center(self) -> QPoint:
        s = self.scale
        area = super(CanvasPicture, self).size()
        w, h = self.pixmap.width() * s, self.pixmap.height() * s
        aw, ah = area.width(), area.height()
        x = (aw - w) / (2 * s) if aw > w else 0
        y = (ah - h) / (2 * s) if ah > h else 0
        return QPoint(int(x), int(y))


class CanvasScroll(QScrollArea):

    def __init__(self, parent: QWidget, canvas_picture: CanvasPicture):
        super(CanvasScroll, self).__init__(parent=parent)
        self._p = parent
        self._canvas_picture = canvas_picture
        self._zoom = 100

        self.setWidget(canvas_picture)
        self.setWidgetResizable(True)
        self.scrollBars = {
            Qt.Orientation.Vertical: self.verticalScrollBar(),
            Qt.Orientation.Horizontal: self.horizontalScrollBar()}
        self.setMinimumWidth(400)

        canvas_picture.scroll_request_sig.connect(self.scroll_request)
        canvas_picture.zoom_request_sig.connect(self.zoom_request)

    def scroll_request(self, delta: int, orientation: Qt.Orientation) -> None:
        traceback_and_exit(self.scroll_request_impl,
                           delta=delta,
                           orientation=orientation)
    def scroll_request_impl(self, delta: int, orientation: Qt.Orientation) -> None:
        units = - delta / (8 * 15)
        bar = self.scrollBars[orientation]
        bar.setValue(int(bar.value() + bar.singleStep() * units))

    def zoom_request(self, delta: int) -> None:
        traceback_and_exit(self.zoom_request_impl, delta=delta)
    def zoom_request_impl(self, delta: int) -> None:
        if self._canvas_picture.pixmap is None:
            return
        # get the current scrollbar positions
        # calculate the percentages ~ coordinates
        h_bar = self.scrollBars[Qt.Orientation.Horizontal]
        v_bar = self.scrollBars[Qt.Orientation.Vertical]
        # get the current maximum, to know the difference after zooming
        h_bar_max = h_bar.maximum()
        v_bar_max = v_bar.maximum()
        # get the cursor position and canvas size
        # calculate the desired movement from 0 to 1
        # where 0 = move left
        #       1 = move right
        # up and down analogous
        cursor = QCursor()
        pos = cursor.pos()
        relative_pos = QWidget.mapFromGlobal(self._p, pos)
        cursor_x = relative_pos.x()
        cursor_y = relative_pos.y()
        w = self.width()
        h = self.height()
        # the scaling from 0 to 1 has some padding
        # you don't have to hit the very leftmost pixel for a maximum-left movement
        margin = 0.1
        move_x = (cursor_x - margin * w) / (w - 2 * margin * w)
        move_y = (cursor_y - margin * h) / (h - 2 * margin * h)
        # clamp the values from 0 to 1
        move_x = min(max(move_x, 0), 1)
        move_y = min(max(move_y, 0), 1)
        # zoom in
        units = delta / (8 * 15)
        scale = 10
        self.add_zoom(scale * units)
        # get the difference in scrollbar values
        # this is how far we can move
        d_h_bar_max = h_bar.maximum() - h_bar_max
        d_v_bar_max = v_bar.maximum() - v_bar_max
        # get the new scrollbar values
        new_h_bar_value = h_bar.value() + move_x * d_h_bar_max
        new_v_bar_value = v_bar.value() + move_y * d_v_bar_max
        h_bar.setValue(int(new_h_bar_value))
        v_bar.setValue(int(new_v_bar_value))

    def __clip(
        self,
        value: int | float,
        lower: int | float,
        upper: int | float):
        return max(lower, min(value, upper))

    def set_zoom(self, zoom: int) -> None:
        if self._canvas_picture.pixmap is None:
            return
        self._zoom = int(zoom)
        self._zoom = self.__clip(self._zoom, 1, 500)
        self._canvas_picture.set_zoom(self._zoom)

    def add_zoom(self, increment: int = 10):
        if self._canvas_picture.pixmap is None:
            return
        self._zoom = int(self._zoom + increment)
        self._zoom = self.__clip(self._zoom, 1, 500)
        self._canvas_picture.set_zoom(self._zoom)

    def fit_window(self):
        if self._canvas_picture.pixmap is None:
            return
        value = self.__scale_to_fit_window()
        self._zoom = int(100 * value)
        self._zoom = self.__clip(self._zoom, 1, 500)
        self._canvas_picture.set_zoom(self._zoom)

    def __scale_to_fit_window(self) -> int:
        if self._canvas_picture.pixmap is None:
            return
        e = 2.0  # So that no scrollbars are generated.
        w1 = self.width() - e
        h1 = self.height() - e
        a1 = w1 / h1
        # Calculate a new scale value based on the pixmap's aspect ratio.
        w2 = self._canvas_picture.pixmap.width()
        h2 = self._canvas_picture.pixmap.height()
        a2 = w2 / h2
        return w1 / w2 if a2 >= a1 else h1 / h2

from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

from .scenedata import SceneData

class SeekBarWidget(QWidget):

    def __init__(self, scene_data: SceneData, parent=None):
        super().__init__(parent)

        self.scene_data = scene_data
        self.scene_data.selected_lot_idx_changed.connect(self.repaint)
        self.scene_data.data_changed.connect(self.repaint)
        self.scene_data.selected_scene_idx_changed.connect(self.update_value)
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(100)
        self.slider.setValue(0)
        self.slider.valueChanged.connect(self.value_changed)

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

    def value_changed(self, value):
        self.scene_data.update_current_frame(f"{value:05d}")

    def set_maxvalue(self, value):
        self.slider.setMaximum(value)

    def get_value(self):
        return self.slider.value()

    def get_value_str(self):
        return f"{self.slider.value():05d}"

    def set_value(self, value):
        self.slider.setValue(value)

    def update_value(self):
        self.slider.setValue(int(self.scene_data.current_frame()))

    def paintEvent(self, event):
        super().paintEvent(event)

        if self.scene_data.scenes_with_current_lot_id() is None:
            return

        painter = QPainter(self)
        slider_rect = self.slider.geometry()
        slider_min = self.slider.minimum()
        slider_max = self.slider.maximum()
        pen_free = QPen(QColor("green"), 2)
        pen_busy = QPen(QColor("red"), 2)
        pen_flags = QPen(QColor("blue"), 2)

        line_length = slider_rect.bottom() - slider_rect.top()
        center = slider_rect.top() + int(line_length / 2)

        for scene in self.scene_data.scenes_with_current_lot_id():
            if scene["label"] == 'free':
                painter.setPen(pen_free)
            if scene["label"] == 'busy':
                painter.setPen(pen_busy)
            marker = slider_rect.left() + slider_rect.width() * (int(scene["frame"]) - slider_min) / (slider_max - slider_min)
            marker = int(marker)
            painter.drawLine(marker, center - line_length, marker, center)

            flags = scene["flags"]
            if not flags:
                continue
            painter.setPen(pen_flags)
            painter.drawLine(marker, center, marker, center + line_length)

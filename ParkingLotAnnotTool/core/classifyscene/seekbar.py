from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *


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

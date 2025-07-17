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

        self.conditions = {'sunny': set([]), 'rainy': set([]), 'day': set([]), 'night': set([])}

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

    def reset_conditions(self):
        self.conditions = {'sunny': set([]), 'rainy': set([]), 'day': set([]), 'night': set([])}
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

    def add_sunny_condition(self):
        self.conditions['sunny'].add(self.slider.value())

    def add_rainy_condition(self):
        self.conditions['rainy'].add(self.slider.value())

    def add_day_condition(self):
        self.conditions['day'].add(self.slider.value())

    def add_night_condition(self):
        self.conditions['night'].add(self.slider.value())

    def remove_sunny_condition(self, value):
        self.conditions['sunny'].remove(value)

    def remove_rainy_condition(self, value):
        self.conditions['rainy'].remove(value)

    def remove_day_condition(self, value):
        self.conditions['day'].remove(value)

    def remove_night_condition(self, value):
        self.conditions['night'].remove(value)

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)

        slider_rect = self.slider.geometry()
        slider_min = self.slider.minimum()
        slider_max = self.slider.maximum()
        pen_rainy = QPen(QColor("cyan"), 2)
        pen_sunny = QPen(QColor("red"), 2)
        pen_day = QPen(QColor("orange"), 2)
        pen_night = QPen(QColor("blue"), 2)

        line_length = slider_rect.bottom() - slider_rect.top()
        center = slider_rect.top() + int(line_length / 2)
        y1, y2 = 0, 0

        for key, conditions_set in self.conditions.items():
            if key == 'rainy':
                painter.setPen(pen_rainy)
                y1, y2 = center - line_length, center
            if key == 'sunny':
                painter.setPen(pen_sunny)
                y1, y2 = center - line_length, center
            if key == 'day':
                painter.setPen(pen_day)
                y1, y2 = center, center + line_length
            if key == 'night':
                painter.setPen(pen_night)
                y1, y2 = center, center + line_length
            for condition in conditions_set:
                marker = slider_rect.left() + slider_rect.width() * (condition - slider_min) / (slider_max - slider_min)
                marker = int(marker)
                painter.drawLine(marker, y1, marker, y2)

import keyboard
from PyQt6.QtCore import QObject, pyqtSignal, Qt


class HotKey(QObject):

    hotkey_signal = pyqtSignal(int)

    def __init__(self):
        super(HotKey, self).__init__()
        keyboard.add_hotkey("h", self.key_h)
        keyboard.add_hotkey("j", self.key_j)
        keyboard.add_hotkey("k", self.key_k)
        keyboard.add_hotkey("l", self.key_l)
        keyboard.add_hotkey("left", self.key_left)
        keyboard.add_hotkey("right", self.key_right)

    def key_h(self):
        self.hotkey_signal.emit(Qt.Key.Key_H)

    def key_j(self):
        self.hotkey_signal.emit(Qt.Key.Key_J)

    def key_k(self):
        self.hotkey_signal.emit(Qt.Key.Key_K)

    def key_l(self):
        self.hotkey_signal.emit(Qt.Key.Key_L)

    def key_left(self):
        self.hotkey_signal.emit(Qt.Key.Key_Left)

    def key_right(self):
        self.hotkey_signal.emit(Qt.Key.Key_Right)


def initialize():
    global global_hotkey
    global_hotkey = HotKey()

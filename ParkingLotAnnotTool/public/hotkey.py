from pynput import keyboard
from PyQt6.QtCore import QObject, pyqtSignal, Qt


class HotKey(QObject):
    hotkey_signal = pyqtSignal(int)

    def __init__(self):
        super(HotKey, self).__init__()
        self.listener = keyboard.Listener(on_press=self.on_press)
        self.listener.start()

    def on_press(self, key):
        key_mapping = {
            'h': Qt.Key.Key_H,
            'j': Qt.Key.Key_J,
            'k': Qt.Key.Key_K,
            'l': Qt.Key.Key_L,
            keyboard.Key.left: Qt.Key.Key_Left,
            keyboard.Key.right: Qt.Key.Key_Right
        }

        try:
            if isinstance(key, keyboard.KeyCode):  # 文字キーの場合
                key_char = key.char
            else:  # 矢印キーなどの特殊キー
                key_char = key

            if key_char in key_mapping:
                self.hotkey_signal.emit(key_mapping[key_char])

        except AttributeError:
            pass  # 予期しないキーは無視


def initialize():
    global global_hotkey
    global_hotkey = HotKey()

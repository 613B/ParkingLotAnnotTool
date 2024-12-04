from PyQt6.QtCore import QObject, pyqtSignal


class Signals(QObject):

    print_sig = pyqtSignal(str, bool)

    def __init__(self):
        super(Signals, self).__init__()

    def print(self, text, date=True):
        self.print_sig.emit(text, date)

def initialize():
    global global_signals
    global_signals = Signals()

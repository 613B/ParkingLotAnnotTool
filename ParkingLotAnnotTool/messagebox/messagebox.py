# logger.py
from datetime import datetime
from loguru import logger
from PyQt6.QtWidgets import *
from PyQt6.QtGui import QTextCursor

from ParkingLotAnnotTool.utils.trace import traceback_and_exit
from ParkingLotAnnotTool.public.signals import global_signals

class MessageBox(QDockWidget):
    def __init__(self, name, parent=None):
        super().__init__(name, parent)
        self.mb = QPlainTextEdit()
        self.setWidget(self.mb)
        self.setFeatures(QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)
        global_signals.print_sig.connect(self.print)

    def print(self, text: str, date: bool = True) -> None:
        traceback_and_exit(self.print_impl, text=text, date=date)
    def print_impl(self, text: str, date: bool) -> None:
        try:
            if date:
                now = datetime.now()
                now = now.strftime('%Y/%m/%d %H:%M:%S.%f')[:-3]
                self.mb.appendPlainText(f'[{now}] {text}')
            else:
                self.mb.appendPlainText(f'{text}')
            self.mb.moveCursor(QTextCursor.MoveOperation.End)
            logger.info(text)
        except RuntimeError as e:
            print(e)

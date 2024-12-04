# ParkingLotAnnotTool/__main__.py

import sys
from PyQt6.QtWidgets import QApplication

import ParkingLotAnnotTool.public.signals as Signals
Signals.initialize()

from mainwindow import MainWindow

def main():
    print("ParkingLotAnnotTool is running.")
    app = QApplication(sys.argv)
    app.setStyle("WindowsVista")  # white mode explicitly
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

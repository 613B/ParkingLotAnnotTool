# ParkingLotAnnotTool/__main__.py

import sys
from PyQt6.QtWidgets import QApplication
from mainwindow import MainWindow

def main():
    print("ParkingLotAnnotTool is running.")
    app = QApplication(sys.argv)
    app.setStyle("WindowsVist")  # white mode explicitly
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

# ParkingLotAnnotTool/__main__.py

import sys
from PyQt5.QtWidgets import QApplication
from mainwindow import MainWindow

def main():
    print("ParkingLotAnnotTool is running.")
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
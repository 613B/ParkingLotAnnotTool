from PyQt5.QtWidgets import QMenuBar, QAction, QMainWindow

def create_menubar(mw: QMainWindow) -> None:
    menubar = QMenuBar(mw)
    edit_menu = menubar.addMenu('Edit')
    edit_action = QAction('Edit Action', mw)
    edit_menu.addAction(edit_action)
    ctrl_menu = menubar.addMenu('Ctrl')
    ctrl_action = QAction('Ctrl Action', mw)
    ctrl_menu.addAction(ctrl_action)
    help_menu = menubar.addMenu('Help')
    help_action = QAction('Help Action', mw)
    help_menu.addAction(help_action)

    mw.setMenuBar(menubar)
import sys
import os.path as osp
from PyQt6.QtGui import *
from PyQt6.QtCore import *


def read_icon(name: str) -> QIcon:
    path = osp.join('icon', name)
    if hasattr(sys, '_MEIPASS'):
        path = osp.join(sys._MEIPASS, path)
    return QIcon(QPixmap(path))

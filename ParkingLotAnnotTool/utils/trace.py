import sys
import traceback
from loguru import logger
from PyQt6.QtWidgets import QMessageBox as QMB


def traceback_and_exit(func, **kwargs):
    return func(**kwargs)

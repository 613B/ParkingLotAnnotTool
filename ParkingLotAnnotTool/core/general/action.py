from typing import Callable
from typing import Optional
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import QWidget


def new_action(
        parent: QWidget,
        text: str,
        icon: Optional[QIcon] = None,
        slot: Optional[Callable] = None,
        shortcut: Optional[str] = None,
        checkable: bool = False,
        checked: bool = False,
        enabled: Optional[bool] = None,
        icon_text: str = None
        ) -> QAction:
    action = QAction(text, parent)
    if icon is not None:
        action.setIcon(icon)
    if slot is not None:
        action.triggered.connect(slot)
    if shortcut is not None:
        action.setShortcut(shortcut)
    if checkable:
        action.setCheckable(True)
        action.setChecked(checked)
    if enabled is not None:
        action.setEnabled(enabled)
    if icon_text is not None:
        action.setIconText(icon_text)
    return action

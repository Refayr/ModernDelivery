from PySide6.QtCore import Signal
from PySide6.QtWidgets import QLineEdit


class MLineEdit(QLineEdit):
    onFocus = Signal()
    outFocus = Signal()

    def focusInEvent(self, event):
        super().focusInEvent(event)
        self.onFocus.emit()

    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        self.outFocus.emit()

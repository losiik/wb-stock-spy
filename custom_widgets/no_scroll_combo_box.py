from PyQt6.QtWidgets import QComboBox


class NoScrollComboBox(QComboBox):
    """ComboBox без прокрутки колесиком мыши"""

    def wheelEvent(self, event):
        # Игнорируем событие прокрутки
        event.ignore()

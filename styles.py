# styles.py
"""Стили для приложения Wildberries Scraper - темная тема"""


def get_main_window_stylesheet() -> str:
    """Стили для главного окна - темная тема"""
    return """
        QMainWindow, QWidget, QScrollArea {
            background-color: #1a1d1f;
        }

        /* Убираем фон у ВСЕХ QLabel */
        QLabel {
            background-color: transparent;
        }

        /* Главный заголовок */
        QLabel#mainTitle {
            font-size: 28px;
            font-weight: 700;
            color: #ffffff;
        }

        /* Карточки */
        QFrame#card, QFrame#account {
            background-color: #272b30;
            border-radius: 12px;
            border: 1px solid #3a3f47;
        }

        /* Заголовки карточек */
        QLabel#cardTitle {
            font-size: 18px;
            font-weight: 600;
            color: #ffffff;
        }

        QLabel#description {
            font-size: 14px;
            color: #9ca3af;
            line-height: 1.5;
        }

        /* Статусы авторизации */
        QLabel#statusSuccess {
            font-size: 14px;
            color: #34d399;
            font-weight: 500;
        }

        QLabel#statusInactive {
            font-size: 14px;
            color: #9ca3af;
            font-weight: 500;
        }

        /* Поля ввода */
        QLineEdit {
            padding: 14px 16px;
            border: 1px solid #3a3f47;
            border-radius: 8px;
            font-size: 15px;
            background-color: #1f2327;
            color: #ffffff;
        }

        QLineEdit:focus {
            border: 1px solid #6366f1;
            background-color: #1f2327;
        }

        QLineEdit:disabled {
            background-color: #1a1d1f;
            color: #6b7280;
        }

        /* Поле с ошибкой */
        QLineEdit[error="true"] {
            border: 2px solid #ef4444;
            background-color: #1f2327;
        }

        /* Комбобоксы */
        QComboBox {
            padding: 14px 16px;
            border: 1px solid #3a3f47;
            border-radius: 8px;
            font-size: 15px;
            background-color: #1f2327;
            color: #ffffff;
        }

        QComboBox:focus {
            border: 1px solid #6366f1;
        }

        QComboBox::drop-down {
            border: none;
            padding-right: 12px;
        }

        QComboBox::down-arrow {
            image: none;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 6px solid #9ca3af;
            margin-right: 8px;
        }

        QComboBox QAbstractItemView {
            border: 1px solid #3a3f47;
            border-radius: 8px;
            background-color: #272b30;
            selection-background-color: #6366f1;
            selection-color: #ffffff;
            padding: 8px;
            color: #ffffff;
        }

        /* Кнопки */
        QPushButton {
            font-size: 15px;
            font-weight: 600;
            border-radius: 8px;
            padding: 14px 24px;
            border: none;
            color: white;
        }

        /* Главная кнопка ЗАПУСКА - ЗЕЛЕНАЯ */
        QPushButton#startButton {
            background-color: #10b981;
            color: white;
        }

        QPushButton#startButton:hover {
            background-color: #059669;
        }

        QPushButton#startButton:pressed {
            background-color: #047857;
        }

        QPushButton#startButton:disabled {
            background-color: #3a3f47;
            color: #6b7280;
        }

        /* Вторичная кнопка (Добавить) - ФИОЛЕТОВАЯ */
        QPushButton#secondaryButton {
            background-color: #6366f1;
            color: white;
        }

        QPushButton#secondaryButton:hover {
            background-color: #4f46e5;
        }

        QPushButton#secondaryButton:pressed {
            background-color: #4338ca;
        }

        /* Кнопка опасного действия (Отключить) */
        QPushButton#dangerButton {
            background-color: #ef4444;
            color: white;
        }

        QPushButton#dangerButton:hover {
            background-color: #dc2626;
        }

        QPushButton#dangerButton:pressed {
            background-color: #b91c1c;
        }

        /* Основная кнопка */
        QPushButton#primaryButton {
            background-color: #6366f1;
            color: white;
        }

        QPushButton#primaryButton:hover {
            background-color: #4f46e5;
        }

        QPushButton#primaryButton:pressed {
            background-color: #4338ca;
        }

        QPushButton#primaryButton:disabled {
            background-color: #3a3f47;
            color: #6b7280;
        }

        /* Сообщения об ошибках */
        QLabel#errorLabel {
            color: #f87171;
            padding: 4px 0px;
            font-size: 13px;
        }

        QLabel#successLabel {
            color: #34d399;
            padding: 4px 0px;
            font-size: 13px;
        }

        QLabel#warningLabel {
            color: #fbbf24;
            padding: 4px 0px;
            font-size: 13px;
        }

        QLabel#hintLabel {
            color: #9ca3af;
            font-size: 13px;
        }

        /* Скроллбар */
        QScrollBar:vertical {
            background-color: #1a1d1f;
            width: 12px;
            border-radius: 6px;
        }

        QScrollBar::handle:vertical {
            background-color: #3a3f47;
            border-radius: 6px;
            min-height: 30px;
        }

        QScrollBar::handle:vertical:hover {
            background-color: #4a5160;
        }

        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0px;
        }
        
        QRadioButton {
            font-size: 15px;
            color: #ffffff;
            spacing: 10px;
            background-color: transparent;
        }
        
        QRadioButton::indicator {
            width: 20px;
            height: 20px;
            border-radius: 10px;
            border: 2px solid #3a3f47;
            background-color: #1f2327;
        }
        
        QRadioButton::indicator:checked {
            border: 2px solid #6366f1;
            background-color: #6366f1;
        }
        
        QRadioButton::indicator:checked:hover {
            border: 2px solid #4f46e5;
            background-color: #4f46e5;
        }
        
        QRadioButton::indicator:hover {
            border: 2px solid #6366f1;
        }
    """


def get_tracking_window_stylesheet() -> str:
    """Стили для окна отслеживания - темная тема"""
    return """
        QMainWindow {
            background-color: #1a1d1f;
        }

        /* Убираем фон у ВСЕХ QLabel */
        QLabel {
            background-color: transparent;
        }

        /* Заголовок товара */
        QLabel#productTitle {
            font-size: 24px;
            font-weight: 600;
            color: #ffffff;
            padding: 8px 16px 16px 16px;
        }

        /* Карточки */
        QFrame#card {
            background-color: #272b30;
            border-radius: 12px;
            border: 1px solid #3a3f47;
            padding: 10px 20px 20px 20px;
        }

        QLabel#cardTitle {
            font-size: 16px;
            font-weight: 600;
            color: #ffffff;
            padding-bottom: 8px;
        }

        /* Статусы */
        QLabel#statusRunning {
            color: #60a5fa;
            background-color: #1e3a5f;
            border-radius: 10px;
            padding: 10px 20px 20px 20px;
            font-size: 18px;
            font-weight: 600;
        }

        QLabel#statusCompleted {
            color: #34d399;
            background-color: #064e3b;
            border-radius: 10px;
            padding: 10px 20px 20px 20px;
            font-size: 18px;
            font-weight: 600;
        }

        QLabel#statusError {
            color: #f87171;
            background-color: #7f1d1f;
            border-radius: 10px;
            padding: 10px 20px 20px 20px;
            font-size: 18px;
            font-weight: 600;
        }

        /* Счетчик */
        QLabel#counterLabel {
            color: #60a5fa;
            font-size: 54px;
            font-weight: 700;
        }

        /* Прогресс */
        QLabel#progressText {
            color: #9ca3af;
            font-size: 15px;
        }

        QProgressBar {
            border: 1px solid #3a3f47;
            border-radius: 8px;
            text-align: center;
            background-color: #1f2327;
            height: 12px;
        }

        QProgressBar::chunk {
            background-color: #6366f1;
            border-radius: 7px;
        }

        /* Кнопки */
        QPushButton {
            font-size: 15px;
            font-weight: 600;
            border-radius: 8px;
            padding: 14px 24px;
            border: none;
        }

        QPushButton#dangerButton {
            background-color: #ef4444;
            color: white;
        }

        QPushButton#dangerButton:hover {
            background-color: #dc2626;
        }

        QPushButton#dangerButton:pressed {
            background-color: #b91c1c;
        }

        QPushButton#primaryButton {
            background-color: #6366f1;
            color: white;
        }

        QPushButton#primaryButton:hover {
            background-color: #4f46e5;
        }

        QPushButton#primaryButton:pressed {
            background-color: #4338ca;
        }
    """


# Цветовая палитра - темная тема
class Colors:
    """Цветовая палитра приложения - темная тема"""

    # Основные цвета
    PRIMARY = "#6366f1"
    PRIMARY_DARK = "#4f46e5"
    PRIMARY_DARKER = "#4338ca"

    SUCCESS = "#10b981"
    SUCCESS_DARK = "#059669"
    SUCCESS_DARKER = "#047857"

    DANGER = "#ef4444"
    DANGER_DARK = "#dc2626"
    DANGER_DARKER = "#b91c1c"

    WARNING = "#f59e0b"
    WARNING_DARK = "#d97706"

    # Фоновые цвета
    BACKGROUND = "#1a1d1f"
    CARD_BACKGROUND = "#272b30"
    INPUT_BACKGROUND = "#1f2327"

    # Текст
    TEXT_PRIMARY = "#ffffff"
    TEXT_SECONDARY = "#9ca3af"
    TEXT_DISABLED = "#6b7280"

    # Границы
    BORDER = "#3a3f47"
    BORDER_FOCUS = "#6366f1"

    # Статусы (темный фон)
    STATUS_RUNNING_BG = "#1e3a5f"
    STATUS_RUNNING_TEXT = "#60a5fa"

    STATUS_SUCCESS_BG = "#064e3b"
    STATUS_SUCCESS_TEXT = "#34d399"

    STATUS_ERROR_BG = "#7f1d1d"
    STATUS_ERROR_TEXT = "#f87171"

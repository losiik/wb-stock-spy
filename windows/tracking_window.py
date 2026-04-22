from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QProgressBar,
    QHBoxLayout
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from styles import get_tracking_window_stylesheet


class TrackingWindow(QMainWindow):
    """Окно отслеживания процесса заказа товара"""

    # Сигнал для остановки процесса
    stop_requested = pyqtSignal()

    def __init__(self, product_name: str, parent=None):
        super().__init__(parent)
        self.product_name = product_name
        self.ordered_count = 0
        self.is_running = True

        self.setWindowTitle("WB StockSpy")
        self.setMinimumSize(600, 400)
        self.setStyleSheet(get_tracking_window_stylesheet())

        self._init_ui()

    def _init_ui(self):
        """Инициализация интерфейса"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)

        # Название товара
        product_label = QLabel(f"Отслеживание: {self.product_name}")
        product_label.setObjectName("productTitle")
        product_label.setWordWrap(True)
        product_label.setMinimumHeight(50)

        # Карточка статуса
        status_card = self._create_status_card()

        # Карточка счетчика
        counter_card = self._create_counter_card()

        # Индикатор загрузки
        loading_card = self._create_loading_card()

        # Кнопка остановки
        self.stop_btn = QPushButton("Остановить и вернуться")
        self.stop_btn.setObjectName("dangerButton")
        self.stop_btn.setMinimumHeight(50)
        self.stop_btn.clicked.connect(self._on_stop_clicked)

        # Добавляем все элементы
        main_layout.addWidget(product_label)
        main_layout.addWidget(status_card)
        main_layout.addWidget(counter_card)
        main_layout.addWidget(loading_card)
        main_layout.addStretch()
        main_layout.addWidget(self.stop_btn)

        central_widget.setLayout(main_layout)

    def _create_status_card(self):
        """Создает карточку статуса"""
        card = QFrame()
        card.setObjectName("card")

        layout = QVBoxLayout()
        layout.setContentsMargins(25, 20, 25, 20)
        layout.setSpacing(10)

        # Горизонтальный layout для заголовка и статуса
        status_row = QHBoxLayout()
        status_row.setSpacing(15)

        # Заголовок
        title = QLabel("Статус:")
        title.setObjectName("cardTitle")
        title.setFixedWidth(80)

        # Статус
        self.status_label = QLabel("Работает")
        self.status_label.setObjectName("statusRunning")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setMinimumHeight(45)
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        self.status_label.setFont(font)

        status_row.addWidget(title)
        status_row.addWidget(self.status_label)
        status_row.addStretch()

        layout.addLayout(status_row)

        card.setLayout(layout)
        return card

    def _create_counter_card(self):
        """Создает карточку счетчика заказов"""
        card = QFrame()
        card.setObjectName("card")

        layout = QVBoxLayout()
        layout.setContentsMargins(25, 20, 25, 20)
        layout.setSpacing(10)

        # Горизонтальный layout для заголовка и счетчика
        counter_row = QHBoxLayout()
        counter_row.setSpacing(15)

        # Заголовок
        title = QLabel("Заказано товаров:")
        title.setObjectName("cardTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        # Счетчик
        self.counter_label = QLabel("0")
        self.counter_label.setObjectName("counterLabel")
        self.counter_label.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        self.counter_label.setMinimumHeight(40)
        font = QFont()
        font.setPointSize(32)
        font.setBold(True)
        self.counter_label.setFont(font)

        counter_row.addWidget(title)
        counter_row.addWidget(self.counter_label)
        counter_row.addStretch()

        layout.addLayout(counter_row)

        card.setLayout(layout)
        return card

    def _create_loading_card(self):
        """Создает карточку с индикатором загрузки"""
        card = QFrame()
        card.setObjectName("card")

        layout = QVBoxLayout()
        layout.setContentsMargins(25, 20, 25, 20)
        layout.setSpacing(15)

        # Заголовок
        title = QLabel("Процесс выполнения")
        title.setObjectName("cardTitle")

        # Progress bar (бесконечный)
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimumHeight(30)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setRange(0, 0)  # Бесконечная прокрутка

        # Текст статуса
        self.progress_text = QLabel("Проверка наличия товара...")
        self.progress_text.setObjectName("progressText")
        self.progress_text.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(title)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.progress_text)

        card.setLayout(layout)
        return card

    def set_status_running(self):
        """Устанавливает статус 'Работает'"""
        self.is_running = True
        self.status_label.setText("Работает")
        self.status_label.setObjectName("statusRunning")
        self.status_label.setStyleSheet("")
        self.status_label.style().unpolish(self.status_label)
        self.status_label.style().polish(self.status_label)

    def set_status_completed(self):
        """Устанавливает статус 'Завершено'"""
        self.is_running = False
        self.status_label.setText("✓ Завершено")
        self.status_label.setObjectName("statusCompleted")
        self.status_label.setStyleSheet("")
        self.status_label.style().unpolish(self.status_label)
        self.status_label.style().polish(self.status_label)

        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(100)
        self.progress_text.setText("Все задачи выполнены")

        self.stop_btn.setText("Вернуться на главный экран")
        self.stop_btn.setObjectName("primaryButton")
        # Принудительно обновляем стили кнопки
        self.stop_btn.style().unpolish(self.stop_btn)
        self.stop_btn.style().polish(self.stop_btn)

    def set_status_error(self, error_message: str = ""):
        """Устанавливает статус 'Ошибка'"""
        self.is_running = False
        self.status_label.setText("✗ Завершилось с ошибкой")
        self.status_label.setObjectName("statusError")
        self.status_label.setStyleSheet("")
        self.status_label.style().unpolish(self.status_label)
        self.status_label.style().polish(self.status_label)

        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)

        if error_message:
            self.progress_text.setText(f"Ошибка: {error_message}")
        else:
            self.progress_text.setText("Произошла ошибка")

        self.stop_btn.setText("Вернуться на главный экран")
        self.stop_btn.setObjectName("primaryButton")
        # Принудительно обновляем стили кнопки
        self.stop_btn.style().unpolish(self.stop_btn)
        self.stop_btn.style().polish(self.stop_btn)

    def update_counter(self, count: int):
        """Обновляет счетчик заказанных товаров"""
        self.ordered_count = count
        self.counter_label.setText(str(count))

    def increment_counter(self):
        """Увеличивает счетчик на 1"""
        self.ordered_count += 1
        self.counter_label.setText(str(self.ordered_count))

    def set_progress_text(self, text: str):
        """Устанавливает текст прогресса"""
        self.progress_text.setText(text)

    def _on_stop_clicked(self):
        """Обработчик кнопки остановки"""
        print(f"[TrackingWindow] Кнопка нажата, is_running={self.is_running}")

        # Всегда отправляем сигнал, независимо от статуса
        self.stop_requested.emit()
        print("[TrackingWindow] Сигнал stop_requested отправлен")

    def closeEvent(self, event):
        """Обработчик закрытия окна"""
        print("[TrackingWindow] closeEvent вызван")
        if self.is_running:
            print("[TrackingWindow] Отправка сигнала при закрытии")
            self.stop_requested.emit()
        event.accept()
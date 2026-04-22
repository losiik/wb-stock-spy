import time

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QIntValidator
from PyQt6.QtWidgets import (
    QMainWindow,
    QPushButton,
    QLabel,
    QLineEdit,
    QVBoxLayout,
    QWidget,
    QFrame,
    QScrollArea,
    QMessageBox,
    QRadioButton,
    QButtonGroup
)
from styles import get_main_window_stylesheet

from custom_widgets.no_scroll_combo_box import NoScrollComboBox

from models.models import Product, Settings
from wb_account_auth import WildberriesSession
from services.product_service import ProductService
from services.settings_service import SettingsService
from windows.tracking_window import TrackingWindow
from threads.tracking_thread import TrackingThread


class MainWindow(QMainWindow):
    def __init__(
            self,
            product_service: ProductService,
            wb_session: WildberriesSession,
            settings_service: SettingsService
    ):
        super().__init__()

        self.wb_session = wb_session
        self.product_service = product_service
        self.settings_service = settings_service

        self.setWindowTitle("WB StockSpy")
        self.setMinimumSize(QSize(800, 600))
        self.resize(800, 900)

        # Создаем scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        # Контейнер для контента
        content_widget = QWidget()

        # Основной layout с отступами
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)

        # Заголовок приложения
        title_label = QLabel("Отслеживать товар")
        title_label.setObjectName("mainTitle")
        title_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        title_label.setMinimumHeight(50)
        main_layout.addWidget(title_label)

        # Карточка аккаунта
        account_card = self.account_login(
            is_authorized=self.wb_session.load_session_data() is not None
        )
        main_layout.addWidget(account_card)

        # Карточка выбора товара
        card1 = self.create_selection_card()
        main_layout.addWidget(card1)

        # Карточка добавления нового товара
        card2 = self.create_add_card()
        main_layout.addWidget(card2)

        # Карточка лимита по цене
        card3 = self.create_price_card()
        main_layout.addWidget(card3)

        # Карточка лимита выкупа
        card4 = self.create_purchase_limit_card()
        main_layout.addWidget(card4)

        # Кнопка запуска
        self.button_start = QPushButton("Запустить отслеживание")
        self.button_start.setObjectName("startButton")
        self.button_start.setMinimumHeight(60)
        self.button_start.clicked.connect(self.on_start)
        main_layout.addWidget(self.button_start)

        main_layout.addStretch()

        # Устанавливаем layout в контейнер
        content_widget.setLayout(main_layout)

        # Добавляем контейнер в scroll area
        scroll.setWidget(content_widget)

        # Устанавливаем scroll area как центральный виджет
        self.setCentralWidget(scroll)

        # Применяем стили
        self.setStyleSheet(get_main_window_stylesheet())

    def account_login(self, is_authorized: bool = False):
        """Статус входа в аккаунт вб"""
        card = QFrame()
        card.setObjectName("account")

        layout = QVBoxLayout()
        layout.setContentsMargins(25, 20, 25, 20)
        layout.setSpacing(15)

        label = QLabel("Аккаунт WB")
        label.setObjectName("cardTitle")
        label.setMinimumHeight(25)

        # Сохраняем ссылку на label для обновления
        self.label_authorized = QLabel()
        self.label_authorized.setMinimumHeight(20)
        self.label_authorized.setWordWrap(True)

        # Сохраняем ссылку на кнопку
        self.button_authorize = QPushButton()
        self.button_authorize.setMinimumHeight(50)

        # Подключаем обработчик
        self.button_authorize.clicked.connect(self.on_authorize_clicked)

        # Устанавливаем начальное состояние
        self.update_auth_status(is_authorized)

        layout.addWidget(label)
        layout.addWidget(self.label_authorized)
        layout.addWidget(self.button_authorize)

        card.setLayout(layout)
        return card

    def create_selection_card(self):
        """Карточка выбора существующего товара"""
        items = self.product_service.get_all_products_name()
        card = QFrame()
        card.setObjectName("card")

        layout = QVBoxLayout()
        layout.setContentsMargins(25, 20, 25, 20)
        layout.setSpacing(15)

        label = QLabel("Выберите товар")
        label.setObjectName("cardTitle")
        label.setMinimumHeight(25)

        self.combo = NoScrollComboBox()
        self.combo.addItems([
            "None"
        ])
        self.combo.addItems(items)
        settings = self.settings_service.get_settings()
        if settings is not None:
            last_product = self.product_service.get_by_id(product_id=settings.last_product_id)
            self.combo.setCurrentText(last_product.name)
        self.combo.setMinimumHeight(50)

        layout.addWidget(label)
        layout.addWidget(self.combo)

        card.setLayout(layout)
        return card

    def create_add_card(self):
        """Карточка добавления нового товара"""
        card = QFrame()
        card.setObjectName("card")

        layout = QVBoxLayout()
        layout.setContentsMargins(25, 20, 25, 20)
        layout.setSpacing(15)

        label = QLabel("Добавить новый товар")
        label.setObjectName("cardTitle")
        label.setMinimumHeight(25)

        self.line_new_goods = QLineEdit()
        self.line_new_goods.setPlaceholderText("https://www.wildberries.ru/catalog/...")
        self.line_new_goods.setMinimumHeight(50)

        self.button_add = QPushButton("Добавить")
        self.button_add.setObjectName("secondaryButton")
        self.button_add.setMinimumHeight(50)
        self.button_add.clicked.connect(self.on_add_clicked)

        layout.addWidget(label)
        layout.addWidget(self.line_new_goods)
        layout.addWidget(self.button_add)

        card.setLayout(layout)
        return card

    def create_price_card(self):
        """Карточка установки лимита цены"""
        card = QFrame()
        card.setObjectName("card")

        layout = QVBoxLayout()
        layout.setContentsMargins(25, 20, 25, 20)
        layout.setSpacing(15)

        label = QLabel("Лимит по цене")
        label.setObjectName("cardTitle")
        label.setMinimumHeight(25)

        desc_label = QLabel("Бот не скупает выше указанной цены")
        desc_label.setObjectName("description")
        desc_label.setMinimumHeight(20)
        desc_label.setWordWrap(True)

        self.line_price = QLineEdit()

        validator = QIntValidator(0, 99999999, self)
        self.line_price.setValidator(validator)

        settings = self.settings_service.get_settings()
        if settings is not None and settings.price is not None:
            self.line_price.setText(str(settings.price))
        else:
            self.line_price.setPlaceholderText("Например: 15000")
        self.line_price.setMinimumHeight(50)

        self.price_error_label = QLabel("")
        self.price_error_label.setObjectName("errorLabel")
        self.price_error_label.setVisible(False)
        self.price_error_label.setWordWrap(True)

        self.line_price.textChanged.connect(self._validate_price)

        layout.addWidget(label)
        layout.addWidget(desc_label)
        layout.addWidget(self.line_price)
        layout.addWidget(self.price_error_label)

        card.setLayout(layout)
        return card

    def update_auth_status(self, is_authorized: bool):
        """Обновляет UI в зависимости от статуса авторизации"""
        self.is_authorized = is_authorized

        if self.is_authorized:
            self.label_authorized.setText("✓ Аккаунт Wildberries подключен")
            self.label_authorized.setObjectName("statusSuccess")

            self.button_authorize.setText("Отключить аккаунт")
            self.button_authorize.setObjectName("dangerButton")
        else:
            self.label_authorized.setText("○ Аккаунт Wildberries не подключен")
            self.label_authorized.setObjectName("statusInactive")

            self.button_authorize.setText("Подключить аккаунт")
            self.button_authorize.setObjectName("secondaryButton")

        # Обновляем стили
        self.label_authorized.setStyle(self.label_authorized.style())
        self.button_authorize.setStyle(self.button_authorize.style())

    def on_authorize_clicked(self):
        """Обработчик нажатия на кнопку авторизации"""
        if self.is_authorized:
            print("Отключение аккаунта...")
            self.unauthorize_account()
            self.update_auth_status(False)
        else:
            print("Подключение аккаунта...")
            success = self.authorize_account()
            if success:
                self.update_auth_status(True)

    def authorize_account(self) -> bool:
        """Логика авторизации аккаунта WB"""
        return self.wb_session.authorize(wait_timeout=300)

    def unauthorize_account(self):
        return self.wb_session.clear_session()

    def on_add_clicked(self):
        """Обработчик добавления нового товара"""
        new_product_url = self.line_new_goods.text().strip()

        if not new_product_url:
            QMessageBox.warning(
                self,
                "Пустое поле",
                "Введите URL или ID товара"
            )
            return

        # Пробуем создать продукт
        product = self.product_service.create_product(url=new_product_url)

        if product is None:
            # Показываем окно с ошибкой
            QMessageBox.critical(
                self,
                "Ошибка",
                "Не удалось найти товар.\n\n"
                "Проверьте:\n"
                "• Правильность URL\n"
                "• Существование товара\n"
                "• Подключение к интернету"
            )
            return

        # Успешно добавлен
        self.combo.addItem(product.name, userData=product.id)
        self.combo.setCurrentText(product.name)
        self.line_new_goods.clear()

        # Показываем успех (опционально)
        QMessageBox.information(
            self,
            "Успешно",
            f"Товар добавлен:\n{product.name}"
        )

    def _validate_price(self, text: str):
        """Валидация поля цены"""
        if not text:
            self.price_error_label.setVisible(False)
            self.line_price.setProperty("error", False)
            self.line_price.style().unpolish(self.line_price)
            self.line_price.style().polish(self.line_price)
            return

        try:
            price = int(text)

            if price < 0:
                self._show_price_error("Цена не может быть отрицательной")
            elif price == 0:
                self._show_price_error("Цена должна быть больше 0")
            else:
                self.price_error_label.setVisible(False)
                self.line_price.setProperty("error", False)
                self.line_price.style().unpolish(self.line_price)
                self.line_price.style().polish(self.line_price)

        except ValueError:
            self._show_price_error("Введите целое число без пробелов и символов")

    def _show_price_error(self, message: str):
        """Показывает сообщение об ошибке"""
        self.price_error_label.setText(message)
        self.price_error_label.setVisible(True)
        # Вместо прямого setStyleSheet используем property
        self.line_price.setProperty("error", True)
        self.line_price.style().unpolish(self.line_price)
        self.line_price.style().polish(self.line_price)

    def get_price_value(self) -> int | None:
        """Получает значение цены с валидацией"""
        text = self.line_price.text().strip()

        if not text:
            return None

        try:
            price = int(text)

            if price <= 0:
                self._show_price_error("Цена должна быть больше 0")
                return None

            return price

        except ValueError:
            self._show_price_error("Введите корректное число")
            return None

    def _open_tracking_window(self, product: Product, settings: Settings):
        """Открывает окно отслеживания"""
        # Создаем окно отслеживания
        self.tracking_window = TrackingWindow(
            f"{product.name} wb_id: {product.wb_product_id}",
            parent=self
        )

        # Создаем поток отслеживания
        self.tracking_thread = TrackingThread(
            product=product,
            settings=settings,
            wb_session=self.wb_session
        )

        # Подключаем сигналы потока к методам окна
        self.tracking_thread.status_updated.connect(
            self.tracking_window.set_progress_text
        )
        self.tracking_thread.progress_updated.connect(
            self.tracking_window.set_progress_text
        )
        self.tracking_thread.counter_updated.connect(
            self.tracking_window.update_counter
        )
        self.tracking_thread.tracking_completed.connect(
            self._on_tracking_completed
        )
        self.tracking_thread.tracking_error.connect(
            self._on_tracking_error
        )

        # Подключаем сигнал остановки из окна к потоку
        self.tracking_window.stop_requested.connect(
            self._on_tracking_stopped
        )

        # Показываем окно
        self.tracking_window.show()
        self.hide()

        # Запускаем поток
        self.tracking_thread.start()

    def _on_tracking_completed(self):
        """Обработчик успешного завершения"""
        if self.tracking_window:
            self.tracking_window.set_status_completed()

    def _on_tracking_error(self, error_message: str):
        """Обработчик ошибки"""
        if self.tracking_window:
            self.tracking_window.set_status_error(error_message)

    def _on_tracking_stopped(self):
        """Обработчик остановки отслеживания"""
        print("[MainWindow] Получен сигнал остановки")

        # Останавливаем поток (если он еще работает)
        if hasattr(self, 'tracking_thread') and self.tracking_thread:
            if self.tracking_thread.isRunning():
                print("[MainWindow] Останавливаем поток...")
                self.tracking_thread.stop()
            self.tracking_thread = None

        # Показываем главное окно
        self.show()

        # Закрываем окно отслеживания
        if self.tracking_window:
            # Отключаем сигнал, чтобы не было рекурсии
            try:
                self.tracking_window.stop_requested.disconnect()
            except:
                pass

            self.tracking_window.close()
            self.tracking_window = None

        print("[MainWindow] Возврат на главный экран завершен")

    def _show_error(self, message: str):
        """Показывает сообщение об ошибке"""
        QMessageBox.warning(self, "Ошибка", message)

    def create_purchase_limit_card(self):
        """Карточка установки лимита выкупа"""

        card = QFrame()
        card.setObjectName("card")

        layout = QVBoxLayout()
        layout.setContentsMargins(25, 20, 25, 20)
        layout.setSpacing(15)

        # Заголовок
        label = QLabel("Лимит выкупа")
        label.setObjectName("cardTitle")
        label.setMinimumHeight(25)
        layout.addWidget(label)

        settings = self.settings_service.get_settings()
        if settings is not None:
            unlimited = settings.unlimited
            amount = settings.amount
        else:
            unlimited = False
            amount = 1

        # Группа радиокнопок (только один выбор)
        self.purchase_mode_group = QButtonGroup(self)

        # Радиокнопка 1: Количество товара
        self.radio_quantity = QRadioButton("Указать количество товара")
        self.radio_quantity.setObjectName("radioButton")
        self.radio_quantity.setMinimumHeight(30)
        self.radio_quantity.setChecked(not unlimited)  # По умолчанию выбрано
        self.purchase_mode_group.addButton(self.radio_quantity, 1)
        layout.addWidget(self.radio_quantity)

        # Поле для ввода количества
        self.line_quantity = QLineEdit()
        self.line_quantity.setPlaceholderText("Введите количество")
        self.line_quantity.setMinimumHeight(50)
        if not unlimited:
            self.line_quantity.setText(str(amount))
        quantity_validator = QIntValidator(1, 9999999, self)
        self.line_quantity.setValidator(quantity_validator)

        layout.addWidget(self.line_quantity)

        # Сообщение об ошибке для количества
        self.quantity_error_label = QLabel("")
        self.quantity_error_label.setObjectName("errorLabel")
        self.quantity_error_label.setVisible(False)
        self.quantity_error_label.setWordWrap(True)
        layout.addWidget(self.quantity_error_label)

        # Радиокнопка 2: Пост-оплата
        self.radio_postpay = QRadioButton("Выкупать пока доступна пост-оплата")
        self.radio_postpay.setObjectName("radioButton")
        self.radio_postpay.setMinimumHeight(30)
        self.radio_postpay.setChecked(unlimited)
        self.purchase_mode_group.addButton(self.radio_postpay, 2)
        layout.addWidget(self.radio_postpay)

        # Подключаем обработчики
        self.radio_quantity.toggled.connect(self._on_mode_changed)
        self.radio_postpay.toggled.connect(self._on_mode_changed)
        self.line_quantity.textChanged.connect(self._validate_quantity)

        card.setLayout(layout)
        return card

    def _on_mode_changed(self, checked: bool):
        """Обработчик изменения режима выкупа"""
        if self.radio_quantity.isChecked():
            # Включаем поле количества
            self.line_quantity.setEnabled(True)
            self._validate_quantity(self.line_quantity.text())
        else:
            # Отключаем поле количества
            self.line_quantity.setEnabled(False)
            self.quantity_error_label.setVisible(False)
            self.line_quantity.setProperty("error", False)
            self.line_quantity.style().unpolish(self.line_quantity)
            self.line_quantity.style().polish(self.line_quantity)

    def _validate_quantity(self, text: str):
        """Валидация поля количества"""
        # Проверяем только если выбран режим "количество"
        if not self.radio_quantity.isChecked():
            return

        if not text:
            self._show_quantity_error("Укажите количество товара")
            return

        try:
            quantity = int(text)

            if quantity <= 0:
                self._show_quantity_error("Количество должно быть больше 0")
            else:
                # Валидное значение
                self.quantity_error_label.setVisible(False)
                self.line_quantity.setProperty("error", False)
                self.line_quantity.style().unpolish(self.line_quantity)
                self.line_quantity.style().polish(self.line_quantity)

        except ValueError:
            self._show_quantity_error("Введите целое число")

    def _show_quantity_error(self, message: str):
        """Показывает сообщение об ошибке количества"""
        self.quantity_error_label.setText(message)
        self.quantity_error_label.setVisible(True)
        self.line_quantity.setProperty("error", True)
        self.line_quantity.style().unpolish(self.line_quantity)
        self.line_quantity.style().polish(self.line_quantity)

    def get_purchase_mode(self) -> dict | None:
        """Получает выбранный режим выкупа"""
        if self.radio_quantity.isChecked():
            quantity_text = self.line_quantity.text().strip()

            if not quantity_text:
                self._show_quantity_error("Укажите количество товара")
                return None

            try:
                quantity = int(quantity_text)
                if quantity <= 0:
                    self._show_quantity_error("Количество должно быть больше 0")
                    return None

                return {
                    "mode": "quantity",
                    "value": quantity
                }
            except ValueError:
                self._show_quantity_error("Введите корректное число")
                return None
        else:
            return {
                "mode": "postpay",
                "value": None
            }

    def on_start(self):
        product_name = self.combo.currentText()
        current_price = self.line_price.text()

        product = self.product_service.get_by_name(product_name=product_name)

        if self.radio_quantity.isChecked():
            unlimited = False
            amount = int(self.line_quantity.text())
        else:
            amount = None
            unlimited = True

        settings = self.settings_service.create_settings(
            last_product_id=product.id,
            price=current_price,
            unlimited=unlimited,
            amount=amount
        )

        self._open_tracking_window(
            product,
            settings
        )

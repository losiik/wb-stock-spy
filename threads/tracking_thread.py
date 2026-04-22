import time

from PyQt6.QtCore import QThread, pyqtSignal

from models.models import Product, Settings
from wb_account_auth import WildberriesSession


class TrackingThread(QThread):
    """Поток для отслеживания товара в фоне"""

    # Сигналы для передачи данных в GUI
    status_updated = pyqtSignal(str)  # Обновление текста статуса
    progress_updated = pyqtSignal(str)  # Обновление прогресса
    counter_updated = pyqtSignal(int)  # Обновление счетчика
    tracking_completed = pyqtSignal()  # Отслеживание завершено
    tracking_error = pyqtSignal(str)  # Произошла ошибка

    def __init__(
            self,
            product: Product,
            settings: Settings,
            wb_session: WildberriesSession
    ):
        super().__init__()
        self.product = product
        self.settings = settings
        self.wb_session = wb_session
        self.is_running = True
        self.ordered_count = 0

    def run(self):
        """Основной метод потока - выполняется в фоне"""
        try:
            self.status_updated.emit("Запуск браузера...")
            self.progress_updated.emit("Инициализация сессии...")

            # Открываем авторизованную сессию
            if not self.wb_session.open_authorized_session():
                self.tracking_error.emit("Не удалось открыть сессию. Проверьте авторизацию.")
                return

            self.progress_updated.emit("Переход на страницу товара...")

            # Получаем содержимое страницы
            page_content = self.wb_session.get_page_content(self.product.url)

            if not page_content:
                self.tracking_error.emit("Не удалось загрузить страницу товара")
                return

            # Основной цикл отслеживания
            max_attempts = self.settings.amount if not self.settings.unlimited else float('inf')

            while self.is_running and self.ordered_count < max_attempts:
                self.wb_session.driver.refresh()
                print(f"Попытка заказа #{self.ordered_count + 1}...")
                self.progress_updated.emit(f"Попытка заказа #{self.ordered_count + 1}...")

                # Пытаемся нажать "Купить сейчас"
                if self.wb_session.click_buy_now():
                    self.progress_updated.emit("Кнопка 'Купить сейчас' нажата")
                    print("Кнопка 'Купить сейчас' нажата")

                    # Проверяем наличие оплаты при получении
                    if self.wb_session.find_on_receipt():
                        self.progress_updated.emit("Найдена опция 'При получении'")
                        print("Найдена опция 'При получении'")

                        # Пытаемся оформить заказ
                        if self.wb_session.click_order():
                            self.ordered_count += 1
                            self.counter_updated.emit(self.ordered_count)
                            self.progress_updated.emit(f"✓ Заказ #{self.ordered_count} оформлен!")
                            print(f"✓ Заказ #{self.ordered_count} оформлен!")

                            # Проверяем лимит
                            if not self.settings.unlimited and self.ordered_count >= self.settings.amount:
                                self.progress_updated.emit("Достигнут лимит заказов")
                                break
                        else:
                            self.progress_updated.emit("Кнопка заказа недоступна")
                            print("Кнопка заказа недоступна")
                    else:
                        self.progress_updated.emit("Пост-оплата недоступна")
                        print("Пост-оплата недоступна")

                        if not self.settings.unlimited:
                            self.tracking_error.emit("Пост-оплата недоступна, но выбран режим с лимитом")
                            return
                else:
                    self.progress_updated.emit("Товар недоступен для покупки")

                # Небольшая пауза перед следующей попыткой
                self.msleep(200)  # 0.2 секунды

            # Завершение
            if self.is_running:
                self.tracking_completed.emit()

        except Exception as e:
            self.tracking_error.emit(f"Произошла ошибка: {str(e)}")

        finally:
            # Закрываем сессию
            time.sleep(3)
            if self.wb_session:
                self.wb_session.close()

    def stop(self):
        """Останавливает поток"""
        self.is_running = False
        self.quit()
        self.wait()

import sys
import traceback
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QMessageBox

from wb_account_auth import WildberriesSession
from windows.main_window import MainWindow

from db_manager import initialize_database
from services.name_scrapper_service import NameScrapperService
from services.product_service import ProductService
from services.settings_service import SettingsService


def get_data_dir(subdir=None):
    """Получает директорию для данных"""
    if getattr(sys, 'frozen', False):
        base = Path(sys.executable).parent
    else:
        base = Path(__file__).parent
    if subdir:
        base = base / subdir
    base.mkdir(parents=True, exist_ok=True)
    return base


def show_error_dialog(title, message):
    """Показывает диалог с ошибкой"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    msg_box = QMessageBox()
    msg_box.setIcon(QMessageBox.Icon.Critical)
    msg_box.setWindowTitle(title)
    msg_box.setText(message)
    msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
    msg_box.exec()


def main():
    """Главная функция приложения"""
    try:
        print("\n" + "=" * 60)
        print("ЗАПУСК WB STOCKSPY")
        print("=" * 60)

        # Определяем, запущено ли из exe
        if getattr(sys, 'frozen', False):
            print("Режим: Запущено из EXE")
            print(f"Путь к exe: {sys.executable}")
        else:
            print("Режим: Запущено из Python")

        print("=" * 60 + "\n")

        # Инициализация базы данных
        print("Шаг 1/4: Инициализация базы данных...")
        db_manager = initialize_database()

        if db_manager is None:
            error_msg = "Не удалось инициализировать базу данных"
            print(f"\n✗ {error_msg}")

            if getattr(sys, 'frozen', False):
                show_error_dialog("Ошибка инициализации", error_msg)

            input("\nНажмите Enter для выхода...")
            sys.exit(1)

        print("✓ База данных инициализирована\n")

        # Инициализация сервисов
        print("Шаг 2/4: Инициализация сервисов...")

        # WildberriesSession с правильными путями
        wb_data_dir = get_data_dir("wb_client_data")
        print(f"  WB данные: {wb_data_dir}")
        wb_session = WildberriesSession(base_dir=str(wb_data_dir))

        # Другие сервисы
        name_scrapper_service = NameScrapperService()
        product_service = ProductService(
            db=db_manager,
            name_scrapper_service=name_scrapper_service
        )
        settings_service = SettingsService(db=db_manager)

        print("✓ Все сервисы инициализированы\n")

        # Запуск GUI
        print("Шаг 3/4: Запуск графического интерфейса...")
        app = QApplication(sys.argv)

        print("Шаг 4/4: Создание главного окна...")

        try:
            window = MainWindow(
                product_service=product_service,
                settings_service=settings_service,
                wb_session=wb_session
            )
            print("✓ Окно создано\n")
        except Exception as e:
            error_details = f"Ошибка при создании главного окна:\n{str(e)}\n\n{traceback.format_exc()}"
            print(f"\n✗ {error_details}")

            if getattr(sys, 'frozen', False):
                show_error_dialog(
                    "Ошибка создания окна",
                    f"Не удалось создать главное окно.\n\nОшибка: {str(e)}\n\nПроверьте базу данных."
                )

            input("\nНажмите Enter для выхода...")
            sys.exit(1)

        print("=" * 60)
        print("ПРИЛОЖЕНИЕ УСПЕШНО ЗАПУЩЕНО")
        print("=" * 60 + "\n")

        window.show()

        return app.exec()

    except Exception as e:
        error_msg = f"Критическая ошибка: {str(e)}"
        print(f"\n{'=' * 60}")
        print("✗ КРИТИЧЕСКАЯ ОШИБКА")
        print("=" * 60)
        print(f"\n{error_msg}\n")
        print("Полная информация об ошибке:")
        print("-" * 60)
        traceback.print_exc()
        print("-" * 60)

        # Показываем диалог с ошибкой в exe
        if getattr(sys, 'frozen', False):
            show_error_dialog(
                "Критическая ошибка",
                f"{error_msg}\n\nПодробности в консоли."
            )

        input("\nНажмите Enter для выхода...")
        sys.exit(1)


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        print("\n\nПрограмма прервана пользователем")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ НЕОЖИДАННАЯ ОШИБКА: {e}")
        traceback.print_exc()

        if getattr(sys, 'frozen', False):
            show_error_dialog("Неожиданная ошибка", str(e))

        input("\nНажмите Enter для выхода...")
        sys.exit(1)

import sys
from pathlib import Path
from yoyo import read_migrations, get_backend
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker


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


def get_migrations_dir():
    """Получает директорию с миграциями"""
    if getattr(sys, 'frozen', False):
        # В exe миграции упакованы в _MEIPASS
        if hasattr(sys, '_MEIPASS'):
            return Path(sys._MEIPASS) / 'migrations'
        else:
            return get_data_dir() / 'migrations'
    else:
        # В разработке
        return Path(__file__).parent / 'migrations'


class DatabaseManager:
    """Менеджер базы данных с автоматической инициализацией"""

    def __init__(self, db_dir: str = None, db_name: str = "database.db"):
        """
        Инициализация менеджера БД

        Args:
            db_dir: Папка для базы данных (None = автоопределение)
            db_name: Имя файла базы данных
        """
        # Автоматически определяем директорию
        if db_dir is None:
            self.db_dir = get_data_dir("db")
        else:
            self.db_dir = Path(db_dir)

        self.db_path = self.db_dir / db_name

        # Определяем путь к миграциям
        self.migrations_dir = get_migrations_dir()

        # Создаем connection string для SQLite
        self.db_url = f"sqlite:///{self.db_path}"

        # Инициализируем БД при создании объекта
        self._initialize_database()

    def _initialize_database(self):
        """Создает папку, базу и применяет миграции"""
        # Шаг 1: Создаем папку db если её нет
        if not self.db_dir.exists():
            self.db_dir.mkdir(parents=True, exist_ok=True)
            print(f"✓ Создана папка: {self.db_dir}")

        # Проверяем наличие базы
        db_exists = self.db_path.exists()

        if not db_exists:
            print(f"✓ База данных будет создана: {self.db_path}")
        else:
            print(f"✓ База данных найдена: {self.db_path}")

        # Шаг 2: Проверяем наличие таблиц
        if db_exists and self._has_tables():
            print("✓ Таблицы уже существуют")
        else:
            # Применяем миграции
            self._apply_migrations()

    def _has_tables(self) -> bool:
        """Проверяет наличие таблиц в базе данных"""
        try:
            engine = create_engine(self.db_url, echo=False)
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            engine.dispose()

            # Проверяем наличие основных таблиц
            required_tables = ['product', 'settings']  # Добавь свои таблицы
            has_all = all(table in tables for table in required_tables)

            if has_all:
                print(f"✓ Найдены таблицы: {', '.join(tables)}")
                return True
            else:
                print(f"⚠ Не все таблицы найдены. Существующие: {', '.join(tables)}")
                return False

        except Exception as e:
            print(f"⚠ Ошибка проверки таблиц: {e}")
            return False

    def _apply_migrations(self):
        """Применяет все непримененные миграции"""
        if not self.migrations_dir.exists():
            print(f"⚠ Папка миграций не найдена: {self.migrations_dir}")

            # В exe это нормально, если таблицы уже есть
            if getattr(sys, 'frozen', False):
                if self._has_tables():
                    print("  (База уже инициализирована)")
                    return
                else:
                    # Критическая ошибка - нет ни миграций, ни таблиц
                    print("  ✗ ОШИБКА: Нет миграций и нет таблиц!")
                    print("  Создаю таблицы вручную...")
                    self._create_tables_manually()
                    return

            # В разработке создаем папку
            self.migrations_dir.mkdir(parents=True, exist_ok=True)
            print(f"✓ Создана папка миграций: {self.migrations_dir}")
            return

        try:
            # Подключаемся к базе через yoyo
            backend = get_backend(self.db_url)
            migrations = read_migrations(str(self.migrations_dir))

            # Получаем список непримененных миграций
            unapplied = backend.to_apply(migrations)

            if unapplied:
                print(f"⏳ Применение {len(unapplied)} миграций...")

                # Применяем миграции
                with backend.lock():
                    backend.apply_migrations(unapplied)

                print("✓ Миграции успешно применены:")
                for migration in unapplied:
                    print(f"  - {migration.id}")
            else:
                print("✓ Все миграции уже применены")

        except Exception as e:
            print(f"⚠ Ошибка при применении миграций: {e}")

            # Пробуем создать таблицы вручную
            if not self._has_tables():
                print("  Попытка создать таблицы вручную...")
                self._create_tables_manually()

    def _create_tables_manually(self):
        """
        Создает таблицы вручную, если миграции недоступны
        ВАЖНО: Замени это на свои модели SQLAlchemy!
        """
        try:
            from models.models import Base  # Импортируй свой Base

            engine = create_engine(self.db_url, echo=False)
            Base.metadata.create_all(engine)
            engine.dispose()

            print("✓ Таблицы созданы вручную")

        except ImportError:
            print("✗ Не удалось импортировать модели для создания таблиц")
            print("  Убедись, что models/models.py содержит Base и все модели")
        except Exception as e:
            print(f"✗ Ошибка создания таблиц: {e}")

    def get_engine(self):
        """Возвращает SQLAlchemy engine"""
        return create_engine(self.db_url, echo=False)

    def get_session(self):
        """Создает и возвращает новую сессию SQLAlchemy"""
        engine = self.get_engine()
        Session = sessionmaker(bind=engine)
        return Session()

    def check_database_status(self):
        """Выводит информацию о состоянии базы данных"""
        print("\n" + "=" * 60)
        print("СТАТУС БАЗЫ ДАННЫХ")
        print("=" * 60)
        print(f"Папка БД:    {self.db_dir.absolute()}")
        print(f"Файл БД:     {self.db_path.absolute()}")
        print(f"Существует:  {'Да' if self.db_path.exists() else 'Нет'}")

        if self.db_path.exists():
            size = self.db_path.stat().st_size
            print(f"Размер:      {size} байт")

        # Проверяем таблицы
        try:
            engine = create_engine(self.db_url, echo=False)
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            engine.dispose()

            print(f"\nТаблицы:     {', '.join(tables) if tables else 'Нет таблиц'}")
        except:
            print("\nТаблицы:     Не удалось проверить")

        # Проверяем примененные миграции
        if self.migrations_dir.exists():
            try:
                backend = get_backend(self.db_url)
                migrations = read_migrations(str(self.migrations_dir))
                applied = list(backend.to_mark_done(migrations))

                print(f"\nМиграции:")
                print(f"  Всего:      {len(list(migrations))}")
                print(f"  Применено:  {len(applied)}")
            except:
                print("\nМиграции:    Не удалось проверить")

        print("=" * 60 + "\n")


# Для удобства - синглтон инстанс
_db_manager_instance = None


def get_db_manager() -> DatabaseManager:
    """Возвращает единственный экземпляр DatabaseManager (синглтон)"""
    global _db_manager_instance
    if _db_manager_instance is None:
        _db_manager_instance = DatabaseManager()
    return _db_manager_instance


def initialize_database():
    """Инициализирует базу данных при запуске приложения"""
    try:
        print("\n" + "=" * 60)
        print("ИНИЦИАЛИЗАЦИЯ БАЗЫ ДАННЫХ")
        print("=" * 60 + "\n")

        # Создаем менеджер БД (автоматически создает папку, базу и применяет миграции)
        db = DatabaseManager()

        # Показываем статус
        db.check_database_status()

        print("✓ База данных готова к работе\n")
        return db

    except Exception as e:
        print(f"\n✗ КРИТИЧЕСКАЯ ОШИБКА при инициализации БД: {e}")
        import traceback
        traceback.print_exc()
        return None
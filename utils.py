import sys
from pathlib import Path


def get_base_dir() -> Path:
    """
    Получает базовую директорию приложения
    Работает и в Python, и в exe
    """
    if getattr(sys, 'frozen', False):
        # Запущено из exe
        base_dir = Path(sys.executable).parent
    else:
        # Запущено из Python
        base_dir = Path(__file__).parent

    return base_dir


def get_data_dir(subdir: str = None) -> Path:
    """
    Получает директорию для данных

    Args:
        subdir: Поддиректория (например, 'db', 'wb_client_data')
    """
    base_dir = get_base_dir()

    if subdir:
        data_dir = base_dir / subdir
    else:
        data_dir = base_dir

    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def get_migrations_dir() -> Path:
    """Получает директорию с миграциями"""
    if getattr(sys, 'frozen', False):
        # В exe миграции должны быть упакованы
        # PyInstaller распаковывает в _MEIPASS
        if hasattr(sys, '_MEIPASS'):
            return Path(sys._MEIPASS) / 'migrations'
        else:
            return get_base_dir() / 'migrations'
    else:
        # В разработке
        return Path(__file__).parent / 'migrations'

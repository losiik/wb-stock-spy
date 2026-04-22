# -*- mode: python ; coding: utf-8 -*-
# wb_stockspy.spec - Конфигурация для сборки WB StockSpy

block_cipher = None

a = Analysis(
    ['main.py'],  # Главный файл приложения
    pathex=[],
    binaries=[],
    datas=[
        # Включаем папку с миграциями базы данных
        ('migrations', 'migrations'),

        # Если есть иконка, раскомментируй:
        # ('icon.ico', '.'),

        # Если есть другие ресурсы (шрифты, картинки и т.д.):
        # ('resources', 'resources'),
    ],
    hiddenimports=[
        # PyQt6
        'PyQt6',
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'PyQt6.sip',

        # Selenium и undetected-chromedriver
        'selenium',
        'selenium.webdriver',
        'selenium.webdriver.common.by',
        'selenium.webdriver.common.keys',
        'selenium.webdriver.support.ui',
        'selenium.webdriver.support.expected_conditions',
        'selenium.webdriver.chrome.service',
        'selenium.webdriver.chrome.options',
        'selenium.common.exceptions',
        'undetected_chromedriver',
        'undetected_chromedriver.patcher',

        # SQLAlchemy и базы данных
        'sqlalchemy',
        'sqlalchemy.orm',
        'sqlalchemy.ext.declarative',
        'sqlalchemy.pool',
        'sqlite3',  # Драйвер SQLite (используется)

        # Yoyo migrations
        'yoyo',
        'yoyo.migrations',

        # Модели приложения (ВАЖНО!)
        'models',
        'models.models',

        # Стандартные библиотеки (на всякий случай)
        'pathlib',
        'json',
        'time',
        'shutil',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Исключаем ненужные модули для уменьшения размера
        'tkinter',
        'matplotlib',
        'numpy',
        'pandas',
        'PIL',
        'scipy',
        'IPython',
        'pytest',
        'unittest',
        'test',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='WB_StockSpy',  # Имя exe файла
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # Сжатие (можно отключить если долго собирается)
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # TRUE = с консолью (для отладки), FALSE = без консоли (для релиза)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # icon='icon.ico',  # Раскомментируй если есть иконка
)
import time
import json
import shutil
import sys
from pathlib import Path
from typing import Optional, Dict

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    StaleElementReferenceException,
    ElementClickInterceptedException,
    WebDriverException
)


class WildberriesSession:
    def __init__(
            self,
            base_dir: str = None,  # Теперь опциональный
            profile_dir: str = None,
            cookies_file: str = None,
            local_storage_file: str = None,
            session_storage_file: str = None,
            session_file: str = None
    ):
        """
        Инициализация класса

        Args:
            base_dir: Базовая директория (None = автоопределение)
            ...
        """
        # Автоматическое определение базовой директории
        if base_dir is None:
            if getattr(sys, 'frozen', False):
                # Запущено из exe
                base_dir = Path(sys.executable).parent / "wb_client_data"
            else:
                # Запущено из Python
                base_dir = Path(__file__).parent / "wb_client_data"

        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(exist_ok=True)

        # Остальные пути с правильными значениями по умолчанию
        if profile_dir:
            self.profile_dir = Path(profile_dir)
        else:
            self.profile_dir = self.base_dir / "wb_chrome_profile"

        if cookies_file:
            self.cookies_file = Path(cookies_file)
        else:
            self.cookies_file = self.base_dir / "wb_cookies.json"

        if local_storage_file:
            self.local_storage_file = Path(local_storage_file)
        else:
            self.local_storage_file = self.base_dir / "wb_localstorage.json"

        if session_storage_file:
            self.session_storage_file = Path(session_storage_file)
        else:
            self.session_storage_file = self.base_dir / "wb_sessionstorage.json"

        if session_file:
            self.session_file = Path(session_file)
        else:
            self.session_file = self.base_dir / "wb_session.json"

        # Создаем директории
        self.profile_dir.mkdir(exist_ok=True)

        self.driver = None
        self.is_authorized = False

        # CSS/XPath селекторы
        self.buy_now_css = '#reactContainers button[aria-label="Купить сейчас"]'
        self.on_receipt_xpath = "//button[contains(@class,'tabs-switch__text') and normalize-space()='При получении']"
        self.order_css = 'button[name="ConfirmOrderByRegisteredUser"].j-btn-confirm-order'

    def _init_driver(self, use_profile: bool = True) -> uc.Chrome:
        """
        Инициализирует ChromeDriver с настройками для обхода защиты

        Args:
            use_profile: Использовать ли сохраненный профиль Chrome
        """
        options = uc.ChromeOptions()
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-blink-features=AutomationControlled")

        # Используем сохраненный профиль Chrome
        if use_profile:
            options.add_argument(f"--user-data-dir={self.profile_dir.absolute()}")
            options.add_argument("--profile-directory=Default")
            print(f"✓ Используется профиль: {self.profile_dir.absolute()}")

        options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        # Отключаем уведомления
        prefs = {
            "profile.default_content_setting_values.notifications": 2,
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False
        }
        options.add_experimental_option("prefs", prefs)

        driver = uc.Chrome(options=options, use_subprocess=True)
        return driver

    def save_cookies(self) -> None:
        """Сохраняет cookies в файл"""
        if not self.driver:
            raise RuntimeError("Driver не инициализирован")

        cookies = self.driver.get_cookies()
        with open(self.cookies_file, 'w', encoding='utf-8') as f:
            json.dump(cookies, f, ensure_ascii=False, indent=2)
        print(f"✓ Сохранено {len(cookies)} cookies в {self.cookies_file}")

    def load_cookies(self) -> bool:
        """Загружает cookies из файла"""
        if not self.cookies_file.exists():
            print(f"⚠ Файл {self.cookies_file} не найден")
            return False

        if not self.driver:
            raise RuntimeError("Driver не инициализирован")

        try:
            with open(self.cookies_file, 'r', encoding='utf-8') as f:
                cookies = json.load(f)

            added_count = 0
            for cookie in cookies:
                try:
                    # Удаляем проблемные поля
                    if 'sameSite' in cookie and cookie['sameSite'] not in ['Strict', 'Lax', 'None']:
                        cookie.pop('sameSite')
                    if 'expiry' in cookie:
                        cookie['expiry'] = int(cookie['expiry'])

                    self.driver.add_cookie(cookie)
                    added_count += 1
                except Exception as e:
                    print(f"⚠ Не удалось добавить cookie {cookie.get('name', 'unknown')}: {e}")

            print(f"✓ Загружено {added_count}/{len(cookies)} cookies")
            return True

        except Exception as e:
            print(f"✗ Ошибка загрузки cookies: {e}")
            return False

    def save_local_storage(self) -> None:
        """Сохраняет localStorage в файл"""
        if not self.driver:
            raise RuntimeError("Driver не инициализирован")

        try:
            local_storage = self.driver.execute_script(
                "return JSON.stringify(window.localStorage);"
            )

            with open(self.local_storage_file, 'w', encoding='utf-8') as f:
                f.write(local_storage)

            items_count = len(json.loads(local_storage))
            print(f"✓ Сохранено {items_count} элементов localStorage в {self.local_storage_file}")

        except Exception as e:
            print(f"✗ Ошибка сохранения localStorage: {e}")

    def load_local_storage(self) -> bool:
        """Загружает localStorage из файла"""
        if not self.local_storage_file.exists():
            print(f"⚠ Файл {self.local_storage_file} не найден")
            return False

        if not self.driver:
            raise RuntimeError("Driver не инициализирован")

        try:
            with open(self.local_storage_file, 'r', encoding='utf-8') as f:
                local_storage = f.read()

            # Экранирование для безопасной передачи в JavaScript
            local_storage_escaped = local_storage.replace("\\", "\\\\").replace("'", "\\'")

            self.driver.execute_script(
                f"Object.entries(JSON.parse('{local_storage_escaped}')).forEach(([key, value]) => "
                "{ window.localStorage.setItem(key, value); });"
            )

            items_count = len(json.loads(local_storage))
            print(f"✓ Загружено {items_count} элементов localStorage")
            return True

        except Exception as e:
            print(f"✗ Ошибка загрузки localStorage: {e}")
            return False

    def save_session_storage(self) -> None:
        """Сохраняет sessionStorage в файл"""
        if not self.driver:
            raise RuntimeError("Driver не инициализирован")

        try:
            session_storage = self.driver.execute_script(
                "return JSON.stringify(window.sessionStorage);"
            )

            with open(self.session_storage_file, 'w', encoding='utf-8') as f:
                f.write(session_storage)

            items_count = len(json.loads(session_storage))
            print(f"✓ Сохранено {items_count} элементов sessionStorage в {self.session_storage_file}")

        except Exception as e:
            print(f"✗ Ошибка сохранения sessionStorage: {e}")

    def load_session_storage(self) -> bool:
        """Загружает sessionStorage из файла"""
        if not self.session_storage_file.exists():
            print(f"⚠ Файл {self.session_storage_file} не найден")
            return False

        if not self.driver:
            raise RuntimeError("Driver не инициализирован")

        try:
            with open(self.session_storage_file, 'r', encoding='utf-8') as f:
                session_storage = f.read()

            # Экранирование для безопасной передачи в JavaScript
            session_storage_escaped = session_storage.replace("\\", "\\\\").replace("'", "\\'")

            self.driver.execute_script(
                f"Object.entries(JSON.parse('{session_storage_escaped}')).forEach(([key, value]) => "
                "{ window.sessionStorage.setItem(key, value); });"
            )

            items_count = len(json.loads(session_storage))
            print(f"✓ Загружено {items_count} элементов sessionStorage")
            return True

        except Exception as e:
            print(f"✗ Ошибка загрузки sessionStorage: {e}")
            return False

    def save_session_data(self, user_data: Dict = None) -> None:
        """Сохраняет данные сессии в JSON"""
        session_data = {
            'is_authorized': self.is_authorized,
            'timestamp': time.time(),
            'user_data': user_data or {},
            'profile_dir': str(self.profile_dir.absolute())
        }

        with open(self.session_file, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, ensure_ascii=False, indent=2)

        print(f"✓ Данные сессии сохранены в {self.session_file}")

    def load_session_data(self) -> Optional[Dict]:
        """Загружает данные сессии из JSON"""
        if not self.session_file.exists():
            print(f"⚠ Файл {self.session_file} не найден")
            return None

        try:
            with open(self.session_file, 'r', encoding='utf-8') as f:
                session_data = json.load(f)

            self.is_authorized = session_data.get('is_authorized', False)
            print(f"✓ Данные сессии загружены из {self.session_file}")
            return session_data

        except Exception as e:
            print(f"✗ Ошибка загрузки сессии: {e}")
            return None

    def wait_for_authorization(self, timeout: int = 300) -> bool:
        """
        Ожидает появление элементов авторизации

        Args:
            timeout: Максимальное время ожидания в секундах

        Returns:
            True если авторизация успешна, False если таймаут
        """
        if not self.driver:
            raise RuntimeError("Driver не инициализирован")

        print("\n" + "=" * 60)
        print("🔐 ОЖИДАНИЕ АВТОРИЗАЦИИ")
        print("=" * 60)
        print("Пожалуйста, войдите в аккаунт Wildberries в открывшемся окне браузера")
        print(f"Максимальное время ожидания: {timeout} секунд")
        print("=" * 60 + "\n")

        # XPath элементов для проверки
        auth_xpaths = [
            '//*[@id="diamondsMenu"]/div/ul/li[7]',
            '//*[@id="header"]/div/div[2]/div[4]/div[4]/a'
        ]

        try:
            wait = WebDriverWait(self.driver, timeout, poll_frequency=2)

            print("⏳ Ожидание появления элемента авторизации...")

            # Ждем появления любого из элементов
            def wait_auth_elements(driver):
                wait = WebDriverWait(driver, timeout)
                elements = []

                for xpath in auth_xpaths:
                    try:
                        element = wait.until(
                            EC.visibility_of_element_located((By.XPATH, xpath))
                        )
                        print(f"\n✓ Найден элемент: {xpath}")
                        elements.append(element)
                    except Exception as e:
                        print(f"\n✗ Не найден элемент: {xpath}")

                return elements

            element = wait.until(wait_auth_elements)

            if element:
                print("✓ Авторизация обнаружена!")
                self.is_authorized = True

                # Даем время на полную загрузку данных профиля
                print("⏳ Ожидание загрузки данных профиля...")
                time.sleep(10)  # Увеличили время для полной синхронизации

                return True

        except TimeoutException:
            print(f"\n✗ Таймаут: элементы авторизации не появились за {timeout} секунд")
            return False
        except Exception as e:
            print(f"\n✗ Ошибка при ожидании авторизации: {e}")
            return False

        return False

    def debug_page_state(self) -> None:
        """Отладочная информация о состоянии страницы"""
        if not self.driver:
            return

        print("\n" + "=" * 60)
        print("🔍 ОТЛАДОЧНАЯ ИНФОРМАЦИЯ")
        print("=" * 60)

        # URL
        print(f"URL: {self.driver.current_url}")

        # Cookies
        cookies = self.driver.get_cookies()
        print(f"\nCookies: {len(cookies)} шт.")
        important_cookies = ['WBToken', 'BasketUID', '__wba']
        for cookie in cookies:
            if cookie.get('name') in important_cookies:
                print(f"  ✓ {cookie.get('name')}: {cookie.get('value')[:30]}...")

        # localStorage
        try:
            local_storage_str = self.driver.execute_script(
                "return JSON.stringify(window.localStorage);"
            )
            local_storage = json.loads(local_storage_str)
            print(f"\nlocalStorage: {len(local_storage)} элементов")

            # Ищем токен в localStorage
            important_keys = ['wbtoken', 'user', 'auth', 'token', 'access']
            for key in local_storage.keys():
                if any(imp_key in key.lower() for imp_key in important_keys):
                    value = str(local_storage[key])
                    print(f"  ✓ {key}: {value[:50]}...")
        except Exception as e:
            print(f"\nlocalStorage: ошибка - {e}")

        # sessionStorage
        try:
            session_storage_str = self.driver.execute_script(
                "return JSON.stringify(window.sessionStorage);"
            )
            session_storage = json.loads(session_storage_str)
            print(f"\nsessionStorage: {len(session_storage)} элементов")
        except Exception as e:
            print(f"\nsessionStorage: ошибка - {e}")

        # Проверка элементов авторизации
        auth_xpaths = [
            '//*[@id="header"]/div/div[2]/div[4]/div[2]/a',
            '//*[@id="diamondsMenu"]/div/ul/li[9]'
        ]

        print("\nПроверка элементов авторизации:")
        for xpath in auth_xpaths:
            try:
                element = self.driver.find_element(By.XPATH, xpath)
                if element:
                    print(f"  ✓ Найден: {xpath}")
                    print(f"    Видим: {element.is_displayed()}")
                    print(f"    Текст: {element.text[:50]}")
            except Exception as e:
                print(f"  ✗ Не найден: {xpath}")

        print("=" * 60 + "\n")

    def authorize(self, wait_timeout: int = 300) -> bool:
        """
        Открывает браузер для авторизации и сохраняет сессию

        Args:
            wait_timeout: Максимальное время ожидания авторизации в секундах

        Returns:
            True если авторизация успешна
        """
        try:
            # Используем профиль для базового сохранения
            self.driver = self._init_driver(use_profile=True)
            self.driver.get('https://www.wildberries.ru/')

            # Ждем загрузки страницы
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            print("✓ Страница Wildberries загружена")
            time.sleep(5)

            # Ожидаем авторизацию по появлению элементов
            if self.wait_for_authorization(timeout=wait_timeout):
                # Даем дополнительное время на синхронизацию
                print("⏳ Сохранение данных сессии...")
                time.sleep(5)

                # Сохраняем все данные
                self.save_cookies()
                self.save_local_storage()
                self.save_session_storage()
                self.save_session_data()

                # Отладочная информация
                self.debug_page_state()

                print("\n" + "=" * 60)
                print("✓ АВТОРИЗАЦИЯ ЗАВЕРШЕНА УСПЕШНО!")
                print(f"✓ Профиль Chrome сохранен в: {self.profile_dir.absolute()}")
                print("✓ Cookies сохранены")
                print("✓ localStorage сохранен")
                print("✓ sessionStorage сохранен")
                print("✓ Сессия сохранена")
                print("=" * 60 + "\n")
                self.close()

                return True
            else:
                print("\n✗ Не удалось авторизоваться")
                return False

        except Exception as e:
            print(f"\n✗ Ошибка при авторизации: {e}")
            import traceback
            traceback.print_exc()
            return False

        finally:
            if self.driver:
                input("\nНажмите Enter для закрытия браузера...")
                self.driver.quit()
                self.driver = None

    def open_authorized_session(self, debug: bool = False) -> bool:
        """
        Открывает браузер с загруженной сессией

        Args:
            debug: Показывать ли отладочную информацию

        Returns:
            True если сессия успешно восстановлена
        """
        try:
            # Инициализируем драйвер с профилем
            self.driver = self._init_driver(use_profile=True)

            # Сначала открываем страницу для установки домена
            self.driver.get('https://www.wildberries.ru/')

            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            print("✓ Страница загружена")
            time.sleep(3)

            # Загружаем cookies
            cookies_loaded = self.load_cookies()

            # Загружаем localStorage
            local_storage_loaded = self.load_local_storage()

            # Загружаем sessionStorage
            session_storage_loaded = self.load_session_storage()

            if cookies_loaded or local_storage_loaded or session_storage_loaded:
                # Перезагружаем страницу для применения данных
                print("⏳ Применение сохраненных данных...")
                self.driver.refresh()

                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )

                time.sleep(7)  # Даем время на восстановление сессии

                if debug:
                    self.debug_page_state()

                # Проверяем авторизацию
                if self.check_authorization_status():
                    print("✓ Сессия успешно восстановлена!")
                    print("✓ Вы авторизованы")
                    return True
                else:
                    print("⚠ Данные загружены, но авторизация не подтверждена")
                    print("Возможно, сессия устарела. Выполните авторизацию заново.")

                    if debug:
                        input("\nНажмите Enter для продолжения...")

                    return False
            else:
                print("✗ Не удалось загрузить сохраненные данные")
                print("Сначала выполните авторизацию через authorize()")
                return False

        except Exception as e:
            print(f"✗ Ошибка при восстановлении сессии: {e}")
            import traceback
            traceback.print_exc()
            return False

    def get_page_content(self, url: str = 'https://www.wildberries.ru/') -> Optional[str]:
        """
        Получает содержимое страницы

        Args:
            url: URL страницы для загрузки

        Returns:
            HTML содержимое страницы или None
        """
        if not self.driver:
            print("✗ Driver не инициализирован. Используйте open_authorized_session() сначала")
            return None

        try:
            self.driver.get(url)
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            time.sleep(2)

            return self.driver.page_source

        except Exception as e:
            print(f"✗ Ошибка при загрузке страницы: {e}")
            return None

    def check_authorization_status(self) -> bool:
        """
        Проверяет статус авторизации

        Returns:
            True если авторизован, False если нет
        """
        if not self.driver:
            return False

        auth_xpaths = [
            '//*[@id="header"]/div/div[2]/div[4]/div[2]/a',
            '//*[@id="diamondsMenu"]/div/ul/li[9]'
        ]

        for xpath in auth_xpaths:
            try:
                element = self.driver.find_element(By.XPATH, xpath)
                if element and element.is_displayed():
                    self.is_authorized = True
                    return True
            except:
                continue

        self.is_authorized = False
        return False

    def close(self) -> None:
        """Закрывает браузер"""
        if self.driver:
            self.driver.quit()
            self.driver = None
            print("✓ Браузер закрыт")

    def clear_session(self) -> None:
        """Удаляет все сохраненные данные сессии"""
        if self.profile_dir.exists():
            shutil.rmtree(self.profile_dir, ignore_errors=True)
            print(f"✓ Профиль удален: {self.profile_dir}")

        self.cookies_file.unlink(missing_ok=True)
        self.local_storage_file.unlink(missing_ok=True)
        self.session_storage_file.unlink(missing_ok=True)
        self.session_file.unlink(missing_ok=True)
        self.is_authorized = False
        print("✓ Все данные сессии удалены")

    def __enter__(self):
        """Поддержка контекстного менеджера"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Автоматическое закрытие при выходе из контекста"""
        self.close()

    def click_buy_now(self) -> bool:
        try:
            WebDriverWait(self.driver, 2).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, self.buy_now_css))
            )
        except TimeoutException:
            return False

        elements = self.driver.find_elements(By.CSS_SELECTOR, self.buy_now_css)
        for el in elements:
            try:
                if not el.is_displayed() or not el.is_enabled():
                    continue

                self.driver.execute_script(
                    "arguments[0].scrollIntoView({block:'center'});", el
                )

                WebDriverWait(self.driver, 3).until(lambda d: el.is_displayed() and el.is_enabled())

                try:
                    el.click()
                except ElementClickInterceptedException:
                    self.driver.execute_script("arguments[0].click();", el)

                return True

            except (StaleElementReferenceException, WebDriverException):
                continue

        return False

    def find_on_receipt(self) -> bool:
        try:
            WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located((By.XPATH, self.on_receipt_xpath))
            )
            return True
        except TimeoutException:
            return False

    def click_order(self) -> bool:
        try:
            WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, self.order_css))
            )
        except TimeoutException:
            return False

        elements = self.driver.find_elements(By.CSS_SELECTOR, self.order_css)
        for el in elements:
            try:
                if not el.is_displayed() or not el.is_enabled():
                    continue

                self.driver.execute_script(
                    "arguments[0].scrollIntoView({block:'center'});", el
                )

                WebDriverWait(self.driver, 3).until(lambda d: el.is_displayed() and el.is_enabled())

                try:
                    el.click()
                except ElementClickInterceptedException:
                    self.driver.execute_script("arguments[0].click();", el)

                return True

            except (StaleElementReferenceException, WebDriverException):
                continue

        return False

    def check_out_of_stock_xpath(self) -> bool:
        """
        Проверяет наличие элемента "Нет в наличии" по XPath

        Returns:
            True если товар НЕ в наличии, False если в наличии
        """
        try:
            element = WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located((
                    By.XPATH,
                    "//h2[contains(@class, 'soldOutProduct') and contains(normalize-space(), 'Нет в наличии')]"
                ))
            )
            return True
        except TimeoutException:
            return False


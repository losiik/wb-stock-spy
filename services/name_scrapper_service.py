import re
import requests
from typing import Optional
from requests.exceptions import RequestException, HTTPError, Timeout


class NameScrapperService:
    """Сервис для получения информации о товарах Wildberries"""

    def __init__(self, timeout: int = 10):
        """
        Инициализация сервиса

        Args:
            timeout: Таймаут запросов в секундах
        """
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def validate_url(self, url: str) -> bool:
        """
        Проверяет URL на соответствие шаблону Wildberries

        Args:
            url: URL или ID товара

        Returns:
            True если URL валиден
        """
        # Паттерн для URL Wildberries
        url_pattern = r'^https?://(?:www\.)?wildberries\.ru/catalog/(\d+)/detail\.aspx'

        # Паттерн для ID (только цифры, 6-12 символов)
        id_pattern = r'^\d{6,12}$'

        # Проверяем полный URL
        if re.match(url_pattern, url):
            return True

        # Проверяем что это валидный ID
        if re.match(id_pattern, url):
            return True

        return False

    def get_product_id(self, url: str) -> Optional[str]:
        """
        Извлекает ID товара из URL

        Args:
            url: URL страницы товара или ID

        Returns:
            ID товара или None
        """
        # Если это не валидный URL - возвращаем None
        if not self.validate_url(url):
            return None

        # Пробуем извлечь из URL
        match = re.search(r'/catalog/(\d+)', url)
        if match:
            return match.group(1)

        # Если это просто число (ID)
        if url.isdigit() and len(url) >= 6 and len(url) <= 12:
            return url

        return None

    def get_url_for_product_data(self, product_id: str) -> str:
        url = (
            f"https://spb-basket-cdn-03bl.geobasket.ru/vol{product_id[:4]}/"
            f"part{product_id[:6]}/{product_id}/info/ru/card.json"
        )
        return url

    def get_url_for_product_data_v2(self, product_id: str) -> str:
        url = (
            f"https://spb-basket-cdn-03bl.geobasket.ru/vol{product_id[:3]}/"
            f"part{product_id[:5]}/{product_id}/info/ru/card.json"
        )
        return url

    def make_request(self, url: str) -> Optional[dict]:
        """
        Выполняет HTTP запрос и возвращает JSON

        Args:
            url: URL для запроса

        Returns:
            Словарь с данными или None при ошибке
        """
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()  # Вызовет исключение для 4xx/5xx

            return response.json()

        except HTTPError as e:
            if e.response.status_code == 404:
                print(f"✗ Товар не найден (404): {url}")
            else:
                print(f"✗ HTTP ошибка {e.response.status_code}: {url}")
            return None

        except Timeout:
            print(f"✗ Превышен таймаут запроса: {url}")
            return None

        except RequestException as e:
            print(f"✗ Ошибка запроса: {e}")
            return None

        except ValueError as e:
            print(f"✗ Ошибка парсинга JSON: {e}")
            return None

    def check_product_exists(self, product_id: str) -> bool:
        """
        Проверяет существование товара по ID

        Args:
            product_id: ID товара

        Returns:
            True если товар существует
        """
        search_url = self.get_url_for_product_data(product_id)
        product_data = self.make_request(search_url)

        return product_data is not None

    def check_product_name(self, url: str) -> Optional[dict]:
        if not self.validate_url(url):
            return None

        product_id = self.get_product_id(url)
        if not product_id:
            return None

        search_url = self.get_url_for_product_data(product_id)
        product_data = self.make_request(search_url)

        if product_data is None:
            search_url = self.get_url_for_product_data_v2(product_id)
            product_data = self.make_request(search_url)

        if product_data is None:
            print(f"✗ Товар с ID {product_id} не найден или недоступен")
            return None

        try:
            name = product_data.get("imt_name")

            if not name:
                print(f"✗ В данных товара отсутствует название")
                return None

            print(f"✓ Получено название для ID {product_id}: {name}")
            return {"name": name, "product_id": int(product_id)}

        except (KeyError, TypeError) as e:
            print(f"✗ Ошибка при извлечении названия: {e}")
            return None

    def close(self):
        """Закрывает сессию"""
        self.session.close()

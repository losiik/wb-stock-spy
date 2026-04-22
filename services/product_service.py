from datetime import datetime
from typing import Optional

from db_manager import DatabaseManager
from models.models import Product
from services.name_scrapper_service import NameScrapperService


class ProductService:
    def __init__(
            self,
            db: DatabaseManager,
            name_scrapper_service: NameScrapperService
    ):
        self.db = db
        self.db.check_database_status()
        self.session = self.db.get_session()
        self.name_scrapper_service = name_scrapper_service

    def create_product(self, url: str) -> Optional[Product]:
        product_dict = self.name_scrapper_service.check_product_name(url=url)
        if product_dict is None:
            return None

        product = Product(
            name=product_dict["name"],
            wb_product_id=product_dict["product_id"],
            url=url,
            created_at=datetime.now()
        )

        self.session.add(product)
        self.session.commit()

        return product

    def get_all_products_name(self) -> list[str]:
        products = self.session.query(Product).all()
        products_name = [product.name for product in products]
        return products_name

    def get_by_id(self, product_id: int) -> Product:
        return self.session.query(Product).filter(Product.id == product_id).first()

    def get_by_name(self, product_name: str) -> Product:
        return self.session.query(Product).filter(Product.name == product_name).first()

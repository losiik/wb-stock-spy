from typing import Optional

from db_manager import DatabaseManager
from models.models import Settings


class SettingsService:
    def __init__(
            self,
            db: DatabaseManager
    ):
        self.db = db
        self.db.check_database_status()
        self.session = self.db.get_session()

    def create_settings(
            self,
            last_product_id: int,
            unlimited: bool,
            amount: int = None,
            price: int = None
    ) -> Settings:
        settings = Settings(
            last_product_id=last_product_id,
            unlimited=unlimited,
            amount=amount,
            price=price
        )
        self.session.add(settings)
        self.session.commit()
        return settings

    def get_settings(self) -> Optional[Settings]:
        try:
            settings = self.session.query(Settings).order_by(Settings.id.desc()).first()
            return settings
        except:
            return None

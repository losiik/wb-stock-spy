CREATE TABLE settings (
            id INTEGER PRIMARY KEY,
            last_product_id INTEGER,
            price INTEGER,
            FOREIGN KEY (last_product_id) REFERENCES product(id) ON DELETE CASCADE
        )
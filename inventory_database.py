import json

class InventoryDatabase:
    def __init__(self, db_file='data/inventory.json'):
        self.db_file = db_file

    def load_inventory(self) -> dict:
        try:
            with open(self.db_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def save_inventory(self, inventory: dict) -> None:
        with open(self.db_file, 'w') as f:
            json.dump(inventory, f, indent=4)

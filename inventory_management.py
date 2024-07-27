import typing
from datetime import datetime
from inventory_database import InventoryDatabase

class InventoryManagement:
    def __init__(self, db: InventoryDatabase):
        self.db = db

    def add_item(self, username: str, name: str, quantity: int, price: float, code: str, expiry_date: str, flag: bool = False) -> bool:
        inventory = self.db.load_inventory()
        user_inventory = inventory.setdefault(username, {})
        item_list = user_inventory.setdefault(name, [])
        item = {
            "id": len(item_list) + 1,
            "name": name,
            "quantity": quantity,
            "price": price,
            "code": code,
            "expiry_date": expiry_date,
            "created_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "flag": flag
        }
        item_list.append(item)
        self.db.save_inventory(inventory)
        return True

    def update_item(self, username: str, name: str, quantity: int, price: float, code: str, expiry_date: str) -> bool:
        inventory = self.db.load_inventory()
        user_inventory = inventory.get(username, [])
        for item in user_inventory:
            if item['name'] == name:
                item['quantity'] = quantity
                item['price'] = price
                item['code'] = code
                item['expiry_date'] = expiry_date
                self.db.save_inventory(inventory)
                return True
        return False

    def delete_item(self, username: str, code: str) -> bool:
        inventory = self.db.load_inventory()
        user_inventory = inventory.get(username, {})
        if code not in user_inventory:
            return False
        del user_inventory[code]
        inventory[username] = user_inventory
        self.db.save_inventory(inventory)
        return True

    def get_inventory(self, username: str) -> dict:
        inventory = self.db.load_inventory()
        return inventory.get(username, {})

    def get_top_users_for_item(self, item_name: str) -> typing.List[typing.Tuple[str, int]]:
        inventory = self.db.load_inventory()
        user_item_count = {}

        for username, items in inventory.items():
            count = sum(item['quantity'] for item in items.get(item_name, []))
            user_item_count[username] = count

        sorted_users = sorted(user_item_count.items(), key=lambda x: x[1], reverse=True)
        return sorted_users[:5]

    def flag_item(self, username, name):
        inventory = self.db.load_inventory()
        user_inventory = inventory.get(username, {})
        for item_list in user_inventory.values():
            for item in item_list:
                if item['name'] == name:
                    item['flag'] = True
                    self.db.save_inventory(inventory)
                    return True
        return False

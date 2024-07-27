import json

class UserDatabase:
    def __init__(self, db_file="data/users.json"):
        self.db_file = db_file

    def load_users(self):
        try:
            with open(self.db_file, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    def save_users(self, users):
        with open(self.db_file, "w") as f:
            json.dump(users, f)

import hashlib
import typing
from user_database import UserDatabase

class UserManagement:
    def __init__(self, db: UserDatabase):
        self.db = db

    def hash_password(self, password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    def register_user(self, username: str, password: str, role: str) -> bool:
        users = self.db.load_users()
        if any(user['username'] == username for user in users):
            return False
        users.append({"username": username, "password": self.hash_password(password), "role": role})
        self.db.save_users(users)
        return True

    def authenticate_user(self, username: str, password: str, role_required: typing.Optional[str] = None) -> typing.Tuple[bool, str]:
        users = self.db.load_users()
        hashed_password = self.hash_password(password)
        for user in users:
            if user['username'] == username and user['password'] == hashed_password:
                if role_required is None or user['role'] == role_required:
                    return True, user['role']
                else:
                    return False, None
        return False, None

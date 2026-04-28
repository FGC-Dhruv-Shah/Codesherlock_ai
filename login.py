import hashlib
import uuid
from datetime import datetime


class LoginPage:

    def __init__(self):
        self.users = {}
        self.logged_in_users = {}

    def register(self, username, password, email):
        if not username or not password or not email:
            print("All fields are required.")
            return False

        if username in self.users:
            print(f"Username '{username}' already exists.")
            return False

        if len(password) < 6:
            print("Password must be at least 6 characters.")
            return False

        self.users[username] = {
            "password": self._hash(password),
            "email": email,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        print(f"User '{username}' registered successfully.")
        return True

    def login(self, username, password):
        if username not in self.users:
            print("User not found.")
            return None

        if self.users[username]["password"] != self._hash(password):
            print("Incorrect password.")
            return None

        token = str(uuid.uuid4())
        self.logged_in_users[token] = username
        print(f"Login successful. Welcome, {username}!")
        return token

    def logout(self, token):
        if token not in self.logged_in_users:
            print("Invalid session.")
            return False

        username = self.logged_in_users.pop(token)
        print(f"User '{username}' logged out.")
        return True

    def is_logged_in(self, token):
        return token in self.logged_in_users

    def get_current_user(self, token):
        if not self.is_logged_in(token):
            print("No active session found.")
            return None
        return self.logged_in_users[token]

    def change_password(self, token, old_password, new_password):
        username = self.get_current_user(token)
        if not username:
            return False

        if self.users[username]["password"] != self._hash(old_password):
            print("Old password is incorrect.")
            return False

        if len(new_password) < 6:
            print("New password must be at least 6 characters.")
            return False

        self.users[username]["password"] = self._hash(new_password)
        print("Password changed successfully.")
        return True

    def get_user_info(self, token):
        username = self.get_current_user(token)
        if not username:
            return None

        user = self.users[username]
        return {
            "username": username,
            "email": user["email"],
            "created_at": user["created_at"],
        }

    def _hash(self, password):
        return hashlib.sha256(password.encode()).hexdigest()


if __name__ == "__main__":
    page = LoginPage()

    page.register("john", "pass123", "john@example.com")
    page.register("jane", "secure456", "jane@example.com")

    token = page.login("john", "pass123")
    print("Logged in:", page.is_logged_in(token))
    print("User info:", page.get_user_info(token))

    page.change_password(token, "pass123", "newpass789")
    page.logout(token)

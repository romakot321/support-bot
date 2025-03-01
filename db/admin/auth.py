from sqladmin import Admin
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from uuid import uuid4
import os

tokens = []


class AdminAuth(AuthenticationBackend):
    username = os.getenv("ADMIN_USERNAME", "admin")
    password = os.getenv("ADMIN_PASSWORD", "admin")

    @classmethod
    def _generate_token(cls) -> str:
        global tokens
        token = (str(uuid4()) + str(uuid4())).replace('-', '')
        tokens.append(token)
        return token

    async def login(self, request: Request) -> bool:
        form = await request.form()
        username, password = form["username"], form["password"]
        if username != self.username or password != self.password:
            return False

        request.session.update({"token": self._generate_token()})
        return True

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        global tokens
        token = request.session.get("token")
        if not token or token not in tokens:
            return False
        return True


authentication_backend = AdminAuth(secret_key=os.getenv("ADMIN_SECRET_KEY", "replaceme"))

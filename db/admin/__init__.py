from fastapi import FastAPI
from sqladmin import Admin
from .views import TaskView
from .auth import authentication_backend
from db import engine


def attach_admin_panel(application: FastAPI):
    admin = Admin(application, engine.engine, authentication_backend=authentication_backend)

    admin.add_view(TaskView)


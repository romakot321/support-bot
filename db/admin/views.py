from db.tables import Task
from sqladmin import ModelView


class TaskView(ModelView, model=Task):
    column_list = "__all__"
    column_searchable_list = [Task.id]
    column_default_sort = [(Task.id, True)]


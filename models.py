from pydantic import BaseModel

class TaskItem(BaseModel):
    task: str
    assignee: str
    deadline: str

from typing import Optional, Literal
from datetime import datetime

class Todo:
    def __init__(
        self,
        id: int,
        name: str,
        description: Optional[str] = None,
        deadline: Optional[datetime] = None,
        status: Literal["Done", "To do"] = "To do"
    ) -> None:
        self.id = id
        self.name = name
        self.description = description
        self.deadline = deadline
        self.status = status

    def edit() -> None:
        pass

    def change_status(self) -> None:
        self.status = "Done" if self.status == "To do" else "To do"
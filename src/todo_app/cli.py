from __future__ import annotations
import pytermgui as ptg
from pytermgui import boxes
from typing import Optional, Any
from datetime import datetime
import aiohttp
import asyncio
from functools import partial
import logging
import webbrowser
from .todo_class import Todo
import json
import time

logger = logging.getLogger(__name__)

todos_text = {
    "PL": "Zadania",
    "EN": "Tasks",
}
todo_text = {
    "PL": "Zadanie",
    "EN": "Task",
}
display_text = {
    "PL": "Wyświetl",
    "EN": "Display",
}
edit_text = {
    "PL": "Edytuj",
    "EN": "Edit",
}
add_text = todos_text = {
    "PL": "Dodaj",
    "EN": "Add",
}
name_text = {
    "PL": "Nazwa: ",
    "EN": "Name: ",
}
description_text = {
    "PL": "Opis: ",
    "EN": "Description: ",
}
deadline_text = {
    "PL": "Termin: ",
    "EN": "Deadline: ",
}
dateformat_text = {
    "PL": "Podaj datę w formacie rok-miesiac-dzien godzina:minuta:sekunda (Mozesz pominac czas)",
    "EN": "Input date should of format year-month-day hour:minute:second (You may ommit time)",
}
quit_text = {
    "PL": "Zgaś",
    "EN": "Quit",
}
change_status_text = {
    "PL": "Zmień status",
    "EN": "Change status",
}


class CLIView:
    def __init__(self, manager: ptg.WindowManager, api: str) -> None:
        self.manager: ptg.WindowManager = manager
        self.api: str = api
        self.user_todos: list[Todo] = asyncio.run(self.get_todos())
        self.todos_view: list[Todo] = []
        self.todos_window: Optional[ptg.Window] = None
        self.language = "EN"
        self.middle_window: Optional[ptg.Window] = None
        self.prompt: Optional[ptg.Window] = None
        self.display_todos()

    def display_todos(
        self,
    ) -> None:
        logger.info("Displaying todos")
        self.generate_todos_view("")
        todos_window = ptg.Window(overflow=ptg.Overflow.SCROLL)

        for todo in self.todos_view:
            todos_window.lazy_add(todo)

        tools_window = ptg.Window(
            ptg.Button(" ++ ", onclick=self.add_todo_view, centered=True),
            ptg.Label(" "),
            ptg.Button(
                " UI ",
                onclick=lambda *_: webbrowser.open("file:///Users/kpz/college_files/KCK/kck/src/frontend/build/index.html"),
            ),
            ptg.Label(""),
            ptg.Button(
                quit_text[self.language],
                onclick=lambda *_: self.manager.stop(),
                centered=True,
            ),
            ptg.Label(" "),
            ptg.Button(
                " " + self.language + " ", onclick=self.change_language, centered=True
            ),
            box="SINGLE",
        )
        self.manager.add(tools_window, assign="bodyleft")

    def generate_todos_view(self, sender) -> None:
        self.todos_view = []
        for todo in self.user_todos:
            todo_window = ptg.Container(
                ptg.Label(name_text[self.language] + todo.name, parent_align=0),
                ptg.Label(
                    description_text[self.language]
                    + (todo.description if todo.description is not None else ""),
                    parent_align=0,
                ),
                ptg.Label(
                    deadline_text[self.language]
                    + (str(todo.deadline) if todo.deadline is not None else ""),
                    parent_align=0,
                ),
                ptg.Label("Status: " + todo.status, parent_align=0),
                ptg.Button(
                    edit_text[self.language],
                    onclick=partial(self.edit_todo_view, todo=todo),
                ),
                "",
                ptg.Button(
                    change_status_text[self.language],
                    onclick=partial(self.change_status, todo=todo),
                ),
            )
            self.todos_view.append(todo_window)
        new_window = ptg.Window(overflow=ptg.Overflow.SCROLL)

        for todo in self.todos_view:
            new_window.lazy_add(todo)

        if self.todos_window is not None:
            self.manager.remove(self.todos_window)
        self.todos_window = new_window
        self.manager.add(self.todos_window, assign="bodyright")

    async def get_todos_false(self) -> list[Todo]:
        return [
            Todo(1, "First Todo", "Describing first Todo"),
            Todo(2, "Second Todo", None, datetime.utcnow()),
            Todo(3, "Third Todo", "Describing third Todo", datetime.utcnow()),
            Todo(4, "Fourth Todo", "Describing third Todo", datetime.utcnow()),
            Todo(4, "fif Todo", "Describing third Todo", datetime.utcnow()),
            Todo(4, "Fouraaaath Todo", "Describing third Todo", datetime.utcnow()),
            Todo(4, "Fourthbbb Todo", "Describing third Todo", datetime.utcnow()),
        ]

    async def get_todos(self) -> list[Todo]:
        async with aiohttp.ClientSession() as client:
            async with client.get(self.api + "/todo/") as resp:
                if resp.status == 200:
                    response_text = await resp.text()
                    return self.parse_todos(response_text)
                else:
                    resp_txt = await resp.text()
                    self.display_error(f"Response: {resp_txt} | Code: {resp.status}")

    def display_error(
        self,
        err_txt: str
    ) -> None:
        self.prompt = ptg.Window(
            ptg.Label(err_txt),
            ptg.Button("OK", onclick=lambda *_: self.hide_prompt()),
        )
        self.manager.add(self.prompt, assign="bodymiddle")

    def hide_prompt(
        self,
    ) -> None:
        self.manager.remove(self.prompt)
        self.prompt = None

    def parse_todos(self, response_text: str) -> list[Todo]:
        if len(response_text) == 0:
            return []
        response = json.loads(response_text)
        todos = []
        for json_object in response:
            todos.append(
                Todo(
                    id=json_object["id"],
                    name=json_object["name"],
                    description=json_object["description"],
                    deadline=datetime.fromisoformat(json_object["deadline"]),
                    status=json_object["status"],
                )
            )
        return todos

    def add_todo_view(self, sender) -> None:
        add_form = ptg.Window(
            ptg.Label(add_text[self.language] + " " + todo_text[self.language]),
            ptg.InputField("", prompt=name_text[self.language]),
            ptg.InputField("", prompt=description_text[self.language]),
            ptg.InputField("", prompt=deadline_text[self.language]),
            ptg.Label(dateformat_text[self.language]),
            ptg.Label(),
        )
        add_form.lazy_add(
            ptg.Button(
                add_text[self.language],
                onclick=partial(self.add_todo, window=add_form),
            )
        )
        if self.middle_window is not None:
            self.manager.remove(self.middle_window)
        if self.prompt is not None:
            self.manager.remove(self.prompt)
            self.prompt = None
        self.middle_window = add_form
        self.manager.add(add_form, "bodymiddle")

    def edit_todo_view(self, sender, todo: Todo) -> None:
        edit_form = ptg.Window(
            ptg.Label(edit_text[self.language] + " " + todo_text[self.language]),
            ptg.InputField(todo.name, prompt=name_text[self.language]),
            ptg.InputField(todo.description, prompt=description_text[self.language]),
            ptg.InputField(
                todo.deadline.isoformat(), prompt=deadline_text[self.language]
            ),
            ptg.Label(dateformat_text[self.language]),
            ptg.Label(),
        )
        edit_form.lazy_add(
            ptg.Button(
                edit_text[self.language],
                onclick=partial(self.edit_todo, window=edit_form),
            )
        )
        if self.middle_window is not None:
            self.manager.remove(self.middle_window)
        if self.prompt is not None:
            self.manager.remove(self.prompt)
            self.prompt = None
        self.middle_window = edit_form
        self.manager.add(edit_form, "bodymiddle")

    def add_todo(self, sender: ptg.Button, window: ptg.Window):
        fields = []
        for field in window:
            if isinstance(field, ptg.InputField):
                fields.append(field.value)
        new_todo = Todo(1, *fields)
        try:
            asyncio.run(self.post_todo(new_todo))
            logger.info("Finished adding to do")
        except Exception as e:
            logger.info(e)
            return
        self.user_todos = asyncio.run(self.get_todos())
        self.generate_todos_view("")

    def edit_todo(self, sender: ptg.Button, window: ptg.Window):
        fields = []
        for field in window:
            if isinstance(field, ptg.InputField):
                fields.append(field.value)
        new_todo = Todo(1, *fields)
        try:
            asyncio.run(self.put_todo(new_todo))
            logger.info("Finished adding to do")
        except Exception as e:
            logger.info(e)
            return
        self.user_todos = asyncio.run(self.get_todos())
        self.generate_todos_view("")

    async def post_todo(self, todo: Todo) -> None:
        async with aiohttp.ClientSession(self.api) as client:
            async with client.post(
                f"/todo/?name={todo.name}&description={todo.description}&deadline={todo.deadline}"
            ) as resp:
                resp_txt = await resp.text()
                self.display_error(f"Response: {resp_txt} | Code: {resp.status}")

    async def put_todo(self, todo: Todo) -> None:
        async with aiohttp.ClientSession(self.api) as client:
            async with client.put(
                f"/todo/{todo.id}?name={todo.name}&description={todo.description}&deadline={todo.deadline.isoformat()[:-6]}&status={todo.status}"
            ) as resp:
                resp_txt = await resp.text()
                self.display_error(f"Response: {resp_txt} | Code: {resp.status}")

    def rebuild_views(self) -> None:
        for window in self.manager._windows:
            logger.info(window)
        try:
            for i in range(len(self.manager._windows)):
                self.manager._windows.remove(0)
        except Exception as e:
            pass
        self.display_todos()

    def change_language(self, sender) -> None:
        self.language = "PL" if self.language == "EN" else "EN"
        self.rebuild_views()

    def change_status(self, sender: Any, todo: Todo) -> None:
        todo.change_status()
        asyncio.run(self.put_todo(todo))
        self.generate_todos_view("")

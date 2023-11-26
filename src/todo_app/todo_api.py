from fastapi import APIRouter, Response
from fastapi.responses import JSONResponse
import logging
from datetime import datetime, date, time
from typing import Optional
import duckdb
import pandas as pd

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/todo")
duckfile = "todo_db.duckdb"
todo_table = "TODO_TABLE"


@router.get("/")
async def get_todos() -> Response:
    create_db()
    try:
        with duckdb.connect(duckfile, read_only=True) as conn:
            result = conn.sql(f"SELECT * FROM {todo_table}")
            response = []
            try:
                for res in result.fetchall():
                    response.append(
                        {
                            "id": res[0],
                            "name": res[1],
                            "description": res[2],
                            "deadline": res[3],
                            "status": res[4],
                        }
                    )
                return response
            except Exception as e:
                logger.critical(e)
    except Exception as e:
        logger.info(e)
    return Response(None, status_code=500)


@router.post("/")
async def post_todo(
    name: str,
    description: Optional[str],
    deadline: Optional[datetime | date],
    status: str = "To do",
) -> Response:
    create_db()
    with duckdb.connect(duckfile, read_only=False) as conn:
        try:
            if isinstance(deadline, date):
                deadline = datetime.combine(deadline, time.min)
            df = pd.DataFrame(
                {
                    "id": (
                        conn.sql("SELECT nextval('todo_id') as next_value").fetchall()
                    )[0],
                    "name": name,
                    "description": description,
                    "deadline": deadline,
                    "status": status,
                },
                index=[0],
            )
            logger.info(df)
            conn.append(f"{todo_table}", df)
            conn.commit()
            logger.info("commit successfull")
        except duckdb.ConstraintException as e:
            return Response("Task with such name already exists", 409)
    return Response(None, 200)


@router.put("/{todo_id}")
async def put_todo(
    todo_id: int,
    name: Optional[str],
    description: Optional[str],
    deadline: Optional[datetime | date],
    status: Optional[str],
) -> Response:
    with duckdb.connect(duckfile, read_only=False) as conn:
        try:
            existing_relation = conn.sql(
                f"SELECT * FROM {todo_table} WHERE id={todo_id}"
            )
            existing = existing_relation.fetchone()
            logger.info(f"Existing: {existing}")
            df = pd.DataFrame(
                {
                    "id": todo_id,
                    "name": name if name is not None else existing[1],
                    "description": description
                    if description is not None
                    else existing[2],
                    "deadline": deadline if deadline is not None else existing[3],
                    "status": status if status is not None else existing[4],
                },
                index=[0],
            )
            logger.info(type(df.deadline[0]))
            if isinstance(df.deadline[0], date):
                df.loc[0, "deadline"] = datetime.combine(df.deadline[0], time.min)
            conn.register("df", df)
            
            query = f"UPDATE {todo_table} SET name = '{df.name[0]}', description = '{df.description[0]}', deadline = '{df.deadline[0].isoformat()}', status = '{df.status[0]}' WHERE id = {df.id[0]};"
            conn.execute(query)
            conn.commit()
        except duckdb.ConstraintException as e:
            logger.info(e)
            return Response("Task with such name already exists", 409)
        except Exception as e:
            return Response(e.args[0], 200)
    return Response(None, 200)


def create_db():
    with duckdb.connect(duckfile, read_only=False) as conn:
        try:
            conn.sql(f"SELECT 1 FROM {todo_table}")
        except duckdb.CatalogException as e:
            conn.sql(
                f"CREATE TABLE {todo_table} (id BIGINT PRIMARY KEY, name STRING NOT NULL, description STRING, deadline TIMESTAMPTZ NOT NULL, status STRING);"
            )
            conn.sql(f"CREATE UNIQUE INDEX name_deadline ON {todo_table} (name, deadline)")
            conn.sql("CREATE SEQUENCE IF NOT EXISTS todo_id START 1;")

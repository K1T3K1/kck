import pytermgui as ptg
from .cli import CLIView
from fastapi import FastAPI
from .todo_api import router
import uvicorn
import asyncio
from functools import partial
from multiprocessing import Process
import logging
import time
import queue
from logging.handlers import QueueHandler, QueueListener
import signal
import sys

que: queue.Queue = queue.Queue(-1)  # no limit on size
queue_handler = QueueHandler(que)
log_format = "%(levelname) -10s %(asctime)s %(name) -30s %(funcName) -35s %(lineno) -5d: %(message)s"
handler = logging.StreamHandler()
handler.setLevel(logging.WARN)
handler.setFormatter(logging.Formatter(log_format))
listener = QueueListener(que, handler)
logger = logging.getLogger()
logger.setLevel(logging.WARN)
logger.addHandler(handler)
listener.start()

logger = logging.getLogger(__name__)


def run_server(port):
    app = FastAPI()
    app.include_router(router)
    uvicorn.run(app, port=port, log_level=logging.CRITICAL)

def sigterm_handler(_signo, _stack_frame, server_process):
    server_process.terminate()
    server_process.join(1)
    server_process.close()
    sys.exit(0)

def main():
    CONFIG = """
    config:
        InputField:
            styles:
                prompt: dim italic
                cursor: '@72'
        Label:
            styles:
                value: dim bold
                color: black

        Window:
            styles:
                border: '15'
                corner: '60'

        Container:
            styles:
                border: '15'
                corner: '96'
        Button:
            styles:
                label: '@surface dim bold'
                highlight: '@surface+1 dim bold'
                prompt: '64'

    """

    api_port = 8000
    server_process = Process(target=run_server, args=[api_port], daemon=True)
    server_process.start()
    time.sleep(1)

    signal.signal(signal.SIGTERM, partial(sigterm_handler, server_process=server_process))
    signal.signal(signal.SIGINT, partial(sigterm_handler, server_process=server_process))


    with ptg.YamlLoader() as loader:
        loader.load(CONFIG)
    with ptg.WindowManager() as manager:
        manager.layout.add_slot("BodyLeft", width=0.33)
        manager.layout.add_slot("BodyMiddle", width=0.33)
        manager.layout.add_slot("BodyRight")
        cli_view = CLIView(manager, f"http://127.0.0.1:{api_port}")
        manager.run()
    server_process.terminate()
    server_process.join(1)
    server_process.close()

if __name__ == "__main__":
    main()
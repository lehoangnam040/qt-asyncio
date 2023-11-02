import asyncio
from collections.abc import Callable, Iterable, Mapping
import threading
import sys
import typing

import PySide2.QtCore
import PySide2.QtWidgets

from qtpy.QtCore import QCoreApplication, QObject, Qt, QThread, Signal, Slot
from qtpy.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QHBoxLayout, QLabel
import uvloop
from aiohttp import ClientSession


class MainApp(QMainWindow):

    def __init__(self, loop: asyncio.AbstractEventLoop) -> None:
        super().__init__(None)

        self.asyncio_loop = loop

        self.qwidget = QWidget()
        self.h_layout = QHBoxLayout(self.qwidget)

        self.button = QPushButton("Push here async")
        self.button.clicked.connect(self.on_clicked_button_async)
        self.button2 = QPushButton("Push here sync")
        self.button2.clicked.connect(self.on_clicked_button)
        self.label = QLabel("abcdef")
        self.h_layout.addWidget(self.label)
        self.h_layout.addWidget(self.button)
        self.h_layout.addWidget(self.button2)
        self.setCentralWidget(self.qwidget)

        self.count = 0

    @Slot()
    def on_clicked_button_async(self):

        asyncio.run
        future = asyncio.run_coroutine_threadsafe(self.call_api(), self.asyncio_loop)
        future.add_done_callback(
            lambda futu: self.label.setText(futu.result())
        )

    async def call_api(self) -> str:

        async def _sleep_random(i):
            for _ in range(i):
                print("---", i)
                await asyncio.sleep(i)

        await asyncio.gather(
            *[_sleep_random(i) for i in range(5)],
            loop=self.asyncio_loop,
        )
        print("finish gather")

        result = ""
        async with ClientSession() as session:
            async with session.get('http://python.org') as response:
                html = await response.text()
                result += str(response.status)
                result += response.headers['content-type']
                result += html[:15]
        print("finish call api")
        return result

    @Slot()
    def on_clicked_button(self):
        self.count += 1
        self.label.setText(f"Count is: {self.count}")


def start_qt_ui(loop: asyncio.AbstractEventLoop) -> None:
    QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
    app = QApplication(sys.argv)
    app.setOrganizationName("lehoangnam040")
    app.setApplicationName("App1")
    app.setApplicationVersion("0.0.1")

    window = MainApp(loop)
    window.setWindowTitle("App1")
    window.show()

    sys.exit(app.exec_())


class AsyncioThread(threading.Thread):

    def __init__(self, loop: asyncio.AbstractEventLoop) -> None:
        super().__init__(daemon=True)
        self.loop = loop

    def run(self) -> None:
        self.loop.run_forever()

if __name__ == "__main__":
    uvloop.install()
    loop = asyncio.new_event_loop()
    asyncio_thread = AsyncioThread(loop)
    asyncio_thread.start()

    start_qt_ui(loop)
import asyncio
import time

from PyQt5.QtCore import pyqtSignal, QThread
from PyQt5.QtWidgets import QApplication

from gui.toast.base_toast import QtBaseToast
from gui.theme.toast_theme import WarningToastTheme


class WorkerThread(QThread):
    finished_signal = pyqtSignal()

    def __init__(self):
        super().__init__()

    def run(self):
        do_something()
        self.finished_signal.emit()


def do_something():
    for i in range(3):
        time.sleep(1)
        print(i)


async def run():
    for i in range(100):
        print("______")
        base_toast = QtBaseToast(message=f"{i}...",
                                 duration=5,
                                 screen_center=app.desktop().screen().geometry().center(),
                                 theme=WarningToastTheme())
        base_toast.show()
        worker = WorkerThread()
        worker.finished_signal.connect(app.exit)

        worker.start()
        app.exec()


    # do_something()


if __name__ == '__main__':
    app = QApplication([])

    base_toast = QtBaseToast(message=f"Starting...",
                             duration=5,
                             screen_center=app.desktop().screen().geometry().center(),
                             theme=WarningToastTheme())
    base_toast.show()
    asyncio.run(run())
    app.exit()

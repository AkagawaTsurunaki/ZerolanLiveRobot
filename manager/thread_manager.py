import threading
from loguru import logger

class ThreadManager:
    def __init__(self):
        self._threads: dict[str, threading.Thread] = {}

    def add_thread(self, thread: threading.Thread):
        if self._threads.get(thread.name, None) is not None:
            raise RuntimeError("Duplicate thread name in ThreadManager.")
        self._threads[thread.name] = thread

    def start_all(self):
        for name, t in self._threads.items():
            t.start()
            logger.info(f"Thread {name} started.")

    def start_thread(self, thread: threading.Thread):
        self.add_thread(thread)
        thread.start()
        logger.info(f"Thread {thread.name} started.")

    def join_all_threads(self):
        for name, thread in self._threads.items():
            thread.join()
            logger.info(f"Thread {name} exited.")
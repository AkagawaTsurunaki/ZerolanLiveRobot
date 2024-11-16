import threading
from loguru import logger

class ThreadManager:
    def __init__(self):
        self._threads: dict[str, threading.Thread] = {}

    def start_thread(self, thread: threading.Thread):
        self._threads[thread.name] = thread
        thread.start()
        logger.info(f"Thread {thread.name} started.")

    def join_all_threads(self):
        for name, thread in self._threads.items():
            thread.join()
            logger.info(f"Thread {name} exited.")
"""
Modify from:
    http://www.s1nh.org/post/python-different-ways-to-kill-a-thread/
"""

import ctypes
import threading


class ThreadKilledError(BaseException):
    def __init__(self, *args):
        super().__init__(*args)


class ThreadCanNotBeKilledError(BaseException):
    def __init__(self, *args):
        super().__init__(*args)


class KillableThread(threading.Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs=None, *, daemon=None):
        super().__init__(group, target, name, args, kwargs, daemon=daemon)

    def get_id(self):
        """
        Get the id of the respective thread.
        Returns: Thread id.

        """
        # returns id of the respective thread
        if hasattr(self, '_thread_id'):
            return self._thread_id
        for id, thread in threading._active.items():
            if thread is self:
                return id

    def kill(self):
        """
        Kill the thread unsafely.
        Notes: This is an unsafe method the thread execution may be corrupted.
        Throws: ThreadCanNotBeKilledError if the thread is not killed successfully.
                ThreadKilledError if the thread is killed successfully.

        """
        thread_id = self.get_id()
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id,
                                                         ctypes.py_object(ThreadKilledError))
        if res > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)
            raise ThreadCanNotBeKilledError('Exception raise failure')

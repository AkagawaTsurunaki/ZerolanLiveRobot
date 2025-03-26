import asyncio
import time
from typing import Callable

from common.killable_thread import KillableThread
from event.eventemitter import emitter
from services.playground.bridge import PlaygroundBridge

pb = PlaygroundBridge(host="127.0.0.1", port=11000, password="123456")


def waituntil(predicate: Callable[[], bool]):
    while not predicate():
        time.sleep(0.1)


def test_conn():
    def run():
        asyncio.run(emitter.start())

    thread_emitter = KillableThread(target=run, daemon=True)
    thread_emitter.start()

    thread_pb = KillableThread(target=pb.start, daemon=True)
    thread_pb.start()

    waituntil(lambda: pb.is_connected)
    time.sleep(2)
    pb.play_speech(bot_id="Koneko", audio_path="tests/resources/tts-test.wav", transcript="我是赤川鹤鸣！",
                   bot_name="赤川小喵")

    thread_emitter.join()
    thread_pb.join()

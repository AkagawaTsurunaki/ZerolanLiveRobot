import asyncio
from asyncio import TaskGroup

import pytest
from zerolan.data.pipeline.asr import ASRStreamQuery

from common.concurrent.killable_thread import KillableThread
from event.event_data import DeviceMicrophoneVADEvent
from event.event_emitter import emitter
from event.registry import EventKeyRegistry
from manager.config_manager import get_config
from devices.microphone import SmartMicrophone
from pipeline.asr.asr_sync import ASRSyncPipeline


@pytest.fixture(scope="session")
def event_loop(event_loop_policy):
    # Needed to work with asyncpg
    loop = event_loop_policy.new_event_loop()
    yield loop
    loop.close()


_config = get_config()
mic = SmartMicrophone()
_asr = ASRSyncPipeline(_config.pipeline.asr)
t = KillableThread(target=mic.start, daemon=True)
_asr_res = []
tasks = []
_flag = True


@emitter.on(EventKeyRegistry.Device.MICROPHONE_VAD)
def _on_speech(event: DeviceMicrophoneVADEvent):
    query = ASRStreamQuery(
        is_final=True,
        audio_data=event.speech,
        media_type=event.audio_type.value,
        sample_rate=event.sample_rate,
        channels=event.channels,
    )
    for prediction in _asr.stream_predict(query):
        print(prediction.transcript)
        _asr_res.append(prediction)
    if len(_asr_res) > 3:
        global _flag
        _flag = False


@pytest.mark.asyncio
async def test_vad():
    t.start()
    async with TaskGroup() as tg:
        tg.create_task(emitter.start())
        while _flag:
            await asyncio.sleep(0.1)
        t.kill()
        await emitter.stop()

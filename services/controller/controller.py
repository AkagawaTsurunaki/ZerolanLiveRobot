from injector import inject

from event.event_data import SwitchVADEvent
from event.eventemitter import emitter
from event.speech_emitter import SpeechEmitter


class ZerolanController:

    @inject
    def __init__(self, vad: SpeechEmitter):
        self._vad = vad

    def switch_microphone(self):
        emitter.emit(SwitchVADEvent())

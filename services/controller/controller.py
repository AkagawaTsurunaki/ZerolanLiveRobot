from injector import inject

from event.event_data import CloseMicrophoneEvent, OpenMicrophoneEvent
from event.eventemitter import emitter
from event.speech_emitter import SpeechEmitter


class ZerolanController:

    @inject
    def __init__(self, vad: SpeechEmitter):
        self._vad = vad

    def switch_microphone(self):
        if not self._vad.is_recording:
            emitter.emit(OpenMicrophoneEvent())
        else:
            emitter.emit(CloseMicrophoneEvent())

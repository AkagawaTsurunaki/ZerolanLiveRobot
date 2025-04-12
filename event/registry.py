class EventKeyRegistry:
    """
    All event names should be registered here.
    """

    class Dev:
        TEST = "test"

    class System:
        CONFIG_FILE_MODIFIED = "system.config_file_modified"
        LANG_CHANGE = "lang_change"
        SYSTEM_UNHANDLED_ERROR = "system.error"
        SYSTEM_CRASHED = "system.crashed"

    class Pipeline:
        ASR = "pipeline.asr"
        LLM = "pipeline.llm"
        TTS = "pipeline.tts"
        IMG_CAP = "pipeline.img_cap"
        OCR = "pipeline.ocr"

    class Device:
        SCREEN_CAPTURED = "device.screen_captured"
        MICROPHONE_VAD = "service.vad.speech_chunk"
        MICROPHONE_SWITCH = "switch_vad"

    class LiveStream:
        CONNECTED = "service.live_stream.connected"
        DISCONNECTED = "service.live_stream.disconnected"
        SUPER_CHAT = "service.live_stream.super_chat"
        DANMAKU = "service.live_stream.danmaku"
        GIFT = "service.live_stream.gift"

    class Koneko:
        # Send from client and should be handled by server.
        class Client:
            HELLO = "koneko.client.hello"
            PUSH_INSTRUCTIONS = "koneko.client.push_instructions"

        class Server:
            HELLO = "koneko.server.hello"
            FETCH_INSTRUCTIONS = "koneko.server.fetch_instructions"
            CALL_INSTRUCTION = "koneko.server.call_instruction"

    class QQBot:
        QQ_MESSAGE = "qq.message"

    class Playground:
        DISCONNECTED = "playground/disconnected"
        CONNECTED = "playground_connected"

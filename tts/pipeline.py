class TTSQuery:
    text: str
    text_language: str
    refer_wav_path: str
    prompt_text: str
    prompt_language: str


class TTSPipeline:
    def __init__(self):
        self.model_id = ...

    def predict_with_prompt(self, tts_query: TTSQuery):
        ...

    def predict(self, tts_query: TTSQuery):
        ...

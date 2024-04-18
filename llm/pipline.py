class LLMPipeline:

    def __init__(self, model: str):
        self.model_list = ['chatglm3', '01-ai/Yi']
        assert model in self.model_list
        self.model = model

    @staticmethod
    def check_chatglm(text: str, history: list, temperature: float, top_p: float) -> bool:

        assert text and len(text) > 0

        if history and len(history) > 0:
            for chat in history:
                assert isinstance(chat, dict)
                assert chat.get('content', None)
                assert chat.get('metadata', None)
                role = chat.get('role', None)
                assert role
                assert role in ['user', 'assistant']

        assert 0.0 < top_p <= 1.0 and 0.0 < temperature <= 1.0

        return True

    @staticmethod
    def check_yi():
        ...

    def query(self, text: str, history: list, temperature: float = 1.0, top_p: float = 1.0):
        if self.model == self.model_list[0]:
            # Chat GLM 3

            # Validate param
            assert LLMPipeline.check_chatglm(text, history, temperature, top_p)

            # Return
            return {
                'query': text,
                'history': history,
                'top_p': top_p,
                'temperature': temperature
            }
        elif self.model == self.model_list[1]:
            ...

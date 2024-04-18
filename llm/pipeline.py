class LLMPipeline:

    def __init__(self, model: str):
        self.model_list = ['chatglm3', '01-ai/Yi', 'qwen']
        assert model in self.model_list, f'Unsupported model "{model}".'
        self.model = model

    @staticmethod
    def chatglm3(text: str,
                 history: list,
                 system_prompt: str = None,
                 temperature: float = 1.0,
                 top_p: float = 1.0) -> dict:

        # Validate param
        assert text and len(text) > 0

        if history and len(history) > 0:
            for chat in history:
                assert isinstance(chat, dict)
                content = chat.get('content', None)
                assert content and len(content) > 0
                assert chat.get('metadata', None)
                role = chat.get('role', None)
                assert role and role in ['user', 'assistant']

        assert 0.0 < top_p <= 1.0 and 0.0 < temperature <= 1.0

        # Convert to ChatGLM3 format
        return {
            'query': system_prompt + '\n' + text if system_prompt else text,
            'history': history,
            'top_p': top_p,
            'temperature': temperature
        }

    @staticmethod
    def yi(text: str,
           history: list) -> list:

        # Validate param
        assert text and len(text) > 0

        if history and len(history) > 0:
            for chat in history:
                assert isinstance(chat, dict)
                content = chat.get('content', None)
                assert content and len(content) > 0
                role = chat.get('role', None)
                assert role and role in ['user', 'assistant']

        # Convert to Yi format
        history += [{'role': 'user', 'content': text}]

        return history

    @staticmethod
    def qwen(text: str, history: list, system_prompt: str = None):

        # Validate param
        assert text and len(text) > 0

        if history and len(history) > 0:
            for chat in history:
                assert isinstance(chat, dict)
                content = chat.get('content', None)
                assert content and len(content) > 0
                role = chat.get('role', None)
                assert role and role in ['user', 'assistant', 'system']

        # Overwrite system prompt
        if history and len(history) > 0:
            if history[0]['role'] == 'system':
                history[0]['content'] = system_prompt

        # Convert to Qwen format
        history += [{'role': 'user', 'content': text}]

        return history

    def query(self,
              text: str,
              history: list,
              system_prompt: str = None,
              temperature: float = 1.0,
              top_p: float = 1.0) -> any:
        if self.model == self.model_list[0]:
            # ChatGLM3
            LLMPipeline.chatglm3(text, history, system_prompt, temperature, top_p)
        elif self.model == self.model_list[1]:
            # Yi
            LLMPipeline.yi(text, history)
        elif self.model == self.model_list[2]:
            # Qwen
            LLMPipeline.qwen(text, history, system_prompt)

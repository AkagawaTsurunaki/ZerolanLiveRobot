import os
import re
from typing import Tuple, List

from loguru import logger
from zerolan.data.data.prompt import TTSPrompt

from character.config import SpeechConfig
from common.enumerator import Language


def _get_all_files(prompts_dir: str):
    res = []
    for dirpath, _, filenames in os.walk(prompts_dir):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            res.append(os.path.abspath(filepath))
    return res


def parse_prompt(audio_path: str):
    audio_path = audio_path.replace("\\", "/")
    filename = audio_path.split("/")[-1]
    lang, sentiment, transcript = parse_tts_prompt_filename(filename)
    tts_prompt = TTSPrompt(audio_path=audio_path, lang=lang, sentiment=sentiment,
                           prompt_text=transcript)
    return tts_prompt


def parse_tts_prompt_filename(s: str) -> Tuple[str, str, str]:
    """
    For example:
        [zh][开心]大家好，我是绫地宁宁，大家一起 0721 吧！.wav
        [ja][羞恥]わ、わたしの...わたしのオナニーを見てください！.wav
        [en][anxiety] This is a detonator, you can't press it! .wav
    :param s: Filename
    :return: lang, sentiment, transcript
    """
    matches = re.findall(r'\[(.*?)\]', s)

    try:
        lang = Language.value_of(matches[0])
    except ValueError:
        raise ValueError(f'Invalid language tag in string "{s}"')
    except IndexError:
        raise ValueError(f"The language tag could not be found in the string: {s}")

    try:
        sentiment = matches[1]
    except ValueError:
        raise ValueError(f'Invalid sentiment tag in string "{s}"')
    except IndexError:
        raise ValueError(f"The language tag could not be found in the string: {s}")

    raw_filename = s.replace(f"[{lang}]", "").replace(f"[{sentiment}]", "")
    filetype = raw_filename.split(".")[-1]
    transcript = raw_filename[:-len(f".{filetype}")]

    return lang, sentiment, transcript


class TTSPromptManager:
    def __init__(self, config: SpeechConfig):
        self.default_tts_prompt: TTSPrompt | None = None
        self.tts_prompts: List[TTSPrompt] = []
        self.sentiments: List[str] = []
        self._lang = Language.ZH
        self._is_remote = config.is_remote
        if not self._is_remote:
            self._prompts_dir: str = config.prompts_dir
            self.load_tts_prompts()
        else:
            self._remote_files: List[str] = config.prompts

    def set_lang(self, lang: str):
        self._lang = lang
        self.load_tts_prompts()

    def get_tts_prompt(self, sentiment: str) -> TTSPrompt:
        for tts_prompt in self.tts_prompts:
            if tts_prompt.sentiment == sentiment:
                return tts_prompt
        return self.default_tts_prompt

    def load_tts_prompts(self):
        self.tts_prompts = []
        self.sentiments = []
        self.default_tts_prompt = None
        if self._is_remote:
            self._load(self._remote_files)
        else:
            self._load(_get_all_files(self._prompts_dir))

    def _load(self, audio_paths: List[str]):
        for audio_path in audio_paths:
            try:
                prompt = parse_prompt(audio_path)
                if prompt.lang != self._lang:
                    continue
                if not self._is_remote:
                    assert os.path.exists(audio_path), f"File not found: {audio_path}"
                    prompt.audio_path = os.path.abspath(audio_path)

                if prompt.sentiment == "Default":
                    self.default_tts_prompt = prompt
                self.tts_prompts.append(prompt)
                self.sentiments.append(prompt.sentiment)
            except ValueError:
                logger.warning(f"No suitable filename parsing strategy, the audio file will skip: {audio_path}")
                continue
        if len(self.tts_prompts) <= 0:
            if self._is_remote:
                raise Exception(f'You must provide remote path for TTS prompts in your config file.')
            raise Exception(f"There are no eligible TTS prompts in the directory you provided: {self._prompts_dir}")
        # Output sentiments result
        sentiments = [tts_prompt.sentiment for tts_prompt in self.tts_prompts]
        logger.info(f"{len(self.tts_prompts)} TTS prompts ({self._lang}) loaded: {sentiments}")

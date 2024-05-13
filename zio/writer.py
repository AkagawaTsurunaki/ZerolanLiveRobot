import os
import uuid


class Writer:
    def __init__(self, path: str):
        self.path: str = path
        self.encode: str = 'utf-8'

    def write_str(self, content: str):
        with open(file=self.path, mode='w+', encoding=self.encode) as f:
            f.write(content)

    def write_wav(self, data: bytes, filename: str | None = None) -> str:
        filename = uuid.uuid4() if filename is None else filename
        tmp_wav_file_path = os.path.join(self.path, f'{filename}.wav')
        tmp_wav_file_path = tmp_wav_file_path.replace("/", "\\")
        with open(file=tmp_wav_file_path, mode='wb') as wav_file:
            wav_file.write(data)
        return tmp_wav_file_path

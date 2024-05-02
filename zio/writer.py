import os
import uuid


class Writer:
    def __init__(self, path: str):
        self.path: str = path
        self.encode: str = 'utf-8'

    def write(self, content: str):
        with open(file=self.path, mode='w+', encoding=self.encode) as f:
            f.write(content)

    def write_wav(self, data) -> str:
        ran_file_name = uuid.uuid4()
        tmp_wav_file_path = os.path.join(self.path, f'{ran_file_name}.wav')
        with open(file=tmp_wav_file_path, mode='wb') as wav_file:
            wav_file.write(data)
        tmp_wav_file_path = tmp_wav_file_path.replace("/", "\\")
        return tmp_wav_file_path

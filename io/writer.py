class Writer:
    def __init__(self, path: str):
        self.path: str = path
        self.encode: str = 'utf-8'

    def write(self, content: str):
        with open(file=self.path, mode='w+', encoding=self.encode) as f:
            f.write(content)

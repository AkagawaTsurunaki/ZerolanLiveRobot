class LimitList(list):
    def __init__(self, maxsize: int):
        super().__init__()
        self.maxsize = maxsize

    def add(self, item):
        if len(self) < self.maxsize:
            super().append(item)
        else:
            super().pop(0)
            super().append(item)

    def __setitem__(self, index, value):
        if index >= len(self):
            raise IndexError("List assignment index out of range")
        super().__setitem__(index, value)

    def __delitem__(self, index):
        if index >= len(self):
            raise IndexError("List assignment index out of range")
        super().__delitem__(index)


    def insert(self, index, item):
        if index > len(self):
            raise IndexError("List assignment index out of range")
        if len(self) + 1 > self.maxsize:
            super().pop(0)
        super().insert(index, item)

    def extend(self, iterable):
        additional = len(iterable) + len(self) - self.maxsize
        if additional > 0:
            for _ in range(additional):
                super().pop(0)
        super().extend(iterable)

    def append(self, item):
        self.add(item)

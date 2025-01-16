def to_value_list(d: dict):
    if isinstance(d, dict):
        ret = []
        for k, v in d.items():
            ret.append(v)
        return ret
    else:
        raise TypeError("需要 dict 类型")

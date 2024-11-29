def clamp(_min, _max, value):
    """
    获取将 value 变为不小于 _min 同时不大于 _max 的值。
    Args:
        _min: 最小值
        _max: 最大值
        value: 要被变换的值

    Returns:
        区间上 [_min, _max] 的值
    """
    if value < _min:
        return _min
    elif value > _max:
        return _max
    else:
        return value

def is_blank(s: str):
    """
    判断字符串是否为空字符串
    :param s: 待判断的字符串
    :return: 如果字符串为空返回 True，否则返回 False
    """
    if s is None:
        return True
    if s == '':
        return True
    if "".isspace():
        return True
    return False


def is_valid_port(port):
    try:
        port = int(port)
        if 0 < port < 65536:
            return True
        else:
            return False
    except ValueError:
        return False


def url_join(host, port, protocol='http'):
    if not host or not port or not protocol:
        return None

    if protocol not in ['http']:
        return None

    url = f"{protocol}://{host}:{port}"
    return url

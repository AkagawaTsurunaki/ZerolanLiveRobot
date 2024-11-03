def urljoin(host: str, port: int, path: str = None):
    """
    根据协议、主机、端口号和路径，拼接 URL。
    Args:
        host: 主机，例如 127.0.0.1。
        port: 端口号，例如 11451。
        path: 路径，例如 /test/speak。

    Returns:

    """
    assert host and port
    assert isinstance(host, str) and isinstance(port, int)

    if ("http://" not in host) and ("https://" not in host):
        url = f"http://{host}:{port}"
    else:
        url = f"{host}:{port}"

    if path:
        assert isinstance(path, str)
        assert path[0] == '/', f'"path" should begin with "/".'
        url += path

    return url

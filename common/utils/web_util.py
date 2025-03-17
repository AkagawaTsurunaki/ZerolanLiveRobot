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


def is_valid_url(url: str | None) -> bool:
    protocol = url.split("://")[0]
    return protocol in ['http', 'https']


import netifaces as ni


def get_local_ip(ipv6=False) -> str | None:
    interfaces = ni.interfaces()  # 获取所有网络接口
    for interface in interfaces:
        if interface != "lo":  # 排除本地回环接口
            if ipv6:
                try:
                    # 尝试获取 IPv6 地址
                    ipv6_info = ni.ifaddresses(interface).get(ni.AF_INET6)
                    if ipv6_info:
                        # 返回第一个 IPv6 地址
                        ipv6_addr = ipv6_info[0]['addr']
                        # 去掉可能的接口标识符（如 %eth0）
                        ipv6_addr = ipv6_addr.split('%')[0]
                        return f"[{ipv6_addr}]"
                except KeyError:
                    pass
            else:
                try:
                    # 如果没有 IPv6 地址，尝试获取 IPv4 地址
                    ipv4_info = ni.ifaddresses(interface).get(ni.AF_INET)
                    if ipv4_info:
                        # 返回第一个 IPv4 地址
                        ipv4_addr = ipv4_info[0]['addr']
                        return ipv4_addr
                except KeyError:
                    continue
    return None
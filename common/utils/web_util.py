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

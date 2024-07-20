import re
import socket

import psutil

from spider import app


class InetUtils:
    def __init__(self):
        pass

    @classmethod
    def find_first_non_loopback_address(cls):
        ipv4 = None
        ipv6 = None
        net_if_addrs = psutil.net_if_addrs()
        for family, address in net_if_addrs.items():
            flag = False
            app.logger.info('获取ip family=【%s】', family)
            for addr in address:
                # fam, addr, mask, broadcast, ptp

                family = addr.family
                netmask = addr.netmask
                app.logger.info('获取ip netmask=【%s】 addr=【%s】', netmask, addr)
                if family == socket.AF_INET and re.match(
                        "^255.255.255.(?!0$)(25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])$", netmask):
                    ipv4 = addr.address
                    flag = True
                if flag and family == socket.AF_INET6:
                    ipv6 = addr.address
                    break
        if ipv4 is None:
            raise Exception('nacos 实例注册异常，未获取到有效 ipv4 地址')
        return ipv4, ipv6

# if __name__ == "__main__":
#     inet_utils = InetUtils()
#     ipv4, ipv6 = inet_utils.find_first_non_loopback_address()
#     print(ipv4, ipv6)

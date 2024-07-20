import ipaddress
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
        net_if_stats = psutil.net_if_stats()
        for family, address in net_if_addrs.items():
            if not cls.is_interface_running(family, net_if_stats) or cls.is_virtual_interface(family):
                # 如果网络接口不在运行，或是虚拟接口，跳过
                continue
            for addr in address:
                # fam, addr, mask, broadcast, ptp
                addr_family = addr.family
                netmask = addr.netmask
                ip = addr.address
                if addr_family != socket.AF_INET and addr_family != socket.AF_INET6:
                    continue
                if cls.is_valid_address(ip) is False:
                    continue
                app.logger.info('成功获取有效地址ip 网络名=【%s】 ip=【%s】 子网掩码=【%s】 全部信息=【%s】', family, ip,
                                netmask, addr)
                if ipv4 is None and addr_family == socket.AF_INET:
                    ipv4 = ip
                if ipv6 is None and addr_family == socket.AF_INET6:
                    ipv6 = ip
        if ipv4 is None:
            raise Exception('nacos 实例注册异常，未获取到有效 ipv4 地址')
        return ipv4, ipv6

    @classmethod
    def is_valid_address(cls, ip: str):
        """
        todo 此处获取ip的方法依然不完善
        如果是ipv4的话
        #&& !address.isLoopbackAddress()
		#&& isPreferredAddress(address)
        如果是ipv6的话
        # // filter ::1
        # && !inetAddress.isLoopbackAddress()   ok
        # // filter fe80::/10
        # && !inetAddress.isLinkLocalAddress()  ok
        # // filter ::/128
        # && !inetAddress.isAnyLocalAddress()
        # // filter fec0::/10,which was discarded, but some
        # // address may be deployed.
        # && !inetAddress.isSiteLocalAddress()  ok
        # // filter fd00::/8
        # && !isUniqueLocalAddress(inetAddress)
        # && isPreferredAddress(inetAddress)
        :param ip:
        :return:
        """
        if not cls.is_valid_ipv4(ip) and not cls.is_valid_ipv6(ip):
            return False
        ipv4_6 = ipaddress.ip_address(ip)
        if ipv4_6.is_loopback:
            return False
        if cls.is_valid_ipv6(ip):
            if ipv4_6.is_link_local or ipv4_6.is_site_local:
                return False
        return True

    @classmethod
    def is_valid_ipv4(cls, ip: str) -> bool:
        pattern = re.compile(r'^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$')
        return pattern.match(ip) is not None

    @classmethod
    def is_valid_ipv6(cls, ip: str) -> bool:
        pattern = re.compile(r'^(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|'
                             r'([0-9a-fA-F]{1,4}:){1,7}:|'
                             r'([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|'
                             r'([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|'
                             r'([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|'
                             r'([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|'
                             r'([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|'
                             r'[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|'
                             r':((:[0-9a-fA-F]{1,4}){1,7}|:)|'
                             r'fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|'
                             r'::(ffff(:0{1,4}){0,1}:){0,1}'
                             r'((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}'
                             r'(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|'
                             r'([0-9a-fA-F]{1,4}:){1,4}:'
                             r'((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}'
                             r'(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))$')
        return pattern.match(ip) is not None

    @classmethod
    def is_interface_running(cls, interface_name, net_if_stats=None):
        # 获取所有网络接口信息
        if net_if_stats is None:
            net_if_stats = psutil.net_if_stats()
        # 检查接口是否存在以及是否已启动并正在运行
        if interface_name in net_if_stats:
            return net_if_stats[interface_name].isup
        return False

    @classmethod
    def is_virtual_interface(cls, interface_name):
        # 简单检查接口名称是否符合常见虚拟接口的命名模式
        virtual_keywords = ['veth', 'br', 'docker', 'vmnet', 'virbr', 'tap', 'VMware']
        return any(interface_name.startswith(keyword) for keyword in virtual_keywords)

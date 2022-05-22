import re
import socket
import struct

import select


def listen():
    mc_port = 4445
    buffer_size = 2048
    mcast_grp = '224.0.2.60'
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    port_regex = re.compile(r"((?:\d+\.){1,8}\d+:?)?(\d+)")
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    req = struct.pack("4sl", socket.inet_aton(mcast_grp), socket.INADDR_ANY)
    s.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, req)
    s.bind(('', mc_port))
    s.setblocking(False)
    while True:
        read = select.select([s], [], [s], 2)[0]
        for r in read:
            msg, peer = r.recvfrom(buffer_size)
            address = peer[0]
            after = str(msg).split("[AD]")
            groups = port_regex.search(after[1])
            server_port = groups.group(2)
            server_data = re.sub(
                r'\[AD\].*\[/AD\]', "", "\n[Server: \"" + msg.decode("utf-8").replace("[MOTD]", "").replace(
                    "[/MOTD]", "\", ")) + "Address: \"" + address + ":" + str(server_port) + '"]'
            return server_port, server_data


if __name__ == '__main__':
    port, content = listen()
    print(content)

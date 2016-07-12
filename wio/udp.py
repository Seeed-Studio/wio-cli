# Send UDP broadcast packets
import socket
import re

PORT = 1025
IP = "192.168.4.1"
cmd = "SCAN"
addr = (IP, PORT)

def udp_list():
    s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    s.settimeout(3)
    ssid_list = []
    flag = False
    while 1:
        s.sendto('SCAN', addr)
        try:
            while 1:
                data, a = s.recvfrom(1024)
                ssid = data
                if ssid in '\r\n':
                    flag = True
                    break
                ssid = ssid.strip('\r\n')
                ssid_list.append(ssid)
        except socket.timeout:
            continue
        except:
            break

        if flag:
            break
    s.close()

    if flag:
        return ssid_list
    else:
        return None

def udp_version():
    s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    s.settimeout(3)
    version = 1.1
    flag = False
    while 1:
        s.sendto('VERSION', addr)
        try:
            while 1:
                data, a = s.recvfrom(1024)
                flag = True
                break
        except socket.timeout:
            continue
        except:
            break

        if flag:
            break
    s.close()

    if flag:
        try:
            version = float(re.match(r"([0-9]+.[0-9]+)", data).group(0))
        except Exception as e:
            version = 1.1
        return version
    else:
        return version
        
def send(cmd):
    s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    s.settimeout(3)
    flag = False
    while 1:
        try:
            s.sendto(cmd, addr)
            while 1:
                data, a = s.recvfrom(1024)
                if 'ok' in data:
                    flag = True
                    break
        except socket.timeout:
            continue
        except:
            break

        if flag:
            break
    s.close()

    return flag

# print udp_list()

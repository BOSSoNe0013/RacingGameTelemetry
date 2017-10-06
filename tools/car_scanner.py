import signal
import sys
import socket
import struct

from tools.debug import Debug

UDP_IP = "127.0.0.1"
UDP_PORT = 20777

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))


def main():
    index = 1
    value = None

    while True:
        data, address = sock.recvfrom(512)
        if not data:
            continue
        stats = struct.unpack('66f', data[0:264])
        new_value = "%.14f;%.14f;%d" % (stats[64], stats[63], int(stats[65]))
        if new_value != value:
            value = new_value
            print(index, value)
            index += 1


# noinspection PyUnusedLocal
def exit_gracefully(signum, frame):
    Debug.warn('Process killed (%s). Exiting gracefully' % signum)
    sock.close()
    sys.exit(0)


if __name__ == '__main__':
    signal.signal(signal.SIGINT, exit_gracefully)
    signal.signal(signal.SIGTERM, exit_gracefully)
    signal.signal(signal.SIGABRT, exit_gracefully)
    main()

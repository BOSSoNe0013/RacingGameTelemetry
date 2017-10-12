import signal
import socket
import struct
import sys

from datetime import datetime

from debug import Debug, LogLevel
from telemetry import Telemetry

UDP_IP = "127.0.0.1"
UDP_PORT = 20777

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))


def main():
    index = 1
    value = None
    last_update = datetime.now()
    found = False
    Debug.set_log_level(LogLevel(2))
    Debug.toggle(True)
    Debug.head("Car Scanner")
    Debug.log('Idle RPM | Max RPM | Max Gears')

    while True:
        if last_update is not None:
            delta = datetime.now() - last_update
            if delta.seconds >= 30:
                Debug.notice('New track')
                found = False
        last_update = datetime.now()
        data, address = sock.recvfrom(512)
        if not data:
            continue
        if found:
            continue
        stats = struct.unpack('66f', data[0:264])
        new_value = "%.14f;%.14f;%d" % \
                    (stats[Telemetry.IDLE_RPM], stats[Telemetry.MAX_RPM], int(stats[Telemetry.MAX_GEARS]))
        if new_value != value:
            value = new_value
            Debug.log(value, '%d' % index)
            index += 1
            found = True


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

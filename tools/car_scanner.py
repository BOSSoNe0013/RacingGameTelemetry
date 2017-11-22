import signal
import socket
import struct
import sys

from datetime import datetime
from threading import Thread

from tools.debug import Debug, LogLevel
from tools.games import Games
from tools.telemetry import Telemetry

UDP_IP = "127.0.0.1"
UDP_PORT = 20777


def main(game=Games.DIRT_RALLY, udp_host=UDP_IP, udp_port=UDP_PORT, callback=None):
    Debug.set_log_level(LogLevel(2))
    Debug.toggle(True)
    try:
        scan = Scan(game, udp_host, udp_port, callback)
        scan.start()
        return scan
    except Exception as e:
        Debug.err(e)


class Scan(Thread):
    def __init__(self, game=Games.DIRT_RALLY, udp_host=UDP_IP, udp_port=UDP_PORT, callback=None):
        Thread.__init__(self)
        Debug.set_log_level(LogLevel(2))
        Debug.toggle(True)
        self.finished = False
        self.callback = callback
        self.game = game
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(1)
        self.sock.bind((udp_host, udp_port))
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)
        signal.signal(signal.SIGABRT, self.exit_gracefully)

    def finish(self):
        self.finished = True
        Debug.notice('Stopping track scanner')
        if self.sock is not None:
            self.sock.close()

    # noinspection PyUnusedLocal
    def exit_gracefully(self, signum, frame):
        try:
            Debug.warn('Process killed (%s). Exiting gracefully' % signum)
            self.finish()
            sys.exit(0)
        except Exception as e:
            Debug.warn(e)

    def run(self):
        try:
            index = 1
            value = None
            last_update = datetime.now()
            found = False
            Debug.head("Car Scanner")
            Debug.log('ID | Idle RPM | Max RPM | Max Gears')
            if self.callback is not None:
                self.callback("Car Scanner")
                self.callback('ID | Idle RPM | Max RPM | Max Gears')

            while not self.finished:
                if last_update is not None:
                    delta = datetime.now() - last_update
                    if delta.seconds >= 30:
                        Debug.notice('New track')
                        found = False
                last_update = datetime.now()
                try:
                    data, address = self.sock.recvfrom(512)
                except socket.timeout:
                    continue
                except socket.error:
                    break
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
                    if self.callback is not None:
                        self.callback('%d;%s' % (index, value))
                    index += 1
                    found = True
        except Exception as e:
            Debug.warn(e)


if __name__ == '__main__':
    main()

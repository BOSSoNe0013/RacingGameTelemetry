import signal
import socket
import struct
import sys
import os
import sqlite3

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
            if self.game['db_file'] is None:
                return
            app_root = os.path.dirname(os.path.realpath(__file__))
            data_path = '/../data/'
            if getattr(sys, 'frozen', False):
                data_path = '/data/'
            conn = sqlite3.connect(app_root + data_path + self.game['db_file'])
            db = conn.cursor()

            index = 1
            value = None
            last_update = datetime.now()
            found = False
            Debug.head("Track Scanner")
            Debug.log('ID | Name | Track Length | Z POS | Laps')
            if self.callback is not None:
                self.callback("Track Scanner")
                self.callback('ID | Name | Track Length | Z POS | Laps')

            while not self.finished:
                if last_update is not None:
                    delta = datetime.now() - last_update
                    if delta.seconds >= 10:
                        found = False
                last_update = datetime.now()
                try:
                    data, address = self.sock.recvfrom(512)
                except socket.timeout:
                    continue
                except socket.error:
                    break
                if not data:
                    print('no data')
                    continue
                if found:
                    print('found')
                    continue
                stats = struct.unpack('66f', data[0:264])
                new_value = "%.14f;%d;%d" % \
                            (
                                stats[Telemetry.TRACK_LENGTH],
                                int(stats[Telemetry.Z_POSITION]),
                                int(stats[Telemetry.TOTAL_LAPS])
                            )
                if new_value != value:
                    value = new_value
                    index += 1
                    db.execute(
                        'SELECT id,name FROM Tracks WHERE length = ? AND (start_z = "" OR round(start_z) = ?)',
                        (stats[Telemetry.TRACK_LENGTH], stats[Telemetry.Z_POSITION]))
                    res = db.fetchall()
                    track_name = 'unknown'
                    track_index = -1
                    if len(res) >= 1:
                        for (index, name) in res:
                            track_index = index
                            track_name = name
                            break
                    Debug.log('%d;%s;%s' % (track_index, track_name, value))
                    if self.callback is not None:
                        self.callback('%d;%s;%s' % (track_index, track_name, value))
                    found = True
            Debug.notice('Scan loop ended')
            if db is not None:
                db.close()
            if conn is not None:
                conn.close()
        except sqlite3.Error as e:
            Debug.err("Database connection error")
            Debug.err(e)
        except Exception as e:
            Debug.warn(e)


if __name__ == '__main__':
    main()

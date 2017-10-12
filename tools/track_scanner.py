import signal
import socket
import struct
import sys
import os
import sqlite3

from datetime import datetime

from debug import Debug, LogLevel
from games import Games
from telemetry import Telemetry

UDP_IP = "127.0.0.1"
UDP_PORT = 20777

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

game = Games.DIRT_RALLY
db = None


def main():
    global db
    index = 1
    value = None
    last_update = datetime.now()
    found = False
    Debug.set_log_level(LogLevel(2))
    Debug.toggle(True)
    Debug.head("Track Scanner")
    Debug.log('ID | Name | Track Length | Z POS | Laps')
    try:
        app_root = os.path.dirname(os.path.realpath(__file__))
        conn = sqlite3.connect(app_root + '/../data/' + game['db_file'])
        db = conn.cursor()
    except sqlite3.Error as e:
        Debug.err("Database connection error")
        Debug.err(e)
        return

    while True:
        if last_update is not None:
            delta = datetime.now() - last_update
            if delta.seconds >= 10:
                found = False
        last_update = datetime.now()
        data, address = sock.recvfrom(512)
        if not data:
            continue
        if found:
            continue
        stats = struct.unpack('66f', data[0:264])
        new_value = "%.14f;%d;%d" % \
                    (stats[Telemetry.TRACK_LENGTH], int(stats[Telemetry.Z_POSITION]), int(stats[Telemetry.TOTAL_LAPS]))
        if new_value != value:
            value = new_value
            index += 1
            db.execute('SELECT id,name FROM Tracks WHERE length = ? AND (start_z = "" OR round(start_z) = ?)',
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
            found = True


# noinspection PyUnusedLocal
def exit_gracefully(signum, frame):
    Debug.warn('Process killed (%s). Exiting gracefully' % signum)
    sock.close()
    if db is not None:
        db.close()
    sys.exit(0)


if __name__ == '__main__':
    signal.signal(signal.SIGINT, exit_gracefully)
    signal.signal(signal.SIGTERM, exit_gracefully)
    signal.signal(signal.SIGABRT, exit_gracefully)
    main()

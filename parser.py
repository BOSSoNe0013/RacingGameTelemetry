import socket
import struct
import asyncore
import os
import threading
import sqlite3
from datetime import datetime
from telemetry import Telemetry
from tools.debug import Debug

UDP_IP = "127.0.0.1"
UDP_PORT = 20777


class Parser(asyncore.dispatcher):
    def __init__(self, listener, game):
        asyncore.dispatcher.__init__(self)
        self.game = game
        self.listener = listener
        self.max_speed = 0
        self.address = (UDP_IP, UDP_PORT)
        self.car = None
        self.previous_car = None
        self.previous_track = None
        self.track = None
        self.last_update = None

    @staticmethod
    def convert_time(time_s):
        time_ms = int(time_s * 1000)
        return int(time_ms / 60000), int((time_ms % 60000) / 1000), int((time_ms % 6000) % 1000)

    def open_socket(self):
        if self.socket and self.connected:
            return
        self.create_socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.bind(self.address)
        thread = threading.Thread(target=asyncore.loop, kwargs={'timeout': 1})
        thread.start()
        if self.listener.connection_callback:
            self.listener.connection_callback(True)
        Debug.notice("Waiting for data on %s:%s" % self.address)

    def close_socket(self):
        self.close()
        if self.listener.connection_callback:
            self.listener.connection_callback(False)

    def handle_connect_event(self):
        Debug.notice('Connected')
        if self.listener.connection_callback:
            self.listener.connection_callback(True)

    def handle_read(self):
        data = self.recv(512)
        if not data or len(data) <= 256:
            return
        self.parse(data)

    def writable(self):
        return False

    def readable(self):
        return True

    def handle_expt(self):
        Debug.warn('An error occurred! Closing socket.')
        self.close_socket()

    def find_track(self, track_length, z_pos):
        # print('Find track', track_length, z_pos)
        # if self.game['db_file'] is None:
        #     return
        try:
            app_root = os.path.dirname(os.path.realpath(__file__))
            conn = sqlite3.connect(app_root + '/data/' + self.game['db_file'])
            db = conn.cursor()
        except sqlite3.Error as e:
            Debug.err("Database connection error {}" % e)
            return
        db.execute('SELECT id,name, start_z FROM Tracks WHERE abs(length - ?) <0.000000001', (track_length,))
        res = db.fetchall()
        if len(res) == 1:
            (index, name, start_z) = res[0]
            self.track = {
                'id': index,
                'name': name,
                'start_z': start_z
            }
        elif len(res) > 1:
            self.track = None
            for (index, name, start_z) in res:
                if abs(z_pos - start_z) < 50:
                    self.track = {
                        'id': index,
                        'name': name,
                        'start_z': start_z
                    }
                    break
        else:
            self.track = None

    def find_car(self, idle_rpm, max_rpm, gears):
        # print('Find car', max_rpm, start_rpm)
        # if self.game['db_file'] is None:
        #     return
        try:
            app_root = os.path.dirname(os.path.realpath(__file__))
            conn = sqlite3.connect(app_root + '/data/' + self.game['db_file'])
            db = conn.cursor()
        except sqlite3.Error as e:
            Debug.err("Database connection error {}" % e)
            return
        db.execute('SELECT id, name FROM cars WHERE idle_rpm = ? AND max_rpm = ? AND gears = ?',
                   (idle_rpm, max_rpm, gears))
        res = db.fetchall()
        if len(res) == 1:
            (index, name) = res[0]
            self.car = {
                'id': index,
                'name': name
            }
        elif len(res) > 1:
            self.car = None
            for (index, name) in res:
                if self.track['id'] >= 1000 and index >= 1000:
                    self.car = {
                        'id': index,
                        'name': name,
                    }
                    break
                if self.track['id'] < 1000 and index < 1000:
                    self.car = {
                        'id': index,
                        'name': name,
                    }
                    break
        else:
            if self.track['id'] <= 1000:
                self.car = None
            else:
                self.car = self.previous_car
        db.close()

    def parse(self, data):
        if self.last_update is not None:
            delta = datetime.now() - self.last_update
            if delta.seconds >= 30:
                self.previous_car = self.car
                self.previous_track = self.track
                self.car = None
                self.track = None
        self.last_update = datetime.now()
        stats = struct.unpack('66f', data[0:264])
        distance = stats[Telemetry.LAP_DISTANCE] / 1000
        speed = int(stats[Telemetry.SPEED_MPS] * Telemetry.MPS_KMH_RATE)
        if speed > self.max_speed:
            self.max_speed = speed
        gear = int(stats[Telemetry.GEAR])
        throttle = stats[Telemetry.THROTTLE]
        steer = stats[Telemetry.STEER]
        brake = stats[Telemetry.BRAKE]
        clutch = stats[Telemetry.CLUTCH]
        rpm = int(stats[Telemetry.ENGINE_RPM] * 10)
        track_length = stats[Telemetry.TRACK_LENGTH] / 1000
        race_time = self.convert_time(stats[Telemetry.RACE_TIME])
        max_rpm = int(stats[Telemetry.MAX_RPM] * 10)
        lap = int(stats[Telemetry.LAP])
        total_laps = int(stats[Telemetry.TOTAL_LAPS])
        lap_time = self.convert_time(stats[Telemetry.LAP_TIME])
        idle_rpm = int(stats[Telemetry.IDLE_RPM] * 10)
        max_gears = int(stats[Telemetry.MAX_GEARS])

        if stats[Telemetry.TIME] < 0.5:
            if self.track is None:
                self.find_track(stats[Telemetry.TRACK_LENGTH], stats[Telemetry.Z_POSITION])
            if self.car is None:
                self.find_car(stats[Telemetry.IDLE_RPM], stats[Telemetry.MAX_RPM], max_gears)

        output = {
            'time': race_time,
            'lap_time': lap_time,
            'distance': distance,
            'track_length': track_length,
            'lap': lap,
            'total_laps': total_laps,
            'gear': gear,
            'max_gears': max_gears,
            'throttle': throttle,
            'steer': steer,
            'brake': brake,
            'clutch': clutch,
            'speed': speed,
            'max_speed': self.max_speed,
            'rpm': rpm,
            'max_rpm': max_rpm,
            'idle_rpm': idle_rpm,
            'car': self.car,
            'track': self.track
        }

        self.console_output(output)
        if distance == track_length:
            self.track = None

        if self.listener.data_callback:
            self.listener.data_callback(output)

    @staticmethod
    def console_output(data):
        os.system('clear')
        Debug.log("Time: %d:%d:%d" % (data['time'][0], data['time'][1], data['time'][2]))
        Debug.log("Distance %.2f km" % data['distance'])
        Debug.log("Track length: %.2f km" % data['track_length'])
        Debug.log("Gear: ", data['gear'])
        Debug.log("Throttle: ", data['throttle'])
        Debug.log("Steer: ", data['steer'])
        Debug.log("Brake: ", data['brake'])
        Debug.log("Clutch: ", data['clutch'])
        Debug.log("Lap: ", data['lap'])
        Debug.log("Lap time: %d:%d:%d" % (data['lap_time'][0], data['lap_time'][1], data['lap_time'][2]))
        Debug.log("Total laps: ", data['total_laps'])
        Debug.log("Speed: %d km/h" % data['speed'])
        Debug.log("Max speed: %d km/h" % data['max_speed'])
        Debug.log("RPM: ", data['rpm'])
        Debug.log("Max RPM: ", data['max_rpm'])
        Debug.log("Car: ", data['car'])
        Debug.log("Track: ", data['track'])

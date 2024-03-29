import asyncore
import os
import socket
import sqlite3
import struct
import threading
from datetime import datetime

from .telemetry import Telemetry
from .games import Games
from .debug import Debug, LogLevel


class ParserListener:
    def __init__(self, data_callback=None, connection_callback=None):
        self.data_callback = data_callback
        self.connection_callback = connection_callback

    def data_received(self, data):
        if not self.data_callback:
            return
        self.data_callback(data)

    def connection_status_changed(self, status):
        if not self.connection_callback:
            return
        self.connection_callback(status)


class Parser(asyncore.dispatcher):
    UDP_IP = "127.0.0.1"
    UDP_PORT = 20777

    def __init__(self, listener, game, address=None, port=None):
        asyncore.dispatcher.__init__(self)
        self.game = game
        self.listener = listener
        self.max_speed = 0
        if address is not None:
            self.UDP_IP = address
        if port is not None:
            self.UDP_PORT = port
        self.address = (self.UDP_IP, self.UDP_PORT)
        self.car = None
        self.previous_car = None
        self.previous_track = None
        self.track = None
        self.last_update = None
        self.log_level = LogLevel.error
        self.thread = None

    @staticmethod
    def convert_time(time_s):
        time_ms = int(time_s * 1000)
        return int(time_ms / 60000), int((time_ms % 60000) / 1000), int((time_ms % 6000) % 1000)

    def enable_parser_debug(self, log_level=LogLevel.verbose):
        self.log_level = LogLevel(log_level)
        Debug.set_log_level(self.log_level)
        Debug.toggle(True)
        Debug.notice('Parser debug mode set to %s' % self.log_level.name)

    def open_socket(self):
        if self.socket and self.connected:
            return
        try:
            self.create_socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.bind(self.address)
            self.thread = threading.Thread(target=asyncore.loop, kwargs={'timeout': 1})
            self.thread.start()
            if self.listener.connection_callback:
                self.listener.connection_callback(True)
            Debug.notice("Waiting for data on %s:%s" % self.address)
        except Exception as e:
            Debug.warn(e)
            self.close_socket()

    def close_socket(self):
        if self.thread is not None:
            Debug.notice('Stopping parser thread')
            asyncore.dispatcher.close(self)
        self.close()
        if self.listener.connection_callback:
            self.listener.connection_callback(False)

    def handle_connect_event(self):
        Debug.notice('Connected')
        if self.listener.connection_callback:
            self.listener.connection_callback(True)

    def handle_read(self):
        data = self.recv(264)
        if not data or len(data) < 264:
            return
        self.parse(data)

    def writable(self):
        return False

    def readable(self):
        return True

    def handle_expt(self):
        Debug.warn('An error occurred! Closing socket.')
        self.close_socket()

    def find_track(self, track_id):
        # print('Find track', track_id)
        if self.game['db_file'] is None:
            return
        try:
            app_root = os.path.dirname(os.path.realpath(__file__))
            conn = sqlite3.connect(app_root + '/../data/' + self.game['db_file'])
            db = conn.cursor()
        except sqlite3.Error as e:
            Debug.err("Database connection error")
            Debug.err(e)
            return
        db.execute('SELECT id,name, start_z FROM Tracks WHERE id = ?', (track_id,))
        res = db.fetchall()
        if len(res) == 1:
            (index, name, start_z) = res[0]
            self.track = {
                'id': index,
                'name': name,
                'start_z': start_z
            }
        else:
            self.track = None
        db.close()
        conn.close()

    def find_track(self, track_length, z_pos):
        # print('Find track', track_length, z_pos)
        if self.game['db_file'] is None:
            return
        try:
            app_root = os.path.dirname(os.path.realpath(__file__))
            conn = sqlite3.connect(app_root + '/../data/' + self.game['db_file'])
            db = conn.cursor()
        except sqlite3.Error as e:
            Debug.err("Database connection error")
            Debug.err(e)
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
        db.close()
        conn.close()

    def find_car(self, idle_rpm, max_rpm, gears):
        # print('Find car', max_rpm, start_rpm)
        if self.game['db_file'] is None:
            return
        try:
            app_root = os.path.dirname(os.path.realpath(__file__))
            conn = sqlite3.connect(app_root + '/../data/' + self.game['db_file'])
            db = conn.cursor()
        except sqlite3.Error as e:
            Debug.err("Database connection error")
            Debug.err(e)
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
                if self.track is None:
                    self.car = {
                        'id': index,
                        'name': name,
                    }
                    break
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
        conn.close()

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
        if len(stats) > Telemetry.TRACK_ID:
            track_id = int(stats[Telemetry.TRACK_ID]) + 1
        else:
            track_id = None

        if stats[Telemetry.TIME] < 0.5:
            if self.track is None:
                if track_id is None:
                    self.find_track(stats[Telemetry.TRACK_LENGTH], stats[Telemetry.Z_POSITION])
                else:
                    self.find_track(track_id)
            if self.car is None:
                self.find_car(stats[Telemetry.IDLE_RPM], stats[Telemetry.MAX_RPM], max_gears)

        output = {
            'game': self.game,
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
            'track_id': track_id,
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
        Debug.log(data['game']['name'])
        Debug.log("%d:%d:%d" % (data['time'][0], data['time'][1], data['time'][2]), "Time")
        Debug.log("%.2f km" % data['distance'], "Distance")
        Debug.log("%.2f km" % data['track_length'], "Track length")
        gear = Parser.parse_gear(data['gear'], data['game'])
        Debug.log(gear, "Gear ")
        Debug.log(data['throttle'], "Throttle")
        Debug.log(data['steer'], "Steer")
        Debug.log(data['brake'], "Brake")
        Debug.log(data['clutch'], "Clutch")
        Debug.log(data['lap'], "Lap")
        Debug.log("%d:%d:%d" % (data['lap_time'][0], data['lap_time'][1], data['lap_time'][2]), "Lap time")
        Debug.log(data['total_laps'], "Total laps")
        Debug.log("%d km/h" % data['speed'], "Speed")
        Debug.log("%d km/h" % data['max_speed'], "Max speed")
        Debug.log(data['rpm'], "RPM")
        Debug.log(data['max_rpm'], "Max RPM")
        Debug.log(data['car'], "Car")
        Debug.log(data['track_id'], "Track ID")
        Debug.log(data['track'], "Track")

    @staticmethod
    def parse_gear(raw_gear, game):
        gear = "%d" % raw_gear
        if game in [Games.F1_2015, Games.F1_2016, Games.F1_2017, Games.F1_2018]:
            if raw_gear == 0:
                gear = "R"
            elif raw_gear == 1:
                gear = "N"
            else:
                gear = "%d" % (raw_gear - 1)
        elif game in [Games.DIRT_RALLY_2]:
            if raw_gear == -1:
                gear = "R"
            elif raw_gear == Telemetry.GEAR_NEUTRAL:
                gear = "N"
        else:
            if raw_gear == Telemetry.GEAR_NEUTRAL:
                gear = "N"
            elif raw_gear == Telemetry.GEAR_REVERSE:
                gear = "R"
        return gear

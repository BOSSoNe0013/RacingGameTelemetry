import threading
import serial
import time

from .debug import Debug, LogLevel

# R'16bRPM''8bRPM_MAX'S'16bSPEED'G'8bGEAR'
# Display values 8 bits
# LEDs 8 bits (R,G,Y,-)
#         output = {
#             'time': race_time,
#             'lap_time': lap_time,
#             'distance': distance,
#             'track_length': track_length,
#             'lap': lap,
#             'total_laps': total_laps,
#             'gear': gear,
#             'max_gears': max_gears,
#             'throttle': throttle,
#             'steer': steer,
#             'brake': brake,
#             'clutch': clutch,
#             'speed': speed,
#             'max_speed': self.max_speed,
#             'rpm': rpm,
#             'max_rpm': max_rpm,
#             'idle_rpm': idle_rpm,
#             'car': self.car,
#             'track': self.track
#         }

# seven_segments_char_table = {
#     '0': [0, 0, 1, 1, 1, 1, 1, 1],
#     '1': [0, 0, 0, 0, 0, 1, 1, 0],
#     '2': [0, 1, 0, 1, 1, 0, 1, 1],
#     '3': [0, 1, 0, 0, 1, 1, 1, 1],
#     '4': [0, 1, 1, 0, 0, 1, 1, 0],
#     '5': [0, 1, 1, 0, 1, 1, 0, 1],
#     '6': [0, 1, 1, 1, 1, 1, 0, 1],
#     '7': [0, 0, 0, 0, 0, 1, 1, 1],
#     '8': [0, 1, 1, 1, 1, 1, 1, 1],
#     '9': [0, 1, 1, 0, 1, 1, 1, 1]
# }

baudrates = {
    '300': 1,
    '1200': 2,
    '2400': 3,
    '4800': 4,
    '9600': 5,
    '14400': 6,
    '19200': 7,
    '28800': 8,
    '38400': 9,
    '57600': 10,
    '115200': 11,
    '230400': 12,
    '250000': 13,
    '1000000': 14,
    '2000000': 15,
    '200000': 16
}
start_data = {
    'time': [0, 0, 0],
    'lap_time': [0, 0, 0],
    'distance': 0,
    'track_length': 0,
    'lap': 0,
    'total_laps': 0,
    'gear': 0,
    'max_gears': 0,
    'throttle': 0,
    'steer': 0,
    'brake': 0,
    'clutch': 0,
    'speed': 0,
    'max_speed': 0,
    'rpm': 0,
    'max_rpm': 100,
    'idle_rpm': 0,
    'car': {
                'id': 0,
                'name': ""
            },
    'track': {
                'id': 0,
                'name': "",
                'start_z': 0
            }
}


class ArduiDash:
    def __init__(self):
        self.serial = serial.Serial()
        self.should_read = True
        self.log_level = LogLevel.error
        self.mode = 3
        self.previous_cmd = ''

    def enable_debug(self, log_level=LogLevel.verbose):
        self.log_level = LogLevel(log_level)
        Debug.set_log_level(self.log_level)
        Debug.toggle(True)
        Debug.notice('ArduiDash debug mode set to %s' % self.log_level.name)

    def start(self, port, baud_rate):
        self.stop()
        self.should_read = True
        self.serial.baudrate = baud_rate
        self.serial.port = port
        self.serial.timeout = 1
        self.serial.open()
        Debug.notice('ArduiDash baudrate mode set to %s (%s)' % (baudrates[str(baud_rate)], str(baud_rate)))
        # self.serial.write(baudrates[str(baud_rate)])
        thread = threading.Thread(target=self.read, args=())
        thread.start()

    def stop(self):
        self.should_read = False
        try:
            if self.serial.is_open:
                self.serial.close()
        except AttributeError:
            Debug.notice("Serial communication was not opened")

    def read(self):
        while self.should_read:
            try:
                if self.serial.is_open:
                    data = self.serial.readline()
                    for c in data:
                        cmd = int(c)
                        Debug.log(cmd, "TTY Read")
                        if cmd in [49, 50, 52]:
                            self.change_mode(cmd)
            except TypeError as e:
                Debug.warn(e)

    def change_mode(self, mode):
        self.mode = mode
        if mode == 49:
            self.print("SP  GR  ")
        elif mode == 50:
            self.print("LP  TL  ")
        elif mode == 524:
            self.print("LP  TIME")
        time.sleep(1)
        self.telemetry_out(start_data)

    def setup(self, intensity):
        cmd = "0"
        cmd += str(intensity)
        self.send(cmd.encode("utf-8"))

    def print(self, data):
        cmd = "2"
        cmd += data
        self.send(cmd.encode("utf-8"))

    def telemetry_out(self, data):
        if self.mode == 1:
            self.send_speed_and_gear(data)
        elif self.mode == 2:
            self.send_lap_data(data)
        elif self.mode == 4:
            self.send_lap_time(data)

    def send_lap_time(self, data):
        self.print("%02d:%02d:%02d" % (data['lap_time'][0], data['lap_time'][1], int(data['lap_time'][2]/10)))

    def send_lap_data(self, data):
        cmd = "4"
        lap = data['lap']
        total_laps = data['total_laps']
        if int(lap / 10) > 0:
            cmd += str(int(lap / 10))
            cmd += str(int(lap % 10))
        else:
            cmd += str(0)
            cmd += str(lap)
        if int(total_laps / 10) > 0:
            cmd += str(int(total_laps / 10))
            cmd += str(int(total_laps % 10))
        else:
            cmd += str(0)
            cmd += str(total_laps)
        p = 0
        if total_laps > 0:
            p = lap * 100 / total_laps
        i = 1
        while i < 9:
            r = p / i
            if r <= 10:
                cmd += "-"
            else:
                cmd += "G"
            i += 1
        self.send(cmd.encode("utf-8"))

    def send_speed_and_gear(self, data):
        cmd = "3"
        speed = data['speed']
        gear = str(data['gear'])
        if data['gear'] == 10:
            gear = 'R'
        cmd += gear
        i = 0
        while i < 5:
            cmd += "-"
            i += 1
        if int(speed / 100) > 0:
            cmd += str(int(speed / 100))
            cmd += str(int(speed % 100 / 10))
        else:
            cmd += "-"
            if int(speed % 100 / 10) > 0:
                cmd += str(int(speed % 100 / 10))
            else:
                cmd += "-"
        cmd += str(speed % 10)
        p = 0
        if data['max_rpm'] > 0:
            p = data['rpm'] * 100 / data['max_rpm']
        i = 1
        while i < 9:
            r = p / i
            if r <= 10:
                cmd += "-"
            else:
                cmd += "G"
            i += 1
        self.send(cmd.encode("utf-8"))

    def send_data(self, data):
        try:
            if self.serial.is_open:
                self.serial.write(0x03)
                self.serial.write(b'1')
                self.serial.write(data)
                self.serial.write(b'\n')
        except TypeError as e:
            Debug.warn(e)

    def send(self, cmd):
        try:
            if self.serial.is_open and cmd != self.previous_cmd:
                self.serial.write(0x03)
                Debug.log(cmd, "TTY Write")
                self.serial.write(cmd)
                self.serial.write(b'\n')
                self.previous_cmd = cmd
        except TypeError as e:
            Debug.warn(e)

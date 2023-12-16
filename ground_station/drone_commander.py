import time
import socket
from database import DRONE_TELEMETRY
from multiprocessing.managers import DictProxy

TELLO_IP = '192.168.10.1'
TELLO_COMMAND_PORT = 8889
TELLO_COMMAND_ADDRESS = (TELLO_IP, TELLO_COMMAND_PORT)

UDP_SOCKET = socket.socket(socket.AF_INET,    # Internet
                           socket.SOCK_DGRAM) # UDP


# Send a command to the drone via the UDP socket
def send_command_to_drone(command: str):
    if command in set(['takeoff', 'streamon']):
        send_command_to_drone('command')

    UDP_SOCKET.sendto(command.encode(), TELLO_COMMAND_ADDRESS)


# Receives telemetry data from the drone. Start it as a Process
def drone_telemetry_listener(db: DictProxy):
    TELLO_TELEMETRY_PORT = 8890
    telemetry_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    telemetry_socket.bind(('', TELLO_TELEMETRY_PORT))
    telemetry_socket.settimeout(2.0)

    try:
        while True:
            try:
                data, _ = telemetry_socket.recvfrom(1024)
                data_dictionary = {}
                for item in data.decode().split(';'):
                    if ':' in item:
                        k, v = item.split(':')
                        data_dictionary[k] = v
            except socket.timeout:
                data_dictionary = {}

            db[DRONE_TELEMETRY] = data_dictionary

    except KeyboardInterrupt:
        time.sleep(0.5)
        telemetry_socket.close()
        print('Drone Telemetry Listener stopped')

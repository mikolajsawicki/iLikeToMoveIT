from Packet import Packet
import Phone
from blender_interface import send_packets
from datetime import datetime
import os


SESSIONS_DIR = 'sessions'


def save_packets_to_file(packets):

    if not os.path.exists(SESSIONS_DIR):
        os.mkdir(SESSIONS_DIR)

    filename = 'session_' + datetime.now().strftime('%d_%m_%Y_%H:%M:%S') + '.txt'

    txt = ''

    for p in packets:
        txt += str(p) + '\n'

    with open(os.path.join(SESSIONS_DIR, filename), 'w') as file:
        file.write(txt)


def read_packets_from_file(filename):
    packets = []

    with open(filename, 'r') as file:
        lines = file.readlines()

    for line in lines:
        packet_raw = line.split(' ')

        quaternion = [float(q) for q in packet_raw[2:]]

        packets.append(Packet(packet_raw[1], quaternion, packet_raw[0]))


    print(str(len(packets)) + ' packets have been read.')

    return packets



class IMUSessionsManager:
    def __init__(self):
        self.phones: list[Phone] = list()

        self.imu_sessions: list[list[Packet]] = list()

    def add_session(self, session: list[Packet]):
        self.imu_sessions.append(session)

        # A session for each phone has been created. It's time to send the whole data to blender.
        if len(self.imu_sessions) == len(self.phones):

            packets = self.merge_sessions()

            send_packets(packets)

            save_packets_to_file(packets)

            self.imu_sessions.clear()

    def merge_sessions(self):
        
        # Shift the timestamp counters to 0
        for i in range(len(self.imu_sessions)):
            for j in range(1, len(self.imu_sessions[i])):
                self.imu_sessions[i][j].timestamp -= self.imu_sessions[i][0].timestamp

        packets_merged = sum(self.imu_sessions, [])

        packets_merged.sort(key=lambda packet: packet.timestamp)

        return packets_merged

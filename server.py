import pickle
import socket
import os

__author__ = 'christopherwildsmith'

CLIENT_CONNECTION_PORT = 5003
CLIENT_DATA_PORT = 5004
SERVER_CONNECTION_PORT = 6003
SERVER_DATA_PORT = 6004

class Server:

    def __init__(self):
        self.serverIpAddr = self.get_device_ip_address()
    
        self.connectionSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
        self.connectionSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.connectionSocket.bind(('', SERVER_CONNECTION_PORT))

        self.dataSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
        self.dataSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.dataSocket.bind((self.serverIpAddr, SERVER_DATA_PORT))

        print("Server IP Address: " + str(self.serverIpAddr))

    def get_device_ip_address(self):
        gw = os.popen("hostname -I").read().split()
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect((gw[0], 0))
        ipaddr = s.getsockname()[0]
        return ipaddr

    def receive_connection_request(self):
        # NOTE: This recvfrom function call is blocking - Can be set with parameters such as a timeout.
        data, ipAddr = self.connectionSocket.recvfrom(2048) 
        #print("Data Received: " + str(list(data)) + " from: " + str(ipAddr))
        nodeIpAddr, sTeamName = pickle.loads(data)
        self.send_connection_confirmation(nodeIpAddr)
        return nodeIpAddr, sTeamName

    def send_connection_confirmation(self, ipAddress):
        dataToSend = pickle.dumps([self.serverIpAddr, "Connection Confirmed"])
        addr = (str(ipAddress), CLIENT_CONNECTION_PORT)
        self.connectionSocket.sendto(dataToSend, addr)

    def receive_data(self):
        # NOTE: This recvfrom function call is blocking - Can be set with parameters such as a timeout.
        data, ip_addr = self.dataSocket.recvfrom(4096)
        #print("Data Received: ")# + str(list(data)) + " from: " + str(ip_addr))
        return data, ip_addr[0]

    def send_data(self, nodeIp, data):
        addr = (str(nodeIp), CLIENT_DATA_PORT)
        #print("Data Sent: " + str(list(data)))
        data = pickle.dumps(data)
        self.dataSocket.sendto(data, addr)

    def __del__(self):
        self.connectionSocket.close()
        self.dataSocket.close()

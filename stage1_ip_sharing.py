import socket
import time
import pandas as pd
from abstract_classes import AbstractClient
from logger import Logger


class Client(AbstractClient):
    ID = None

    def __init__(self, ID):
        self.ID = ID
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect_socket(self, server_ip, server_port):
        self._socket.connect((server_ip, server_port))


if __name__ == '__main__':
    HostIP = '172.21.169.241'
    ServerIP = '172.21.13.147'
    ServerPort = 10023

    logger = Logger('logs/ip_sharing.log')

    # Abro socket en el puerto default
    client = Client(ID='00209216')
    client.connect_socket(ServerIP, ServerPort)

    # Envio mis credenciales
    outgoing_msg = f'{client.ID}|{HostIP}'
    client.write_socket(outgoing_msg)
    logger.add(ServerIP, ServerPort, 'envio', outgoing_msg)

    # Espero respuesta bannerProfesor|OK
    acceptMsg = client.read_socket()
    logger.add(ServerIP, ServerPort, 'recepcion', acceptMsg)
    msgFields = acceptMsg.split('|')
    IDServidor = msgFields[0]
    status = msgFields[1]

    ips = []
    try:
        while True:
            outgoing_msg = f'{client.ID}|LIST'
            client.write_socket(outgoing_msg)
            logger.add(ServerIP, ServerPort, 'envio', outgoing_msg)

            listMsg = client.read_socket()
            logger.add(ServerIP, ServerPort, 'recepcion', listMsg)

            msgFields = listMsg.split('|')
            num = int(msgFields[1])
            ips = []
            for i in range(num):
                ips.append(msgFields[i+2])

            ips = pd.DataFrame(ips)
            ips.columns = ['IPs']
            ips.to_csv('files/ips.csv', index=False)
            time.sleep(10)

    except KeyboardInterrupt:
        outgoing_msg = f'{client.ID}|EXIT'
        client.write_socket(outgoing_msg)
        logger.add(ServerIP, ServerPort, 'envio', outgoing_msg)

        exitMsg = client.read_socket()
        logger.add(ServerIP, ServerPort, 'recepcion', exitMsg)
        client.close_socket()


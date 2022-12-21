import socket
import threading
import pandas as pd
import numpy as np
import time
from abstract_classes import AbstractClient, AbstractServer
from logger import Logger
from msgManager import MsgManager


class Server(AbstractServer):
    IDServer = None
    clients = []

    def __init__(self, IDServer, Port):
        self.IDServer = IDServer
        self.Port = Port
        self._bindsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._bind_and_listen()

    class ClientInServer(AbstractClient):
        IP = None
        Port = None

        def __init__(self, s, fromaddr):
            self._socket = s
            self.IP = fromaddr[0]
            self.Port = fromaddr[1]

    def accept_client(self) -> ClientInServer:
        s, fromaddr = self._accept_connection()
        return self.ClientInServer(s, fromaddr)

    def listen_connections(self):
        print('Listening Thread')
        while True:
            try:
                newClient = self.accept_client()
                serve_thread = threading.Thread(target=self.serve_connection, args=[newClient])
                serve_thread.start()
            except:
                self.close_socket()

    def serve_connection(self, newClient: ClientInServer):
        global MensajesMap, ServerPort, TotalMensajes
        print(f'Serving Connection: {newClient.IP}')
        try:
            connectionMsg = newClient.read_socket()
            logger.add(newClient.IP, ServerPort, 'recepcion', connectionMsg)
            IDCliente, status = connectionMsg.split('|')
            NumMensajes = len(MensajesMap)
            IDPartes_joined = '|'.join([str(x) for x in MensajesMap.keys()])
            partsMsg = f'{self.IDServer}|{NumMensajes}|{IDPartes_joined}'
            newClient.write_socket(partsMsg)
            logger.add(newClient.IP, ServerPort, 'envio', partsMsg)

            while True:
                requestMsg = newClient.read_socket()
                logger.add(newClient.IP, ServerPort, 'recepcion', requestMsg)
                if requestMsg.split('|')[1] == 'disconnect':
                    break
                IDCliente, Request, IDParte = requestMsg.split('|')
                Mensaje = MensajesMap[IDParte]
                responseMsg = f'{self.IDServer}|{IDParte}|{TotalMensajes}|{Mensaje}'
                newClient.write_socket(responseMsg)
                logger.add(newClient.IP, ServerPort, 'envio', responseMsg)
            newClient.close_socket()
            print(f'Messages Sent to {newClient.IP}')
            print(f'{newClient.IP} Disconnected')
        except:
            newClient.close_socket()
            print(f'{newClient.IP} Disconnected')


class Client(AbstractClient):
    IDClient = None

    def __init__(self, IDClient):
        self.IDClient = IDClient
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect_socket(self, ServerIP, ServerPort):
        self._socket.connect((ServerIP, ServerPort))

    def request_messages(self):
        global MensajesMap, ServerIP, ServerPort
        print('Request Thread')
        ips = np.array(pd.read_csv('./files/ips.csv')['IPs'])
        ips = ['172.21.184.98']
        for IP in ips:
            if IP == ServerIP:
                continue
            try:
                print(f'Connecting to IP {IP}')
                self.connect_socket(ServerIP=IP, ServerPort=ServerPort)
            except ConnectionRefusedError as e:
                print(e.strerror)
                continue

            try:
                print(f'Requesting from IP {IP}')
                statusMsg = f'{self.IDClient}|status'
                self.write_socket(statusMsg)
                logger.add(IP, ServerPort, 'envio', statusMsg)

                connectMsg = self.read_socket()
                logger.add(IP, ServerPort, 'recepcion', connectMsg)
                msgFields = connectMsg.split('|')
                IDServidor = msgFields[0]
                NumMensajes = int(msgFields[1])
                IDPartes = msgFields[2:]
                for IDParte in IDPartes:
                    if IDParte not in MensajesMap:
                        requestMsg = f'{self.IDClient}|Request|{IDParte}'
                        logger.add(IP, ServerPort, 'envio', requestMsg)
                        self.write_socket(requestMsg)

                        newPartMsg = self.read_socket()
                        logger.add(IP, ServerPort, 'recepcion', newPartMsg)
                        IDServer, IDParte, TotalMensajes, Mensaje = newPartMsg.split('|')
                        MensajesMap[IDParte] = Mensaje.rstrip()

                disconnectMsg = f'{self.IDClient}|disconnect'
                self.write_socket(disconnectMsg)
                logger.add(IP, ServerPort, 'envio', disconnectMsg)
                self.close_socket()
                print(f'Messages Received From: {IP}')
                MsgManager.save_messages(MensajesMap, './files/mensajes_parciales.csv')

            except:
                self.close_socket()
                continue


if __name__ == '__main__':
    TotalMensajes = int(pd.read_csv('./files/TotalMensajes.csv')['TotalMensajes'])

    ServerIP = '172.21.169.241'
    ServerPort = 20212
    server = Server(IDServer='00209216', Port=ServerPort)

    MensajesMap = MsgManager.load_messages('./files/mensajes_parciales.csv')

    logger = Logger('./logs/exchange.log')


    listening_thread = threading.Thread(target=server.listen_connections)
    listening_thread.start()

    # client = Client(IDClient='00209216')
    # while len(MensajesMap) < TotalMensajes:
    #     try:
    #         client.request_messages()
    #         time.sleep(10)
    #     except:
    #         exit(1)




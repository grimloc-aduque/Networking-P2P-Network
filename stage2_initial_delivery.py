import socket
import pandas as pd
from logger import Logger
from abstract_classes import AbstractClient, AbstractServer
from msgManager import MsgManager

class Server(AbstractServer):
    ID = None

    def __init__(self, ID, Port):
        self.ID = ID
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
        try:
            s, fromaddr = self._accept_connection()
            return self.ClientInServer(s, fromaddr)
        except:
            self.close_socket()
            exit(1)


if __name__ == '__main__':
    server = Server(ID='00209216', Port=10048)
    print('Waiting Connection')
    client = server.accept_client()

    logger = Logger('logs/initial_delivery.log')


    try:
        acceptMsg = client.read_socket()
        logger.add(client.IP, server.Port, 'recepcion', acceptMsg)
        fields = acceptMsg.split('|')
        IDCliente = fields[0]
        NumMensajes = int(fields[1])

        if IDCliente != '00205950':
            errorMsg = f'{server.ID}|ERROR'
            client.write_socket(errorMsg)
            logger.add(client.IP, server.Port, 'error', errorMsg)
            client.close_socket()
            server.close_socket()
            exit(1)

        MensajesMap = []
        okMsg = f'{server.ID}|OK'
        client.write_socket(okMsg)
        logger.add(client.IP, server.Port, 'envio', okMsg)
        for i in range(NumMensajes):
            fileMsg = client.read_socket()
            logger.add(client.IP, server.Port, 'recepcion', fileMsg)
            IDCliente, IDParte, TotalMensajes, Mensaje = fileMsg.split('|')
            MensajesMap.append([IDParte, Mensaje])

            confirmationMsg = f'{server.ID}|{IDParte}'
            client.write_socket(confirmationMsg)
            logger.add(client.IP, server.Port, 'envio', confirmationMsg)

        client.close_socket()
        server.close_socket()

        MsgManager.save_messages(MensajesMap, './files/mensajes_originales.csv')
        MsgManager.save_messages(MensajesMap, './files/mensajes_parciales.csv')

        file = open('./files/TotalMensajes.csv', 'w+')
        file.write(f'TotalMensajes\n{TotalMensajes}\n')
        file.close()

    except:
        client.close_socket()
        server.close_socket()

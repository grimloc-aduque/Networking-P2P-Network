from logger import Logger
from abstract_classes import AbstractClient
import socket
from msgManager import MsgManager


class Client(AbstractClient):
    ID = None
    MensajesMap = None

    def __init__(self, ID):
        self.ID = ID
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect_socket(self, server_ip, server_port):
        self._socket.connect((server_ip, server_port))


if __name__ == '__main__':
    ServerIP = '172.21.13.147'
    ServerPort = 10024
    logger = Logger('logs/validation.log')

    client = Client(ID='00209216')
    client.connect_socket(ServerIP, ServerPort)

    MensajesMap = MsgManager.load_messages('./files/mensajes_parciales.csv')
    TotalMensajes = len(MensajesMap)
    connectMsg = f'{client.ID}|{TotalMensajes}'
    logger.add(ServerIP, ServerPort, 'envio', connectMsg)
    client.write_socket(connectMsg)

    responseMsg = client.read_socket()
    logger.add(ServerIP, ServerPort, 'recepcion', responseMsg)
    IDServer, Status = responseMsg.split('|')
    if Status == 'ERROR':
        client.close_socket()
        exit(1)

    for IDParte in MensajesMap:
        IDParte = IDParte
        Mensaje = MensajesMap[IDParte]
        requestMsg = f'{client.ID}|{IDParte}|{TotalMensajes}|{Mensaje}'
        client.write_socket(requestMsg)
        logger.add(ServerIP, ServerPort, 'envio', requestMsg)

        responseMsg = client.read_socket()
        logger.add(ServerIP, ServerPort, 'recepcion', responseMsg)
        IDServer, Status = responseMsg.split('|')
        if Status == 'ERROR':
            print(f'Error en el ensaje {IDParte}')
            client.close_socket()
            exit(1)
    finalResponseMsg = client.read_socket()
    logger.add(ServerIP, ServerPort, 'recepcion', finalResponseMsg)
    IDServer, Status = finalResponseMsg.split('|')
    if Status != 'OK':
        print('Algo salio mal :(')
        client.close_socket()
        exit(1)
    else:
        print('Se logrooo')


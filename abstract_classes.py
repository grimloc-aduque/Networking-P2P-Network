import socket


class AbstractClient:
    _socket: socket.socket = None

    def read_socket(self) -> str:
        incoming_msg = None
        while incoming_msg is None:
            incoming_msg = self._socket.recv(1024)
        incoming_msg = incoming_msg.decode('ASCII')
        return incoming_msg

    def write_socket(self, msg: str):
        self._socket.sendall(msg.encode('ASCII'))

    def close_socket(self):
        self._socket.close()


class AbstractServer:
    _bindsocket = None
    Port = None

    def _bind_and_listen(self):
        self._bindsocket.bind(('', self.Port))
        self._bindsocket.listen()

    def _accept_connection(self):
        newsocket, fromaddr = self._bindsocket.accept()
        return newsocket, fromaddr

    def close_socket(self):
        self._bindsocket.close()

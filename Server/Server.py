import json
import socket
from threading import Thread

from color import Color
from log import LOG
from Encryption import Asymetric_Server as Asymetric
from Encryption import Symmetric_Server as Symmetric


class Server():

    def __init__(self, SOCKET):
        """
        Inits Server with the server socket
        Init all the external module too

        Args:
            SOCKET (socket): The server socket
        """        
        self.SOCKET = SOCKET 

        self.COLORDB = Color()
        # Database for color management
        self.LOG = LOG(self.COLORDB)
        # Object that takes care of displaying logs

        self.limit_user, self.nb_user = self.COLORDB.number_color(), 0 
        # user limit and Number of logged in users

        self.list_clients_sockets = set()
        # Set of connected sockets
        self.dico_client = {}
        # Dictionary with user information

    def main_loop(self):
        """
        Loop that turns until the server closes
        Main server organ.
        """
        while True:
            client_socket, client_address = self.SOCKET.accept()

            if self.nb_user < self.limit_user:
                # If there is room for a new user
                self.COLORDB.add_user(client_address)
                self.list_clients_sockets.add(client_socket)
                # addition to connect user and color database
                color_user = self.COLORDB.color_user_HEX(client_address)
                self.dico_client[client_socket] = {
                    "Addr": client_address,
                    "Pseudo": None,
                    "Color": color_user,
                    "cypher": None,}
                # We store the color in hexadecimal (base 16), and the client address in the dictionary
                self.LOG.connection_server(client_address)
                self.LOG.showing_client()
                self.nb_user += 1

                self.encryptions_begin(client_socket, client_address)
                # start a new thread for listening this client.
                # daemon Thread ( if the main loop finish, it kill )
                t = Thread(target=self.listen_client, args=(client_socket,))
                t.daemon = True
                t.start()

            else:
                self.COLORDB.temporary_user(client_address)
                # We add color for the user temporarily (for logs)
                color_user = self.COLORDB.color_user_HEX(client_address)
                self.dico_client[client_socket] = {
                    "Addr": client_address,
                    "Pseudo": None,
                    "Color": color_user,
                    "cypher":None,}
                # We store the color in hexadecimal (base 16), and the client address in the dictionary
                self.LOG.server_full(client_address)

                self.encryptions_begin(client_socket, client_address)

                command = self.json_generator_command("ServerFull", None)
                self.broadcast_to_client(command, [client_socket])
                # Sends the client that the server is full
                self.LOG.disconnection_server(client_address)

                del self.dico_client[client_socket]
                self.COLORDB.del_temporary_user(client_address)
                # Removing the user from memory (like database, dico and set)
                client_socket.close()
    
    def listen_client(self, client):
        """
        Function used to listen to customers.
        Start with a DAEMON Thread, each customer benefits from their own Thread
        to listen and return the data

        Args:
            client (socket): the socket to associate with client x
        """
        addr = self.dico_client[client]["Addr"]
        while True:
            try:
                data_encrypted = client.recv(1024)
                # We try to receive what the user sends us
            except:
                # if something goes wrong (like the client disconnect)
                try:
                    self.error_connection(client)
                    # We try to disconnect the client
                except:
                    pass
                break
                # free the resource from the while loop
            else:
                # If we managed to receive what the user sends us
                self.LOG.received_data(addr, data_encrypted)
                data = self.dico_client[client]["cypher"].decrypt(data_encrypted)
                # print(data)


                if self.is_message_command(data) == True:
                    # if the message is a command to be executed
                    answer_command, sending_answer = self.execute_command(
                        client, data)
                    if sending_answer == True:
                        # If a response is requested by the client
                        self.broadcast_to_client(answer_command, [client])
                else:
                    message = self.json_generator_message(client, data)
                    self.broadcast_to_client(message, self.list_clients_sockets)
                    # We send the message to all connected users on the list

    def execute_command(self, client, command):
        """
        Function that executes the command enter as argument
        Command written as {"command": command, "arg": arg}

        List_commands:
            command => "name" and arg => "[Name_enter_by_user]":
                Request from the client to associate a name with its socket
                If the name of the user is correct, we associate it with its socket,
                And we announce to the user already connected that the user has joined the server
                otherwise he is told to start over. We send the answer back to the client
                Return:
                    command => "name" ; arg => "good", if the user name is good
                    command => "name" ; arg => "bad", if the username is bad
            command => "quit" ; arg => None:
                The user warns that he is going to disconnect
                No need to answer
            
        Args:
            client (socket): the socket client who executed the order
            command (string(json serialized dictionary)): the command to execute

        Returns:
            str: if we need to answer something
            str: the answer to send back (if we have to do it)
        """        
        answer_command, sending_answer = None, None

        addr = self.dico_client[client]["Addr"]
        color = self.dico_client[client]["Color"]
        dico_command = json.loads(command)
        command, arg = dico_command["command"], dico_command["arg"]

        if command == "name":
            pseudo_valid = self.pseudo_verificator(arg)
            if pseudo_valid:
                self.dico_client[client]["Pseudo"] = arg
                answer_command = self.json_generator_command("name", "good")
                sending_answer = True

                arg = self.json_generator_arg_annonce(client, "connection")
                announcement = self.json_generator_command("announcement", arg)
                self.broadcast_to_client(announcement, self.list_clients_sockets)
                # new user announcement
            else:
                # The usernme is not good
                answer_command = self.json_generator_command("name", "bad")
                sending_answer = True
        if command == "quit":
            sending_answer = False
            self.error_connection(client)

        return answer_command, sending_answer
        
    def error_connection(self, client):
        """
        Function used to remove users from chat in case of error

        Args:
            client (socket): the client who has just disconnected
        """
        addr = self.dico_client[client]["Addr"]

        self.list_clients_sockets.remove(client)
        if len(self.list_clients_sockets) != 0:
            # If this is the last logged in user
            arg = self.json_generator_arg_annonce(client, "disconnection")
            announcement = self.json_generator_command("announcement", arg)
            self.broadcast_to_client(announcement, self.list_clients_sockets)
        del self.dico_client[client]
        client.close()

        self.LOG.disconnection_server(addr)
        self.COLORDB.del_user(addr)
        self.LOG.showing_client()
        self.nb_user -= 1
        # Removing the user from memory (like database, dico and set)

    def broadcast_to_client(self, data, liste_client):
        """
        Function that sends a message to all the customers enter in parameter

        Args:
            data (str): The message to send
            liste_client (list): list of all users who will receive the message
        """        
        for client_socket in liste_client:
            addr = self.dico_client[client_socket]["Addr"]
            data_encrypted = self.dico_client[client_socket]["cypher"].encrypt(data)
            client_socket.sendall(data_encrypted)
            self.LOG.send_data(addr, data_encrypted)
   
    def pseudo_verificator(self, pseudo_client):
        """
        Function that checks if the user's nickname is not already in use, it not "you"
        or if it is composed of ASCII characters - (/ \: *? "<> |)

        Args:
            pseudo_client (str): the client pseudo

        Returns:
            bool: if the pseudo is valid : True, else False
        """
        if pseudo_client == "you":
            return False
        if (pseudo_client.isascii() == False) or (
            any(c in '/\:*?"<>|' for c in pseudo_client) == True
        ):
            # if there are symbols not ascii or not compatible with window's filesystem
            return False
        else:
            liste_clients_s = list(self.list_clients_sockets)
            for socket in liste_clients_s:
                pseudo_use = self.dico_client[socket]["Pseudo"]
                if pseudo_client == pseudo_use:
                    return False
            return True

    def is_message_command(self, message):
        """
        Function that allows you to know if it is a command

        Args:
            message (string(json serialized dictionary)): the expression to evaluate

        Returns:
            bool: if or if not the message is a command
        """        
        dico = json.loads(message)
        return (dico["type"] == "command")

    def json_generator_command(self, command, arg):
        """
        Function that forms a command in a form understandable by the client
        like this : {"type": "command",
                    "command": command,
                    "arg": arg}

        Args:
            command (str): the name of the command
            arg (str): the arg of the command

        Returns:
            str (json serialized): the command in a good form
        """

        dico = {
            "type": "command",
            "command": command,
            "arg": arg,
        }
        return json.dumps(dico)

    def json_generator_message(self, client, message_user):
        """
        Function that forms a command in a form understandable by the client
        like this : {"type": "command",
                    "command": command,
                    "color": color,
                    "sender" : sender,}

        Args:
            client (socket) : the socket who send data in the first place
            message_user (string(json serialized)) : the message sent by the user {"type": "message", "message": message,}

        Returns:
            (string(json serialized)) => The message to be returned
        """
        dico = json.loads(message_user)
        message = dico["message"]
        color = self.dico_client[client]["Color"]
        sender = self.dico_client[client]["Pseudo"]

        dico = {
            "type": "message",
            "message": message,
            "color": color,
            "sender": sender,
        }
        return json.dumps(dico)

    def json_generator_arg_annonce(self, client, mode):
        """
        function that generates an understandable form of announcement for the client
        like this : {"type_annonce": mode,
                    "name": name,
                    "addr": addr,
                    "color": color,}

        Args:
            client (socket): the socket of the client
            mode (str): what type of announcement

        Returns:
            (string(json serialized)): the annoucement
        """

        addr = self.dico_client[client]["Addr"]
        color = self.dico_client[client]["Color"]
        name = self.dico_client[client]["Pseudo"]
        arg = {
            "type_annonce": mode,
            "name": name,
            "addr": addr,
            "color": color,
        }
        arg = json.dumps(arg)

        return arg

    def encryptions_begin(self, client, addr):
        public_key_pem = client.recv(1024)  
        rsa_public = Asymetric.rsa_server(public_key_pem)
        self.LOG.rsa_public(addr)

        cypher_user = Symmetric.cypher()
        symmetric_key = cypher_user.get_key()

        rsa_encrypted_symmetric_key = rsa_public.encrypt(symmetric_key)
        client.sendall(rsa_encrypted_symmetric_key)
        self.dico_client[client]["cypher"] = cypher_user
        self.LOG.generation_symmetric_key(addr, symmetric_key)


if __name__ == "__main__":

    # Edit this
    SERVER_HOST = "127.0.0.1"   # Standard loopback interface address (localhost) 
    SERVER_PORT = 65432         # Port to listen on (non-privileged ports are > 1023)

    # create a TCP socket, make the port reusable and bind it with the socket
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((SERVER_HOST, SERVER_PORT))
    s.listen(5)

    Server_Tchat = Server(s)
    Server_Tchat.main_loop()


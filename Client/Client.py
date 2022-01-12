import json
import socket
import sys
from threading import Thread
from tkinter import *

from gui import Applications
from Encryption import Asymetric_Client as Asymetric
from Encryption import Symmetric_Client as Symmetric

class user:

    def __init__(self, fenetre):
        """Initialization of the class that manages users

        Args:
            fen (tk.Frame)): The frame where the window will be displayed
        """
        self.rsa_c = Asymetric.rsa_client()

        self.pseudo_valide = False
        # Variable used to know if messages can be sent
        self.pseudo = "ANON"
        # Ansi to reset the color
        self.RESET = "\033[m"

        self.fenetre = fenetre
        self.fenetre.protocol("WM_DELETE_WINDOW", self.deconnection_gui)
        # Closing the window
        self.gui = Applications(self.fenetre)
        self.gui.config_call_function(
            self.init_connnection_gui, self.choose_pseudo_gui, self.send_message_gui
        )
        self.gui.show_addr()

    def init_connnection_gui(self):
        """
        Function which allows to check if the address of the server is the right one
        Activation by the button "Join Server" of the GUI
        """
        host, port = self.gui.return_addr()
        server_valide = self.host_port_valide(host, port)

        if server_valide == True:
            self.encryptions_begin()
            self.start_listening()
            self.gui.hide_addr()
            self.gui.show_pseudo()
        else:
            self.gui.error_server()

    def choose_pseudo_gui(self):
        """
        Function that allows the user to enter his nickname
        Activation by the "Confirm" button of the GUI
        Allows you to ask the server if its nickname is valid
        """
        self.pseudo = self.gui.return_pseudo()
        if len(self.pseudo) != 0 and self.pseudo.isspace != True:
            pseudo = self.json_generator_command("name", self.pseudo)
            pseudo_encrypt = self.Symmetric_cypher.encrypt(pseudo)
            self.send_message(pseudo_encrypt)

    def send_message_gui(self):
        """
        Function that allows the user to send messages written in the field provided for this purpose
        Activation by the "Send" button of the GUI
        """
        message = self.gui.return_message()
        if len(message) != 0 and message.isspace != True:
            message = self.json_generator_message(message)
            message_encrypt = self.Symmetric_cypher.encrypt(message)
            self.send_message(message_encrypt)

    def deconnection_gui(self):
        """
        Call function when closing the window
        """
        message = self.json_generator_command("quit", None)
        try:
            message_byte = message.encode()
            self.send_message(message)
            self.s.close()
        except:
            pass
        self.fenetre.destroy()

    def show_message_gui(self, color, sender, message):
        """
        Function that allows you to display messages on the gui

        Args:
            color (string): the color ( in hexadecimal format #xxxxx)
            sender (string): the user who send the message
            message (string): the message in itself
        """
        self.gui.add_to_tchat(color, sender, message)

    def show_annonce_gui(self, name, addr, mode):
        """
        Function that allows you to display announcements on the gui

        Args:
            name (string): the name of the trigger
            addr (tuple): the ip+port of the trigger
            mode (string): the mode of the annoucement
        """
        self.gui.afficher_annonce(name, addr, mode)

    def host_port_valide(self, host, port):
        """
        Function that allows you to know if the server address is correct
        If the address is correct, we connect and start listening

        Args:
            host (string): The server address (xxx.xxx.xxx.xxx)
            port (string): the server port (0-9999, non-privileged ports are > 1023)

        Returns:
            bool: The adress is valid True or False ?
        """
        try:
            # try to create a socket
            # initialize TCP socket
            # connect to the server
            self.s = socket.socket()
            self.s.connect((host, int(port)))
        except Exception as e:
            # if an error appears
            print(e)
            return False
        else:
            # if the execution goes well
            
            # Start listening to incoming messages
            return True

    def start_listening(self):
        """
        Function that make a thread that listens for messages to this client
        make the thread daemon so it ends whenever the main thread ends
        """
        t = Thread(target=self.listen_for_messages)
        t.daemon = True
        t.start()

    def listen_for_messages(self):
        """
        Function to receive data and act accordingly
        (Start with Thread)
        """
        while True:
            try:
                data_rec = self.s.recv(1024)
            except:
                self.deconnection_gui()
                break
            else:
                data_rec = self.Symmetric_cypher.decrypt(data_rec)
                if self.is_message_command(data_rec):
                    self.execute_command(data_rec)
                else:
                    if self.pseudo_valide:
                        self.afficher_message_cls(data_rec)

    def execute_command(self, command):
        """
        Function that executes the command enter as argument
        Command written as {"command": command, "arg": arg}

        List_commands:
            command => "name":
                arg => "good":
                    The name the user chose is correct
                    We update the GUI client
                arg => "bad":
                    The nickname entered is not good
            command => "announcement" ; arg => None:
                Announcement from the server
            command => "ServerFulle" ; Arg => None:
                Announces that the server is full, and that the user cannot connect
        Args:
            command (string(json serialized dictionary)): the command to execute
        """
        dico_command = json.loads(command)
        command, arg = dico_command["command"], dico_command["arg"]

        if command == "name":
            if arg == "good":
                self.pseudo_valide = True  # autorisation d'envoyer des messages
                self.gui.update_name(self.pseudo)
                self.gui.hide_pseudo()
                self.gui.show_message()
            elif arg == "bad":
                self.gui.error_pseudo()
        if command == "announcement":
            self.afficher_annonce_cls(arg)
        if command == "ServerFull":
            self.s.close()
            self.gui.error_serverfull()
            self.gui.show_addr()

    def send_message(self, data):
        """Function that send the data to the server

        Args:
            data (byte): the data to send
        """
        self.s.sendall(data)

    def afficher_annonce_cls(self, arg):
        """
        Function that show the annoucement in cls
        arg = {
                "type_annonce":mode,
                "name":name,
                "addr":addr,
                "color":color,
        }

        Args:
            arg (string(json serialized)): The different info to display the announcement
        """
        dico_message = json.loads(arg)

        mode = dico_message["type_annonce"]
        name = dico_message["name"]
        addr = dico_message["addr"]
        color = dico_message["color"]
        color = self.hex_to_ansi(color)

        self.show_annonce_gui(name, addr, mode)

        if mode == "connection":
            print(
                f"{self.RESET} New user on the tchat : {color}{addr}{self.RESET} under the following nickname {color}{name}{self.RESET}"
            )
        elif mode == "disconnection":
            print(
                f"{self.RESET} User {color}{addr}{self.RESET} under the following nickname {color}{name}{self.RESET} has disconnected"
            )

    def afficher_message_cls(self, message):
        """
        Function that show the message in cls
        {
            "message", message
            "color", color
            "sender", sender,
        }

        Args:
            message ((string(json serialized))): The different info to display the message
        """
        dico_message = json.loads(message)
        message = dico_message["message"]
        color_hex = dico_message["color"]
        color_ansi = self.hex_to_ansi(color_hex)
        sender = dico_message["sender"]
        if sender == self.pseudo:
            sender = "you"
        LETTER_MAX, count = 80, 1

        if len(message) > LETTER_MAX:
            message2 = ""
            count = 1
            if len(message) > 3:
                for letter in message:
                    message2 += letter
                    if count % LETTER_MAX == 0 and len(message) != count:
                        message2 += "\n" + (len(sender) + 3) * " "
                    count += 1
            message = message2
        print(f"{color_ansi}{sender} > {message}{self.RESET}")
        self.show_message_gui(color_hex, sender, message)

    def is_message_command(self, message):
        """
        Function that informs us if the argument is a command or not

        Args:
            message (string): the string to evaluate

        Returns:
            bool: True if command, else FALSE
        """
        dico = json.loads(message)
        return dico["type"] == "command"

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
        return json.dumps(dico)  # data serialized

    def json_generator_message(self, message):
        """Function that formats the message in a form understandable by the server

        Args:
            message (string): the message in itslef

        Returns:
            str (json serialized): the format message
        """
        dico = {"type": "message", "message": message}
        return json.dumps(dico)  # data serialized

    def hex_to_ansi(self, hex_):
        """
        Function that converts hexadecimal values to ANSI value

        Args:
            hex_ (string): the hexadecimal value (#xxxxxx)

        Returns:
            (string): the ansi value
        """
        hex_ = hex_[1:]
        rgb = []
        for i in (0, 2, 4):
            decimal = int(hex_[i: i + 2], 16)
            rgb.append(decimal)
        R, G, B = rgb[0], rgb[1], rgb[2]

        return f"\033[38;2;{R};{G};{B}m"

    def encryptions_begin(self):
        public_key = self.rsa_c.generate_pem()
        self.s.sendall(public_key)

        rsa_encrypted_symmetric_key = self.s.recv(1024)
        key_symmetric = self.rsa_c.decrypt(rsa_encrypted_symmetric_key)
        print("key_symmetric", key_symmetric)
        self.Symmetric_cypher = Symmetric.cypher(key=key_symmetric)


if __name__ == "__main__":
    root = Tk()
    app = user(root)
    root.mainloop()

# TODO Ajouter + de couleur 
# TODO ERROR
# TODO PyQt5


import datetime
import random


class LOG:

    def __init__(self, colorDB):
        """Initialization of the class to display the LOGs of the server

        Args:
            colorDB (class): The class that takes care of managing colors
        """        

        self.RESET = "\033[m"  # Style reset character
        BLUE = "\033[38;2;0;55;218m"  # Blue style character
        self.colorDB = colorDB # DATABASE avec les couleurs

        self.addr_in_color = lambda addr: f"{self.colorDB.color_user_ANSI(addr)}{addr}{self.RESET}"
        # Lambda function to display addresses with the correct color (improves readability)
        self.time_ = lambda: f"{BLUE}{self.time()}{self.RESET}"
        # Lambda function to display the time with the correct color (improves readability)

        print(f"{self.time_()} Server Starting...")
        print(f"{self.time_()} Server waiting for connection...\n")

    def connection_server(self, addr):
        """
        Function that displays when someone connects

        Args:
            addr (tuple): The socket address (ip + port)
        """        
        print(f"{self.time_()} Connection received from {self.addr_in_color(addr)}",)

    def server_full(self, addr):
        """
        Function that displays when someone connects to the server but there is no more room

        Args:
            addr (tuple): The socket address (ip + port)
        """        
        print(f"{self.time_()} Connection received from {self.addr_in_color(addr)} but the server is full")
        
    def disconnection_server(self, addr):
        """
        Function that displays when someone disconnects

        Args:
            addr (tuple): The socket address (ip + port)
        """        
        print(f"{self.time_()} The client {self.addr_in_color(addr)} it's disconnected")

    def received_data(self, addr, data):
        """Function that displays the data received by the server

        Args:
            addr (tuple): The socket address (ip + port)    
            data (string): The character string that the client has just sent
        """        
        print(f"{self.time_()} {self.addr_in_color(addr)} had send : << {data} >> to the server ")

    def send_data(self, addr,  data):
        """Function that displays the data sent by the server

        Args:
            addr (tuple): The socket address (ip + port)   
            data (string): The character string that the client that the server sent
        """        
        print(f"{self.time_()} Server send {data} to {self.addr_in_color(addr)}")

    def showing_client(self):
        """
        Function that displays all connected users
        """        
        addrs = list(self.colorDB.return_Dico_key())
        max_ = self.colorDB.number_color()
        print(f"{self.time_()} The following clients are connected to the server : [{len(addrs)}/{max_}]")
        print(f"{self.time_()} ", end="")

        if len(addrs) == 0: print(f"None", end=f"{self.RESET}")
        else:
            for addr in addrs:
                print(f"{self.addr_in_color(addr)}", end=f"{self.RESET},")
        print("\n")

    def time(self):
        """Function that send back the time in a formated way 

        Returns:
            string: the time
        """        
        time = datetime.datetime.today().strftime("[%Y-%d-%m] [%H:%M:%S]")
        return time

    def rsa_public(self, addr):
        print(f"{self.time_()} User {self.addr_in_color(addr)} send the RSA public key")

    def generation_symmetric_key(self, addr, key):
        print(f"{self.time_()} The server sends the symmetric key {key} to {self.addr_in_color(addr)}")

if __name__ == "__main__":
    print("This class cannot be run alone")

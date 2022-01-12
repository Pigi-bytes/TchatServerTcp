import json
from tkinter import *
from tkinter import messagebox, ttk
import tkinter.font as tkFont

class Applications:

    def __init__(self, fen):
        """
        Initialization of the class that as a GUi base

        Args:
            fen (tk.Frame)): The frame where the window will be displayed
        """        

        self.fen = fen
        self.fen.title("Tchat via tcp, No Connect")
        self.fen.configure(bg='#F8F8F9')
        self.fen.option_add("*background", "#F8F8F9")
        self.fen.option_add("*foreground", "#2D2D3B")
        self.fen.option_add("*Button.background", "#F2CD15")
        Consolas = tkFont.Font(family='Consolas', size=10, weight="bold")
        self.fen.option_add("*font", Consolas)

        
        self.pseudo = "ANON"
        # self.fen.iconphoto(True, PhotoImage(file=pathfile + '\icone.png'))
        # self.fen.geometry("400x550")

        # ---------- Init display ----------
        self.frame_tchat = Frame(self.fen, bd=1, bg="#262D47")
        
        label_tchat = Label(self.frame_tchat, text="Tchat :", bg="#262D47", fg="#F8F8F9")
        label_tchat.grid(column=0, row=0, padx=5, pady=5)

        self.frame_tchat_2 = VerticalScrolledFrame(self.frame_tchat, height=50, width=125)
        # ----------------------------------

        # ---------- Init parti saisi ip ----------
        self.frame_addr = Frame(self.fen, bd=1)

        label_ip = Label(self.frame_addr, text="Server Ip : ")
        label_ip.grid(column=0, row=0, padx=5, pady=5)

        self.input_ip = Entry(self.frame_addr, width=9)
        self.input_ip.grid(column=1, row=0, padx=5, pady=5,)

        label_port = Label(self.frame_addr, text="Server Port :")
        label_port.grid(column=2, row=0, padx=5, pady=5)

        self.input_port = Entry(self.frame_addr, width=5)
        self.input_port.grid(column=3, row=0, padx=5, pady=5,)

        self.button_join_server = Button(self.frame_addr, text="Join Server", bd='1')
        self.button_join_server.grid(column=4, row=0, padx=10, pady=5)
        # -----------------------------------------

        # ---------- Init parti pseudo ----------
        self.frame_pseudo = Frame(self.fen, bd=1)

        label_pseudo = Label(self.frame_pseudo, text="Enter your nickname :")
        label_pseudo.grid(column=0, row=0, padx=5, pady=5)

        self.txt_input_pseudo = StringVar()
        self.txt_input_pseudo.trace('w', self.limit_pseudo_size)
        self.input_pseudo = Entry(self.frame_pseudo, width=20, textvariable=self.txt_input_pseudo)
        self.input_pseudo.grid(column=1, row=0, padx=5, pady=5,)

        self.button_confirm_pseudo = Button(self.frame_pseudo, text="Confirm", bd='1')
        self.button_confirm_pseudo.grid(column=2, row=0, padx=10, pady=5)
        # ---------------------------------------

        # ---------- Init parti saisi message ----------
        self.frame_message = Frame(self.fen, bd=1,)

        self.label_message = Label(self.frame_message, text="As /")
        self.label_message.grid(column=0, row=0, padx=5, pady=5)

        self.input_message = Entry(self.frame_message, width=30)
        self.input_message.grid(column=1, row=0, padx=5, pady=5,)

        self.button_send_message = Button(self.frame_message, text="Send", bd='1')
        self.button_send_message.grid(column=2, row=0, padx=10, pady=5)
        # ----------------------------------------------

    def config_call_function(self, func_addr, func_pseudo, func_message):
        """Function that associates each button with a function

        Args:
            func_addr (function): the function associate with the 'Join Server' button
            func_pseudo (function): the function associate with the 'Confirm' button
            func_message (function): the function associate with the 'Send' button
        """         

        self.button_join_server["command"] = func_addr
        self.button_confirm_pseudo["command"] = func_pseudo
        self.button_send_message["command"] = func_message

    def show_addr(self):
        """
        Function that allows you to show the frame where you enter the IP
        """        
        self.fen.bind('<Return>', self.button_join_server["command"])
        self.input_ip.focus_set()
        self.frame_addr.grid(column=0, row=1, padx=10, pady=5, sticky=N)

    def show_pseudo(self):
        """
        Function that allows you to show the frame where you enter your pseudo
        """
        self.fen.bind('<Return>', self.button_confirm_pseudo["command"])
        self.input_pseudo.focus_set()
        self.frame_pseudo.grid(column=0, row=1, padx=10, pady=5, sticky=N)

    def show_message(self):
        """
        Function that allows you to show the frame where you enter your message
        """
        self.fen.bind('<Return>', self.button_send_message["command"])
        self.input_message.focus_set()
        self.frame_message.grid(column=0, row=1, padx=10, pady=5,)
        self.frame_tchat_2.grid(column=0, row=1, padx=10, pady=5,)
        self.frame_tchat.grid(column=0, row=0, padx=2, pady=2, sticky=NSEW)

    def hide_addr(self):
        """
        Function that allows you to hide the frame where you enter the IP
        """
        self.frame_addr.grid_forget()

    def hide_pseudo(self):
        """
        Function that allows you to hide the frame where you enter your pseudo
        """
        self.frame_pseudo.grid_forget()

    def hide_message(self):
        """
        Function that allows you to hide the frame where you enter your message
        """
        self.frame_message.grid_forget()

    def error_pseudo(self):
        """
        Function that shows an error message if the nickname is not valid
        """
        messagebox.showerror("Error in your nickname", """Your name is not valid, is it less than 20 characters? 
        Maybe it is already used on the chat, or it contains non ASCII characters or those: / \: *? \ "<> |""",)

    def error_server(self):
        """
        Function that shows an error message if we are not able to reach the server
        """
        messagebox.showerror("Cannot access the server ",
                             "The waiter asks is not reachable, maybe the address is not the right one? Or the server may be offline")

    def error_serverfull(self):
        """
        Function that shows an error message if we are not able to connect bc the server is full
        """
        messagebox.showerror("Cannot access the server ",
                             "The server is full, retry in a moment")

    def return_addr(self):
        """
        Function that return the address enter on the Input

        Returns:
            tuple: the ip and the port enter by the user
        """        
        host, port = self.input_ip.get(), self.input_port.get()
        return host.strip(), port.strip()

    def return_pseudo(self):
        """
        Function that return the name enter by the user

        Returns:
            string: the pseudo enter by the user
        """
        return self.input_pseudo.get().strip()

    def return_message(self):
        """
        Function that return the message enter by the user

        Returns:
            string: the message the user enter
        """
        message = self.input_message.get()
        # We delete what the user wrote
        self.input_message.delete(0, END)
        return message.strip()

    def update_name(self, name):
        """
        Function that updates the new username

        Args:
            name (string): The new name of the user
        """        
        self.pseudo = name
        self.label_message["text"] = f"As {self.pseudo} :"
        self.fen.title(f"Tchat via TCP, connected as {self.pseudo}")

    def add_to_tchat(self, color, sender, message):
        """
        Function that add a new message on the tchatboard

        Args:
            color (string): the color of the message
            sender (string): who send the message
            message (string): the message on itself
        """         
        message = f"{sender} : {message}"

        label_ = Label(self.frame_tchat_2.interior, text=message, justify="left", fg=color)
        label_.pack(pady=0.3, anchor='w')
        self.frame_tchat_2.scrollbar_update_w()

    def afficher_annonce(self, name, addr, mode):
        """
        Function that add a new annoucement on the tchatboard

        Args:
            name (string): the name of the trigger
            addr (tuple): the ip+port of the trigger
            mode (string): the mode of the annoucement
        """        

        if mode == "connection":
            message = f"New user on the tchat : {addr} under the following nickname : {name}"
        elif mode == "disconnection":
            message = f"User {addr} under the following nickname {name} has disconnected"

        label_ = Label(self.frame_tchat_2.interior, text=message, justify="left", )
        label_.pack(padx=0.2, pady=0.1, anchor='w')
        self.frame_tchat_2.scrollbar_update_w()

    def limit_pseudo_size(self, *args,):
        """
        Function call at ecah key stroke in the pseudo input
        Limit the size of the input by 20 chars
        """        
        value = self.txt_input_pseudo.get()
        if len(value) > 20:
            self.txt_input_pseudo.set(value[:20])


class VerticalScrolledFrame(Frame):
    """A pure Tkinter scrollable frame that actually works!
    * Use the 'interior' attribute to place widgets inside the scrollable frame
    * Construct and pack/place/grid normally
    * This frame only allows vertical scrolling

    """

    def __init__(self, parent, *args, **kw):
        Frame.__init__(self, parent, *args, **kw)

        # create a canvas object and a vertical scrollbar for scrolling it
        self.vscrollbar = Scrollbar(self, orient=VERTICAL)
        self.vscrollbar.pack(fill=Y, side=RIGHT, expand=FALSE)
        self.canvas = Canvas(self, bd=0, highlightthickness=0,
                        yscrollcommand=self.vscrollbar.set)
        self.canvas.pack(side=LEFT, fill=BOTH, expand=TRUE)
        self.vscrollbar.config(command=self.canvas.yview)

        # reset the view
        self.canvas.xview_moveto(0)
        self.canvas.yview_moveto(0)

        # create a frame inside the canvas which will be scrolled with it
        self.interior = interior = Frame(self.canvas)
        interior_id = self.canvas.create_window(0, 0, window=interior,
                                           anchor=NW)

        # track changes to the canvas and frame width and sync them,
        # also updating the scrollbar
        def _configure_interior(event):
            # update the scrollbars to match the size of the inner frame
            size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
            self.canvas.config(scrollregion="0 0 %s %s" % size)
            if interior.winfo_reqwidth() != self.canvas.winfo_width():
                # update the canvas's width to fit the inner frame
                self.canvas.config(width=interior.winfo_reqwidth())
        interior.bind('<Configure>', _configure_interior)

        def _configure_canvas(event):
            if interior.winfo_reqwidth() != self.canvas.winfo_width():
                # update the inner frame's width to fill the canvas
                canvas.itemconfigure(interior_id, width=self.canvas.winfo_width())
        self.canvas.bind('<Configure>', _configure_canvas)

    def scrollbar_update_w(self):
        self.canvas.yview_moveto('1.0')



if __name__ == "__main__":
    print("This class cannot be run alone")

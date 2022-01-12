from random import choice


class Color:
    
    def __init__(self):
        """
        Initialization of the class that serve as a DATABASE
        """
        self.color_non_use = [
            self.rgb_to_hex(58, 150, 221),
            self.rgb_to_hex(221, 150, 58),
            self.rgb_to_hex(207, 45, 250),
            self.rgb_to_hex(123, 27, 241),
            self.rgb_to_hex(206, 209, 26),
            self.rgb_to_hex(94, 105, 115),
            self.rgb_to_hex(115, 44, 44),
            self.rgb_to_hex(200, 29, 38),
            self.rgb_to_hex(77, 175, 188)
                            ]
        # Different color
        self.nb_color = len(self.color_non_use)
        # Number of color max
        self.color_use = []
        # Color in use
        self.color_for_user = {}
        # Dico use for associate color and user

    def temporary_user(self, addr):
        """
        Function that generates a temporary color for a user
        to give it a color in the logs. Use when a user
        cannot join the server because no color left

        Args:
            addr (tuple): The socket address (ip + port)
        """
        self.color_for_user[addr] = self.rgb_to_hex(255, 255, 255)

    def del_temporary_user(self, addr):
        """
        Function that delete the temporary color given to a user

        Args:
            addr (tuple): The socket address (ip + port)
        """
        del self.color_for_user[addr]

    def del_user(self, addr):
        """
        Function use to delete users and release color
        when they are no longer connected

        Args:
            addr (tuple): The socket address (ip + port)
        """
        color = self.color_for_user[addr]
        # We get the color associated with the user
        self.color_non_use.append(color)
        # Add the color to the non-use color list
        self.color_use.remove(color)
        # We remove the color from the list of colors to use
        del self.color_for_user[addr]
        # we delete the user from the dictionary

    def add_user(self, addr):
        """
        Function use to add users and associate color to them
        when they log in for the first time

        Args:
            addr (tuple): The socket address (ip + port)
        """
        assert len(self.color_non_use) >= 0, "No color left"

        color = choice(self.color_non_use)
        # Color chosen randomly from the remaining one
        self.color_for_user[addr] = color
        # We associate the user with his color
        self.color_non_use.remove(color)
        # We remove the color to use from the list of free colors
        self.color_use.append(color)
        # Add the color to use in the list of non-free colors

    def color_user_HEX(self, addr):
        """
        Function that returns the color associated with the user in hexadecimal form

        Args:
            addr (tuple): The socket address (ip + port)

        Returns:
            (string): The color under a hexadecimal form
        """
        return self.color_for_user[addr]

    def color_user_ANSI(self, addr):
        """
        Function that returns the color associated with the user in ansi form

        Args:
            addr (tuple): The socket address (ip + port)

        Returns:
            (string): The color under a ansi form
        """
        h = self.color_for_user[addr]
        return self.hex_to_ansi(h)

    def return_Dico_key(self):
        """
        Return the key of the dictionary (all the addresses connected to the server

        Returns:
            (list): The dictionary keys
        """
        return self.color_for_user.keys()

    def rgb_to_hex(self, r, g, b):
        """
        Function that converts RGB values to Hexadecimal value

        Args:
            r, g, b (int): Each value for the color

        Returns:
            (string): The hexadecimal form (#XXXXXX)
        """
        return "#{:02x}{:02x}{:02x}".format(r, g, b)

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

    def number_color(self):
        """
        Return the number of color available

        Returns:
            int: the number of color available
        """
        return self.nb_color


if __name__ == "__main__":
    print("This class cannot be run alone")

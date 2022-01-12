from cryptography.fernet import Fernet


class cypher:

    def __init__(self, key=None):
        """
        The init of the cypher class

        Args:
            key (byte, optional): If the key is needed to be generate user need to enter the key here. Defaults to None.
        """
        if key == None:
            self.key = Fernet.generate_key()
        else:
            self.key = key
        self.fernet = Fernet(self.key)

    def get_key(self):
        """
        Return the key of the cypher

        Returns:
            byte: The key 
        """
        return self.key

    def encrypt(self, data):
        """
        Function to encrypt data using the key

        Args:
            data (byte): The data to encrypt

        Returns:
            byte: The data encrypted
        """
        return self.fernet.encrypt(data.encode())

    def decrypt(self, data):
        """
        Function to decrypt data using the key

        Args:
            data (byte): The data to decrypt

        Returns:
            string: The data decrypted
        """
        return self.fernet.decrypt(data).decode()

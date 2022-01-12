import base64

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import load_pem_public_key

class rsa_server:

    def __init__(self, public_key_pem):
        """
        The init of the rsa_server class

        Args:
            public_key_pem(byte): the public key in a pem format 
        """
        self.public_key = load_pem_public_key(public_key_pem)

    def encrypt(self, data):
        """
        Encrypt the data 

        Args:
            data(byte): The data to encrypt

        Returns:
            byte: The data encrypted with the public key
        """
        encrypted = base64.b64encode(self.public_key.encrypt(
        data, padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None,)))

        return encrypted


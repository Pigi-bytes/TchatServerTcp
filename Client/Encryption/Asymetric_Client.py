import base64

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding



class rsa_client:

    def __init__(self,):
        """
        The init of the rsa_server class

        Args:
            public_key_pem(byte): the public key in a pem format
        """
        self.private_key, self.public_key = self.generate_key()

    def generate_key(self,):
        """
        Generate the private and public key 
        
        Returns:
            tuple: the key 
            cryptography.hazmat.backends.openssl.rsa._RSAPrivateKey
            cryptography.hazmat.backends.openssl.rsa._RSAPublicKey
        """
        private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=default_backend())
        public_key = private_key.public_key()
        return private_key, public_key

    def generate_pem(self):
        """
        Generate the pem to send the key 

        Returns:
            byte: the public_key in byte format
        """        
        pem = self.public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo)
        
        return pem

    def decrypt(self, data):
        """
        Decrypt the data enter in args

        Args:
            data (bytes): the data to decrypt

        Returns:
            byte: The data decrypted with the private key 
        """
        decrypted = self.private_key.decrypt(
            base64.b64decode(data),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,))

        return decrypted


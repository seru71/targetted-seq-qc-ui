import os
import json

from Crypto.Cipher import AES
from data_share.Pad import Pad


class DataShare(object):

    @staticmethod
    def decrypt_data(data):
        assert isinstance(data, str)
        obj = AES.new(os.environ.get('ENCRYPTION_KEY'), AES.MODE_CBC, 'This is an IV456')
        bytes_data = bytes.fromhex(data)
        return Pad.unpad(obj.decrypt(bytes_data)).decode()

    @staticmethod
    def encrypt_data(data):
        assert isinstance(data, str)
        obj = AES.new(os.environ.get('ENCRYPTION_KEY'), AES.MODE_CBC, 'This is an IV456')
        padded = Pad.pad(data.encode())
        ciphertext = obj.encrypt(padded)
        return ciphertext.hex()

    @staticmethod
    def validate_signature(signature):
        return signature == 'dawid'

    @staticmethod
    def prepare_data_for_sending(data):
        return json.dumps(data)

import os

import Crypto
import Crypto.Random
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP


class KeyGeneration(object):

    def __init__(self):
        self.private_key = 0
        self.public_key = 0

    def generate_keys(self, key_length):
        random_gen = Crypto.Random.new().read
        self.private_key = RSA.generate(key_length, random_gen)
        self.public_key = self.private_key.publickey()

    def save_keys(self):
        for key, key_name in [(self.private_key, 'private'), (self.public_key, 'public')]:
            with open(os.path.join('keys', '{}.key'.format(key_name)), 'wb') as file:
                file.write(key.exportKey())

    def load_keys(self):
        self._load_private()
        self._load_public()

        return self.private_key, self.public_key

    def _load_private(self):
        path = os.path.join('keys')
        with open(os.path.join(path, '{}.key'.format('private')), 'rb') as file:
            self.private_key = RSA.importKey(file.read())

    def _load_public(self):
        path = os.path.join('keys')
        with open(os.path.join(path, '{}.key'.format('public')), 'rb') as file:
            self.private_key = RSA.importKey(file.read())

    def load_or_generate(self):
        path = os.path.join('keys')

        keys_path_content = os.listdir(path)

        if 'private.key' not in keys_path_content or 'public.key' not in keys_path_content:
            self.generate_keys(4 * 1024)
            self.save_keys()
        else:
            self.load_keys()

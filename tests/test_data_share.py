import pytest

import data_share


def check_encrypt_and_decrypt(information):
    encrypted = data_share.DataShare.encrypt_data(information)
    decrypted = data_share.DataShare.decrypt_data(encrypted)

    return information, encrypted, decrypted


def test_encryption():
    test_messages = ['x' * x for x in range(17)]

    for message in test_messages:
        information, _, decrypted = check_encrypt_and_decrypt(message)

        assert information == decrypted

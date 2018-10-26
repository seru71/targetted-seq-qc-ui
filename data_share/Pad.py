class Pad(object):

    @staticmethod
    def pad(data, base=16):
        assert isinstance(data, bytes)
        length = base - (len(data) % base)

        return data + bytes([length]) * length

    @staticmethod
    def unpad(data):
        assert isinstance(data, bytes)
        return data[:-data[-1]]


if __name__ == '__main__':
    padded = Pad.pad('dawid'.encode())
    print(padded)
    print(Pad.unpad(padded))

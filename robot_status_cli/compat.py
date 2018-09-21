import sys


def get_str_to_hex(text):
    if sys.version_info >= (3,0):
        return text.hex()
    import binascii
    return binascii.hexlify(text)
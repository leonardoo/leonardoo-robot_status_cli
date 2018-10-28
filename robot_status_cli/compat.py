import sys


def is_python_3():
    return sys.version_info[0] >= 3


def get_str_to_hex(text):
    if is_python_3():
        return text.hex()
    import binascii
    return binascii.hexlify(text)


def get_bytes_from_str(text):
    if is_python_3():
        return bytes.fromhex(text)
    return bytes(bytearray.fromhex(text))

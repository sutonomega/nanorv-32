import struct
import zlib


def reference_crc(content):
    checksum = 0xFFFFFFFF
    for byte in content:
        checksum ^= byte
        for bit_index in range(8):
            checksum = (checksum >> 1) ^ (0xEDB88320 if checksum & 1 else 0)
    return checksum ^ 0xFFFFFFFF


def frame(command, payload):
    content = struct.pack('<BBI', 1, command, len(payload)) + payload
    return b'NRV1' + content + struct.pack('<I', zlib.crc32(content))


assert zlib.crc32(b'123456789') == 0xCBF43926
vectors = {
    'LOAD EBREAK': frame(1, bytes.fromhex('73 00 10 00')),
    'START': frame(2, b''),
    'ACK LOAD': frame(0x81, bytes([1, 0])),
    'ACK START': frame(0x81, bytes([2, 0])),
    'NACK START image absent': frame(0x82, bytes([2, 5])),
}
expected = {
    'LOAD EBREAK': '4e52563101010400000073001000d20431ac',
    'START': '4e52563101020000000066215e00',
    'ACK LOAD': '4e5256310181020000000100fbae3ad3',
    'ACK START': '4e525631018102000000020038fd17f8',
    'NACK START image absent': '4e52563101820200000002052a1395b9',
}
for name, packet in vectors.items():
    assert packet.hex() == expected[name], name
    length = struct.unpack_from('<I', packet, 6)[0]
    assert len(packet) == length + 14
    assert struct.unpack_from('<I', packet, len(packet) - 4)[0] == zlib.crc32(packet[4:-4])
    assert reference_crc(packet[4:-4]) == struct.unpack_from('<I', packet, len(packet) - 4)[0]
    for byte_index in range(4, len(packet) - 4):
        corrupted = bytearray(packet)
        corrupted[byte_index] ^= 1
        assert reference_crc(corrupted[4:-4]) != struct.unpack_from('<I', corrupted, len(corrupted) - 4)[0]
    print(f'{name}: {packet.hex(" ")}')

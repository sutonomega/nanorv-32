import struct
import zlib


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
for name, packet in vectors.items():
    length = struct.unpack_from('<I', packet, 6)[0]
    assert len(packet) == length + 14
    assert struct.unpack_from('<I', packet, len(packet) - 4)[0] == zlib.crc32(packet[4:-4])
    print(f'{name}: {packet.hex(" ")}')

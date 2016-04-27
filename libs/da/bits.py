

def xor(a: bytearray, b: bytearray, l: int) -> bytearray:
    result = bytearray(l)

    for i in range(l):
        result[i] = a[i] ^ b[i]

    return result


def test(frame: bytearray, offset: int) -> bool:
    byte = frame[offset // 8]
    mask = 1 << (7 - offset % 8)

    return byte & mask > 0

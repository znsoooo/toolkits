import zlib
import base64

def slide(start, length, half_window=16384):
    return max(0, start-half_window), min(length, start+half_window)

def compress(old, new):
    if isinstance(old, str):
        old = old.encode()
    if isinstance(new, str):
        new = new.encode()
    old_length = len(old)

    i = 0
    length = 3
    packed = []
    while i < len(new):
        # print(length, new[i:i+length][-30:])
        start, end = slide(i, old_length)
        window = old[start:end]

        # extend repeated
        if new[i:i+length+1] in window and i+length < len(new) and length < 255:
            length += 1
        elif new[i:i+length] in window:
            packed.append((0, window.index(new[i:i+length]), length))
            i += length
            length = 3

        # extend not repeated
        elif new[i+length-3:i+length] not in window and i+length-3 < len(new) and length-3 < 127:
            length += 1
        else:
            packed.append((1, new[i:i+length-3], length-3))
            i += length-3
            length = 3

    packed2 = b''
    for mode, data, length in packed:
        if mode:
            packed2 += bytes([128+length]) + data
        else:
            assert (data < 32768)
            pos1, pos2 = divmod(data, 256)
            packed2 += bytes([pos1, pos2, length])

    packed3 = zlib.compress(packed2)
    packed4 = base64.b64encode(packed3[2:]).decode().strip('=')

    return packed4

def decompress(old, packed):
    if isinstance(old, str):
        old = old.encode()

    tail = len(packed) % 4 * '='
    unpacked1 = base64.b64decode(packed + tail)
    unpacked2 = zlib.decompress(b'x\x9c' + unpacked1)
    unpacked3 = b''

    i = 0
    pos = 0
    old_length = len(old)
    while i < len(unpacked2):
        mode, num = divmod(unpacked2[i], 128)
        start, end = slide(pos, old_length)
        window = old[start:end]
        if mode:
            length = num
            unpacked3 += unpacked2[i+1:i+length+1]
            i += length + 1
        else:
            pos1, pos2, length = unpacked2[i:i+3]
            pos = (pos1 << 8) + pos2
            unpacked3 += old[pos:pos+length]
            i += 3

    return unpacked3


if __name__ == '__main__':
    with open('比对1.03.py', 'rb') as f:
        b1 = f.read()
    with open('比对1.04.py', 'rb') as f:
        b2 = f.read()

    packed = compress(b1, b2)
    unpacked = decompress(b1, packed)
    print(packed)

    with open('unpack_zip_from_base64_2.txt', 'wb') as f:
        f.write(unpacked)

    packed = compress('12323454325', '456342545')
    print(packed)


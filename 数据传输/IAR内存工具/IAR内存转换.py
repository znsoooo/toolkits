import lsx
import struct
import binascii


def hex2bin(path):
    assert '.hex' == lsx.ext(path), lsx.ext(path)
    text = lsx.read(path)
    lines = text.splitlines()
    lines = [line[12:-2] for line in lines[1:-1]]
    data = binascii.a2b_hex(''.join(lines))
    lsx.write(lsx.p12(path, '.bin'), data)


def bin2hex(path, addr=0):
    assert '.bin' == lsx.ext(path), lsx.ext(path)
    lines = ['S0030000FC']
    data = lsx.readb(path)
    for block in lsx.split(data, 16):
        block = struct.pack('>i', addr) + block
        block = struct.pack('>b', len(block) + 1) + block
        block = block + bytes([0xFF - (sum(block) & 0xFF)])
        line = 'S3' + binascii.b2a_hex(block).upper().decode()
        lines.append(line)
        addr += 16
    lines.append('S70500000000FA')
    lsx.write(lsx.p12(path, '.out.hex'), lines)


if __name__ == '__main__':
    hex2bin('motorola.hex')
    hex2bin('motorola2.hex')

    bin2hex('motorola.bin', 0x0C8A5000)
    bin2hex('motorola2.bin', 0x0C8A4FE4)

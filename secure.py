# secure.py
import binascii

IP = [58, 50, 42, 34, 26, 18, 10, 2,
      60, 52, 44, 36, 28, 20, 12, 4,
      62, 54, 46, 38, 30, 22, 14, 6,
      64, 56, 48, 40, 32, 24, 16, 8,
      57, 49, 41, 33, 25, 17, 9, 1,
      59, 51, 43, 35, 27, 19, 11, 3,
      61, 53, 45, 37, 29, 21, 13, 5,
      63, 55, 47, 39, 31, 23, 15, 7]

FP = [40, 8, 48, 16, 56, 24, 64, 32,
      39, 7, 47, 15, 55, 23, 63, 31,
      38, 6, 46, 14, 54, 22, 62, 30,
      37, 5, 45, 13, 53, 21, 61, 29,
      36, 4, 44, 12, 52, 20, 60, 28,
      35, 3, 43, 11, 51, 19, 59, 27,
      34, 2, 42, 10, 50, 18, 58, 26,
      33, 1, 41, 9, 49, 17, 57, 25]

E = [32, 1, 2, 3, 4, 5,
     4, 5, 6, 7, 8, 9,
     8, 9, 10, 11, 12, 13,
     12, 13, 14, 15, 16, 17,
     16, 17, 18, 19, 20, 21,
     20, 21, 22, 23, 24, 25,
     24, 25, 26, 27, 28, 29,
     28, 29, 30, 31, 32, 1]

P = [16, 7, 20, 21, 29, 12, 28, 17,
     1, 15, 23, 26, 5, 18, 31, 10,
     2, 8, 24, 14, 32, 27, 3, 9,
     19, 13, 30, 6, 22, 11, 4, 25]

S_BOXES = [
    [
        [14, 4, 13, 1, 2, 15, 11, 8, 3, 10, 6, 12, 5, 9, 0, 7],
        [0, 15, 7, 4, 14, 2, 13, 1, 10, 6, 12, 11, 9, 5, 3, 8],
        [4, 1, 14, 8, 13, 6, 2, 11, 15, 12, 9, 7, 3, 10, 5, 0],
        [15, 12, 8, 2, 4, 9, 1, 7, 5, 11, 3, 14, 10, 0, 6, 13]
    ],
] * 8  # Repeat for simplicity

def string_to_bin(text):
    return ''.join(f'{ord(c):08b}' for c in text.ljust(8))

def bin_to_string(b):
    return ''.join(chr(int(b[i:i + 8], 2)) for i in range(0, 64, 8)).rstrip()

def permute(block, table):
    return ''.join(block[i - 1] for i in table)

def xor(a, b):
    return ''.join('0' if i == j else '1' for i, j in zip(a, b))

def sbox_substitution(bits):
    result = ''
    for i in range(8):
        block = bits[i * 6:(i + 1) * 6]
        row = int(block[0] + block[5], 2)
        col = int(block[1:5], 2)
        val = S_BOXES[i][row][col]
        result += f'{val:04b}'
    return result

def feistel(right, subkey):
    expanded = permute(right, E)
    xored = xor(expanded, subkey)
    substituted = sbox_substitution(xored)
    return permute(substituted, P)

def key_schedule(key):
    return [key] * 16  # Simple repetition

def des_encrypt_block(plain_bin, key_bin):
    perm = permute(plain_bin, IP)
    left, right = perm[:32], perm[32:]
    keys = key_schedule(key_bin)

    for i in range(16):
        temp = right
        right = xor(left, feistel(right, keys[i]))
        left = temp

    return permute(right + left, FP)

def des_decrypt_block(cipher_bin, key_bin):
    perm = permute(cipher_bin, IP)
    left, right = perm[:32], perm[32:]
    keys = key_schedule(key_bin)[::-1]

    for i in range(16):
        temp = right
        right = xor(left, feistel(right, keys[i]))
        left = temp

    return permute(right + left, FP)

def pad(text):
    pad_len = 8 - (len(text) % 8)
    return text + chr(pad_len) * pad_len

def unpad(text):
    pad_len = ord(text[-1])
    return text[:-pad_len]

# Public API
def des_encrypt(text, key):
    text = pad(text)
    key_bin = string_to_bin(key[:8])
    result = ''
    for i in range(0, len(text), 8):
        block = text[i:i + 8]
        block_bin = string_to_bin(block)
        encrypted_bin = des_encrypt_block(block_bin, key_bin)
        result += f'{int(encrypted_bin, 2):016x}'
    return result

def des_decrypt(cipher_hex, key):
    key_bin = string_to_bin(key[:8])
    result = ''
    for i in range(0, len(cipher_hex), 16):
        block_hex = cipher_hex[i:i + 16]
        block_bin = f'{int(block_hex, 16):064b}'
        decrypted_bin = des_decrypt_block(block_bin, key_bin)
        result += bin_to_string(decrypted_bin)
    return unpad(result)

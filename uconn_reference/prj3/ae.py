#!/usr/bin/python3
import os
from cryptography.hazmat.primitives.ciphers.aead import AESCCM
from cryptography.hazmat.primitives import keywrap
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

string ="This is a secret message."

#convert to bytes. The default format is utf-8 
data = str.encode(string)
aad = b"authenticated but unencrypted data"
# aad can be empty, it is not in the ciphertext
aad = b''

# randomly generate key and nonce
# python 3.5+ supports hex()
key = AESCCM.generate_key(bit_length=128)
print("key in hex =", key.hex())
aesccm = AESCCM(key)
nonce = os.urandom(13)  # must be 7 or 13
print("nouce in hex =", nonce.hex())

# ct is bytes and hexstr is the hex string 
ct = aesccm.encrypt(nonce, data, aad)

hexstr = ct.hex() 

print("ciphertext raw bytes =", ct)       # this is bytes
print("ciphertext in hex =", hexstr)   # this is string

# hex string to bytes
ct1 = bytes.fromhex(hexstr)

assert ct == ct1

# aesccm already has the key
# decrypted plaintext is bytes
# should catch the exception 

pt = aesccm.decrypt(nonce, ct, aad)

# decode bytes to string
new_string = pt.decode()
print("Plaintext' =", new_string)

### key wrapping

kek = AESCCM.generate_key(bit_length=128)

# the lenght of the key to be wrapped must be a multiple of 64
wrapped_key = keywrap.aes_key_wrap(kek, key)
print("wrapped_key in hex =", wrapped_key.hex())

key2 = keywrap.aes_key_unwrap(kek, wrapped_key)

assert key == key2

# if a byte is changed, unwrap will raise an exception
ba = bytearray(wrapped_key)
# ba[0] += 1
wrapped_key = bytes(ba)
key2 = keywrap.aes_key_unwrap(kek, wrapped_key)

# key derivation
salt = b'9eQ23/adfjACX.#8'
kdf = PBKDF2HMAC(
    algorithm=hashes.SHA256(),
    length=16,
    salt=salt,
    iterations=100000
)
# input is bytes
key = kdf.derive(b"my great password")
print("derived key in hex =", key.hex())


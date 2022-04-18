from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db


import os
from cryptography.hazmat.primitives.ciphers.aead import AESCCM
from cryptography.hazmat.primitives import keywrap
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


bp = Blueprint("blog", __name__)

# CSE4400: import current_app so we can access SECRET_KEY in configuration
#           current_app.config['POST_MASTER_KEY']
from flask import current_app
import json

body = "Subash Poudyal"
print("Body:", body, type(body))
data = str.encode(body) # convert str to byte
print("body in bytes:", data, type(data))
POST_MASTER_KEY = "This is the key to encrypt post"
PMK_bytes = str.encode(POST_MASTER_KEY) # convert to byte

nonce = os.urandom(13) # we need to store in db
print("Nonce=", nonce)
key = AESCCM.generate_key(bit_length = 128)
print("Key=", key)

salt = os.urandom(16)
print("Salt=", salt)
kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=100000,)
kek = kdf.derive(PMK_bytes)

wrapped_key = keywrap.aes_key_wrap(kek, key) # we need to store in DB
print("Wrapped key:", wrapped_key)
   
aesccm = AESCCM(key)

ct = aesccm.encrypt(nonce, data, PMK_bytes)
print("Cipher txt:", ct)

# Decryption section
# parameters: salt, PMK_bytes
kdf1 = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=100000,)
kek1 = kdf1.derive(PMK_bytes)

key1 = keywrap.aes_key_unwrap(kek1, wrapped_key)
result = key1 == key
print("Key comparison:", result)
aesccm = AESCCM(key1)

pt_text = aesccm.decrypt(nonce, ct, PMK_bytes)
print("Plain text:", pt_text.decode(), type(pt_text.decode()))

## No need to change anything below
## Search CSE4400 to find out the changes from the original file
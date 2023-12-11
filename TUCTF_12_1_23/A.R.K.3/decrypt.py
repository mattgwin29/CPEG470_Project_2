import binascii

import Crypto
from Crypto.Cipher import DES3
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Hash import SHA1

#meow.keychain:$keychain$*9196324d59f13ef6b20331e2e6d81da8993a02db*34d065407b48d418*976cb9617ec4e656d7fdbb097c525c9fc7502908aab1dc9aefbf40b24368ee8e78af756e91cc960a65d90f9be62e4240

password = "password"
salt = binascii.unhexlify('9196324d59f13ef6b20331e2e6d81da8993a02db')
iv = binascii.unhexlify('34d065407b48d418')
data = binascii.unhexlify('976cb9617ec4e656d7fdbb097c525c9fc7502908aab1dc9aefbf40b24368ee8e78af756e91cc960a65d90f9be62e4240')

key = PBKDF2(password, salt, 24, count=1000, hmac_hash_module=SHA1)
c = DES3.new(key, DES3.MODE_CBC, iv)
t = c.decrypt(data)

print(binascii.hexlify(t))

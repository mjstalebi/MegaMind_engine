import os
from Commu import Commu
import json
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.primitives.serialization import load_pem_public_key
import base64

pubkey_pem = b"-----BEGIN PUBLIC KEY-----\nMIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDlWUe72WqerBFdIIpFroL26E7i\n/P/qSeTN+5spVpHXmikNJ+EJtiY8vcfQ8mzSFlzrOQWz2geawjeAGy+6mBiNjr8i\nizlagasYtGGC+YuIQsiHs8C8yn2pQRE67gsXL32f66m5AcGZ2NxZFe6lAHa15BxV\nc5yVonZPcSquis7yxQIDAQAB\n-----END PUBLIC KEY-----\n"

plaintextMessage = b"This is the symteric key"
alicePubKey = load_pem_public_key(pubkey_pem,default_backend())
ciphertext = alicePubKey.encrypt(
    plaintextMessage,
    padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
  )
)
print('cipher text', ciphertext)
s1 = base64.b32encode(ciphertext)
print(s1)
s1 = s1.replace('=' , '')
print(s1)


def pr(*args , **kwargs):
	print( '**** ' + " ".join(map(str,args)) + " ****" , **kwargs)

pr("secret chat extention")
comm = Commu()
comm.update_ready(False)

while True:
	comm.wait_for_new_data()
	session = comm.read_data()
	pr(session)
	item = comm.get_item_of_interest(session)
	
	print(item)
	if (get_num_of_requests(session) == 2):
		item = "key is " + s1
	else:
		item = encrypt_request(item)
	item = item.replace('saba','sarah')
	item = item.replace('ardalan','alex')
	comm.write_response(item)
	comm.update_ready(True)

	

import os
import subprocess
import base64

base_path = r"c:\Users\moust\Downloads\SecureShare-Main\SecureShare-Main"

# Generate keys
subprocess.run(["bash", "client/encryption/generate_keys.sh"], cwd=base_path)

pub_key = os.path.join(base_path, "client", "keys", "public.pem")
priv_key = os.path.join(base_path, "client", "keys", "private.pem")

# Encrypt
temp_in = os.path.join(base_path, "client", "temp", "test_in.txt")
temp_out = os.path.join(base_path, "client", "temp", "test_out.enc")
with open(temp_in, "w") as f: f.write("Hello World Secret")

script_enc = os.path.join(base_path, "client", "encryption", "encrypt.sh")
res1 = subprocess.run(["bash", script_enc, pub_key, temp_in, temp_out], cwd=os.path.join(base_path, "client", "encryption"), capture_output=True, text=True)
print("Encrypt stdout:", res1.stdout)
print("Encrypt stderr:", res1.stderr)

with open(temp_out, "rb") as f:
    enc_b64 = base64.b64encode(f.read()).decode()

# Decrypt
dec_in = os.path.join(base_path, "client", "temp", "test_dec_in.enc")
dec_out = os.path.join(base_path, "client", "temp", "test_dec_out.txt")
with open(dec_in, "wb") as f:
    f.write(base64.b64decode(enc_b64))

script_dec = os.path.join(base_path, "client", "encryption", "decrypt.sh")
res2 = subprocess.run(["bash", script_dec, priv_key, dec_in, dec_out], cwd=os.path.join(base_path, "client", "encryption"), capture_output=True, text=True)
print("Decrypt stdout:", res2.stdout)
print("Decrypt stderr:", res2.stderr)

if os.path.exists(dec_out):
    with open(dec_out, "r") as f:
        print("Decrypted:", f.read())
else:
    print("Decrypted file not found!")

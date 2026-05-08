import os
import subprocess

base_path = r"c:\Users\moust\Downloads\SecureShare-Main\SecureShare-Main"
script = os.path.join(base_path, "client", "encryption", "encrypt.sh")

# Let's create dummy files for testing
pub_key_path = os.path.join(base_path, "client", "temp", "dummy_pub.pem")
with open(pub_key_path, "w") as f: f.write("dummy")

file_path = os.path.join(base_path, "client", "temp", "dummy_in.txt")
with open(file_path, "w") as f: f.write("hello world")

temp_out = os.path.join(base_path, "client", "temp", "file_out.enc")

res = subprocess.run(["bash", script, pub_key_path, file_path, temp_out],
                     cwd=os.path.join(base_path, "client", "encryption"),
                     capture_output=True, text=True)

print("Return code:", res.returncode)
print("Stdout:", res.stdout)
print("Stderr:", res.stderr)

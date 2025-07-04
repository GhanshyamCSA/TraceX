import os
import zipfile
import tarfile

SAMPLE_DIR = "sample_data"

PUBLIC_IPV4 = "8.8.8.8"
PRIVATE_IPV4 = "192.168.1.1"
PUBLIC_IPV6 = "2001:4860:4860::8888"
PRIVATE_IPV6 = "fd00::1"


def create_text_file(path, lines):
    with open(path, "w") as f:
        for line in lines:
            f.write(line + "\n")


def create_sample_files():
    os.makedirs(SAMPLE_DIR, exist_ok=True)
    create_text_file(os.path.join(SAMPLE_DIR, "file1.txt"), [
        f"This is a public IPv4: {PUBLIC_IPV4}",
        f"This is a private IPv4: {PRIVATE_IPV4}",
        f"This is a public IPv6: {PUBLIC_IPV6}",
        f"This is a private IPv6: {PRIVATE_IPV6}",
        "No IP here."
    ])
    create_text_file(os.path.join(SAMPLE_DIR, "file2.log"), [
        f"Random text {PUBLIC_IPV4}",
        f"Another line {PUBLIC_IPV6}"
    ])
    subdir = os.path.join(SAMPLE_DIR, "subdir")
    os.makedirs(subdir, exist_ok=True)
    create_text_file(os.path.join(subdir, "file3.txt"), [
        f"IPv6 only: {PUBLIC_IPV6}",
        "No IPs here."
    ])
    zip_path = os.path.join(SAMPLE_DIR, "archive.zip")
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr("archived1.txt", f"{PUBLIC_IPV4}\n{PRIVATE_IPV4}")
        zf.writestr("archived2.txt", f"{PUBLIC_IPV6}\n{PRIVATE_IPV6}")
    tar_path = os.path.join(SAMPLE_DIR, "archive.tar.gz")
    with tarfile.open(tar_path, "w:gz") as tf:
        file_content = f"{PUBLIC_IPV4}\n{PRIVATE_IPV6}"
        temp_file = os.path.join(SAMPLE_DIR, "temp.txt")
        create_text_file(temp_file, [file_content])
        tf.add(temp_file, arcname="archived3.txt")
        os.remove(temp_file)

if __name__ == "__main__":
    create_sample_files()
    print(f"Sample data created in '{SAMPLE_DIR}' directory.") 
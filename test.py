import time
import requests
from ftplib import FTP
from urllib.parse import urlparse
import os
import argparse

def generate_test_file(path="test_upload.dat", size_mb=50):
    with open(path, "wb") as f:
        f.write(os.urandom(size_mb * 1024 * 1024))
    print(f"📦 Generated test file: {path} ({size_mb} MB)")

def ftp_upload_download(host, local_file="test_upload.dat", download_file="ftp_download.dat"):
    ftp_user = "parsltests"
    ftp_pass = "dodosaga1234."
    remote_filename = "benchmark_test.dat"

    print(f"\n🔼 FTP Upload to {host}/{remote_filename}")
    ftp = FTP(host)
    ftp.login(user=ftp_user, passwd=ftp_pass)
    start_upload = time.time()
    with open(local_file, "rb") as f:
        ftp.storbinary(f"STOR {remote_filename}", f)
    upload_time = time.time() - start_upload

    print(f"✅ Uploaded in {upload_time:.2f} seconds")

    print(f"⬇️ FTP Download from {host}/{remote_filename}")
    start_download = time.time()
    with open(download_file, "wb") as f:
        ftp.retrbinary(f"RETR {remote_filename}", f.write)
    download_time = time.time() - start_download
    ftp.quit()

    size = os.path.getsize(download_file)
    return upload_time, download_time, size

def http_upload_download(host, local_file="test_upload.dat", download_file="http_download.dat"):
    filename = "benchmark_test.dat"
    upload_url = f"http://{host}:8080/{filename}"
    download_url = upload_url

    print(f"\n🔼 HTTP Upload to {upload_url}")
    with open(local_file, "rb") as f:
        start_upload = time.time()
        r = requests.put(upload_url, data=f)
        upload_time = time.time() - start_upload
    print(f"✅ Uploaded in {upload_time:.2f} seconds (status: {r.status_code})")

    print(f"⬇️ HTTP Download from {download_url}")
    start_download = time.time()
    r = requests.get(download_url, stream=True)
    with open(download_file, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)
    download_time = time.time() - start_download
    size = os.path.getsize(download_file)
    return upload_time, download_time, size

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Benchmark FTP and HTTP upload/download speeds")
    parser.add_argument("--host", default="localhost", help="Hostname or IP of the test server")
    parser.add_argument("--size", type=int, default=50, help="Test file size in MB")
    args = parser.parse_args()

    test_file = "test_upload.dat"
    generate_test_file(test_file, size_mb=args.size)

    ftp_up, ftp_down, ftp_size = ftp_upload_download(args.host, local_file=test_file)
    http_up, http_down, http_size = http_upload_download(args.host, local_file=test_file)

    print("\n📊 Summary:")
    print(f"FTP Upload:    {ftp_up:.2f}")
    print(f"FTP Download speed:  {ftp_down:.2f}")
    print(f"HTTP Upload speed:   {http_up:.2f}")
    print(f"HTTP Download speed: {http_down:.2f}")

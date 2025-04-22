import time
import requests
from ftplib import FTP
from urllib.parse import urlparse
import os


def generate_test_file(path="test_upload.dat", size_mb=50):
    with open(path, "wb") as f:
        f.write(os.urandom(size_mb * 1024 * 1024))
    print(f"Generated test file: {path} ({size_mb} MB)")


def ftp_upload_download(url, local_file="test_upload.dat", download_file="ftp_download.dat"):
    parsed = urlparse(url)
    ftp_host = parsed.hostname
    ftp_user = parsed.username or "anonymous"
    ftp_pass = parsed.password or "anonymous@"
    ftp_path = parsed.path.strip("/") or os.path.basename(local_file)

    print(f"\n🔼 FTP Upload to {ftp_host}/{ftp_path}")
    ftp = FTP(ftp_host)
    ftp.login(user=ftp_user, passwd=ftp_pass)
    start_upload = time.time()
    with open(local_file, "rb") as f:
        ftp.storbinary(f"STOR {ftp_path}", f)
    upload_time = time.time() - start_upload

    print(f"✅ Uploaded in {upload_time:.2f} seconds")

    print(f"⬇️ FTP Download from {ftp_host}/{ftp_path}")
    start_download = time.time()
    with open(download_file, "wb") as f:
        ftp.retrbinary(f"RETR {ftp_path}", f.write)
    download_time = time.time() - start_download
    ftp.quit()

    size = os.path.getsize(download_file)
    return upload_time, download_time, size


def http_upload_download(upload_url, download_url, local_file="test_upload.dat", download_file="http_download.dat"):
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
    test_file = "test_upload.dat"
    generate_test_file(test_file, size_mb=50)

    # Update with your URLs
    ftp_url = "ftp://testuser:testpass@localhost/benchmark_test.dat"
    http_url_base = "http://localhost:8080/benchmark_test.dat"

    ftp_up, ftp_down, ftp_size = ftp_upload_download(
        ftp_url, local_file=test_file)
    http_up, http_down, http_size = http_upload_download(
        http_url_base, http_url_base, local_file=test_file)

    print("\n📊 Summary:")
    print(f"FTP Upload speed:   {ftp_size / 1024 / 1024 / ftp_up:.2f} MB/s")
    print(f"FTP Download speed: {ftp_size / 1024 / 1024 / ftp_down:.2f} MB/s")
    print(f"HTTP Upload speed:  {http_size / 1024 / 1024 / http_up:.2f} MB/s")
    print(
        f"HTTP Download speed:{http_size / 1024 / 1024 / http_down:.2f} MB/s")

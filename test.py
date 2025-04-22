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

def run_tests(host, size_mb, repeat):
    test_file = "test_upload.dat"
    generate_test_file(test_file, size_mb=size_mb)
    remote_filename = "benchmark_test.dat"
    
    csv_file = "benchmark_results.csv"
    with open(csv_file, "w", newline="") as csvfile:
        fieldnames = ["iteration", "ftp_upload", "ftp_download", "http_upload", "http_download"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        ftp_uploads, ftp_downloads = [], []
        http_uploads, http_downloads = [], []

        for i in range(1, repeat + 1):
            print(f"\n🔁 Iteration {i}/{repeat}")

            ftp_up, ftp_down, _ = ftp_upload_download(host, test_file, remote_filename, "ftp_download.dat")
            http_up, http_down, _ = http_upload_download(host, test_file, remote_filename, "http_download.dat")

            ftp_uploads.append(ftp_up)
            ftp_downloads.append(ftp_down)
            http_uploads.append(http_up)
            http_downloads.append(http_down)

            writer.writerow({
                "iteration": i,
                "ftp_upload": f"{ftp_up:.3f}",
                "ftp_download": f"{ftp_down:.3f}",
                "http_upload": f"{http_up:.3f}",
                "http_download": f"{http_down:.3f}"
            })

        print("\n📊 Averages over", repeat, "runs:")
        print(f"FTP Upload:   {sum(ftp_uploads)/repeat:.2f} s")
        print(f"FTP Download: {sum(ftp_downloads)/repeat:.2f} s")
        print(f"HTTP Upload:  {sum(http_uploads)/repeat:.2f} s")
        print(f"HTTP Download:{sum(http_downloads)/repeat:.2f} s")
        print(f"📁 Full results saved in {csv_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Benchmark FTP and HTTP upload/download speeds")
    parser.add_argument("--host", default="localhost", help="Hostname or IP of the test server")
    parser.add_argument("--size", type=int, default=50, help="Test file size in MB")
    parser.add_argument("--repeat", type=int, default=3, help="How many times to repeat the benchmark")
    args = parser.parse_args()

    run_tests(args.host, args.size, args.repeat)

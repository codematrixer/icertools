import os
import base64
import re
import shutil
import zipfile
import stat
import subprocess

from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes


def extract_uuid_from_certificate(certificate_content: str) -> str:
    """
    Get the fingerprint from the given base64-encoded X.509 certificate.

    Args:
        certificate_content (str): A base64-encoded string of the certificate.

    Returns:
        str: The fingerprint extracted from the certificate.

    Raises:
        ValueError: If the fingerprint cannot be extracted.

    """
    cer_content = base64.b64decode(certificate_content)

    # Use OpenSSL to extract the fingerprint from the certificate
    try:
        proc = subprocess.Popen(
            ['openssl', 'x509', '-noout', '-fingerprint'], 
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        stdout, stderr = proc.communicate(input=cer_content)
        stdout = stdout.decode()
    except subprocess.SubprocessError as e:
        raise RuntimeError("Failed to run openssl subprocess.") from e

    fingerprint_pattern = r'([0-9A-Fa-f]{2}:){19}[0-9A-Fa-f]{2}'
    match = re.search(fingerprint_pattern, stdout)

    if match:
        # Remove colons to format the fingerprint as a plain string
        return match.group(0).replace(':', '')
    else:
        error_msg = stderr.decode().strip() if stderr else 'No error message available.'
        raise ValueError(f"Fingerprint extraction failed: {error_msg}")


def extract_uuid_from_certificate_v2(certificate_content: str) -> str:
    """
    Get the fingerprint from the given base64-encoded X.509 certificate.

    Args:
        certificate_content (str): A base64-encoded string of the certificate.

    Returns:
        str: The fingerprint extracted from the certificate.

    Raises:
        ValueError: If the fingerprint cannot be extracted.

    """
    try:
        cer_content = base64.b64decode(certificate_content)

        cert = x509.load_der_x509_certificate(cer_content, default_backend())

        # Extract the fingerprint
        fingerprint = cert.fingerprint(hashes.SHA1())

        # Format the fingerprint as a colon-separated string
        fingerprint_hex = fingerprint.hex()
        formatted_fingerprint = ":".join(fingerprint_hex[i:i + 2].upper() for i in range(0, len(fingerprint_hex), 2))

        return formatted_fingerprint.replace(':', '')

    except Exception as e:
        raise ValueError(f"Fingerprint extraction failed: {e}")


def find_matching_local_certificate(cer_uuids: list) -> str:
    """
    Searches through all local certificates bound to the machine and finds
    a certificate suitable for code signing that matches the provided cer uuids.

    Args:
        uuid_list (list): A list of cer uuids to check against available certificates.

    Returns:
        str: The uuid of the matching certificate.

    Raises:
        RuntimeError: If no matching certificate is found.
    """
    command = ['security', 'find-identity', '-p', 'codesigning', '-v']
    try:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        stdout_decoded = stdout.decode()
        stderr_decoded = stderr.decode().strip()
    except subprocess.SubprocessError as e:
        raise RuntimeError(f"Failed to execute system command ({' '.join(command)}) for retrieving certificates: {e}")

    print("All available local certificates:", stdout_decoded)
    matched_uuid = None

    # Search for the first match where one of the UUIDs in the list appears in the certificates output
    for line in stdout_decoded.splitlines():
        for uuid in cer_uuids:
            if uuid and uuid in line:
                pattern = r'\d+\) [^"]*"([^"]+)"'
                match = re.search(pattern, line)
                if match:
                    matched_uuid = uuid
                    print(f"Matched a certificate: {match.group(0)}")
                    return matched_uuid

    if not matched_uuid:
        error_message = stderr_decoded or "No error message provided."
        raise RuntimeError(f"Failed to match any available certificate for signing: {error_message}")

    return matched_uuid


def zip_directory(res_dir, zip_file_path):
    with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for dirpath, dirnames, filenames in os.walk(res_dir):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                arcname = os.path.relpath(file_path, res_dir)
                zipf.write(file_path, arcname)


def unzip_file(zip_path: str, extract_to: str):

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
        print(f"Unzip {zip_path} to {extract_to}")

    # Iterate over the extracted files and directories, and set the execute permissions.
    for root, dirs, files in os.walk(extract_to):
        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            os.chmod(dir_path, os.stat(dir_path).st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
        for file_name in files:
            file_path = os.path.join(root, file_name)
            os.chmod(file_path, os.stat(file_path).st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)

    return extract_to


def remove_subdirectory(directory: str, subdirectory: str):
    subdirectory_path = os.path.join(directory, subdirectory)
    if os.path.exists(subdirectory_path):
        shutil.rmtree(subdirectory_path)


def remove_files_in_directory(directory: str, files: list):
    for file_name in files:
        file_path = os.path.join(directory, file_name)
        if os.path.exists(file_path):
            os.remove(file_path)


def find_executable_files(base_dir: str, maxdepth=None):
    executables = []
    for root, dirs, files in os.walk(base_dir):
        if maxdepth is not None and root.count(os.sep) - base_dir.count(os.sep) >= maxdepth:
            continue
        for name in files:
            path = os.path.join(root, name)
            if os.access(path, os.X_OK):  # Check if the file is executable
                executables.append(path)
    return executables
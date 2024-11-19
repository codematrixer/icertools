import time
import jwt
import requests
import json
from typing import List, Dict, Any

from requests import HTTPError
from cached_property import cached_property

from ._proto import HTTPResponse, CertificateType, ProfileType, CertificateInfo, BundleInfo, DeviceInfo


ALGORITHM = "RS256"
BASE_URL = 'https://api.appstoreconnect.apple.com/v1'


def dohttp(method: str, url, data: Dict[str, Any] = None, headers={}, timeout=15) -> HTTPResponse:
    try:
        print(f"Http request <method={method}, url={url}, data={data}>")

        _data = json.dumps(data) if data else None
        r = requests.request(method, url, data=_data, headers=headers, timeout=timeout)
        r.raise_for_status()
        response = HTTPResponse(r.content)

        time.sleep(1)   # apple api limit 1000/hour

        return response
    except requests.RequestException as e:
        raise HTTPError(f"HTTP request failed: {e}")


class Api:

    # refer: https://developer.apple.com/documentation/appstoreconnectapi

    def __init__(self, key_file, key_id, issuer_id, user_id):
        self.key_file = key_file
        self.key_id = key_id
        self.issuer_id = issuer_id
        self.user_id = user_id

    @property
    def _api_key(self):
        with open(self.key_file, 'r', encoding='utf-8') as file:
            return file.read()

    @property
    def _token(self):
        headers = {
            'alg': 'ES256',
            'kid': self.key_id,
            'typ': 'JWT'
        }
        payload = {
            'iss': self.issuer_id,
            'exp': time.time() + 60 * 10,
            'aud': 'appstoreconnect-v1'
        }
        token = jwt.encode(payload, self._api_key, headers=headers, algorithm=ALGORITHM)
        return token

    @cached_property
    def _headers(self):
        headers = {
            'Authorization': f"Bearer {self._token}",
            "Content-Type": "application/json"
        }
        return headers

    def list_devices(self) -> list:
        url = f'{BASE_URL}/devices?limit=200'
        response = dohttp("GET", url, headers=self._headers)
        data = response.json().get("data")
        return data

    def register_device(self, udid: str, name: str, platform="IOS"):
        url = f'{BASE_URL}/devices'
        data = {
            'data': {
                'attributes': {
                    'name': name,
                    'udid': udid,
                    'platform': platform
                },
                'type': 'devices'
            }
        }
        response = dohttp("POST", url, data=data, headers=self._headers)
        data = response.json()
        return data

    def list_bundle_ids(self) -> list:
        url = f'{BASE_URL}/bundleIds'
        response = dohttp("GET", url, headers=self._headers)
        data = response.json().get("data")
        return data

    def gete_bundleid_related_profile(self, profile_id):
        url = f"https://api.appstoreconnect.apple.com/v1/profiles/{profile_id}/bundleId"
        response = dohttp("GET", url, headers=self._headers)
        data = response.json().get("data")
        return data

    def create_bundle_id(self, name: str, bundle_id: str, platform="IOS"):
        url = f'{BASE_URL}/bundleIds'
        data = {
            'data': {
                'attributes': {
                    "name": name,
                    'identifier': bundle_id,
                    "seedId": self.user_id,
                    "platform": platform,
                },
                'type': 'bundleIds'
            }
        }
        response = dohttp("POST", url, data=data, headers=self._headers)
        data = response.json()
        return data

    def list_certificates(self) -> list:
        url = f'{BASE_URL}/certificates'
        response = dohttp("GET", url, headers=self._headers)
        data = response.json().get("data")
        return data

    def _validate_certificate_type(self, cert_type):
        try:
            certificate = CertificateType[cert_type]
            print(f"Validated certificate type: {certificate.name}")
        except KeyError:
            valid_types = ", ".join([type.name for type in CertificateType])
            raise ValueError(f"Invalid certificate type: {cert_type}. Please choose from {valid_types}")

    def _read_csr_content(self, path):
        with open(path, 'r', encoding='utf-8') as file:
            return file.read()

    def create_certificate(self, csr_path, cert_type="IOS_DEVELOPMENT"):
        """
        Create certificate

        Args:
            csr_path (str): the file 'CertificateSigningRequest.certSigningRequest' path
            cert_type (str): CertificateType

        """
        url = f'{BASE_URL}/certificates'
        self._validate_certificate_type(cert_type)
        data = {
            'data': {
                'attributes': {
                    'certificateType': cert_type,
                    'csrContent': self._read_csr_content(csr_path),
                },
                'type': 'certificates'
            }
        }
        response = dohttp("POST", url, data=data, headers=self._headers)
        data = response.json()
        return data

    def list_profiles(self) -> list:
        url = f'{BASE_URL}/profiles'
        response = dohttp("GET", url, headers=self._headers)
        data = response.json().get("data")
        return data

    def _validate_profile_type(self, profile_type):
        try:
            profile = ProfileType[profile_type]
            print(f"Validated profile type: {profile.name}")
        except KeyError:
            valid_types = ", ".join([type.name for type in ProfileType])
            raise ValueError(f"Invalid profile type: {profile_type}. Please choose from {valid_types}")

    def create_profile(self,
                       profile_name: str,
                       bundle_info: BundleInfo,
                       certificates: List[CertificateInfo],
                       devices: List[DeviceInfo],
                       profile_type="IOS_APP_DEVELOPMENT"):
        """
        Create profile

        Args:
            profile_name (str): Profile name
            bundle (BundleInfo): Select BundleInfo
            certificates (List[CertificateInfo]): Select List[certificate.json()]
            devices (List[DeviceInfo]): Select List[device.json()]
            profile_type (str): ProfileType

        """
        if len(certificates) == 0:
            raise Exception('Failed to reate profile, certificates is null')
        if len(devices) == 0:
            raise Exception('Failed to reate profile, devices is null')

        _bundle_info = bundle_info.json()
        _certificates = [cer.json() for cer in certificates]
        _devices = [d.json() for d in devices]
        data = {
            'data': {
                'attributes': {
                    'name': profile_name,
                    'profileType': profile_type
                },
                'relationships': {
                    'bundleId': {'data': _bundle_info},
                    'certificates': {'data': _certificates},
                    'devices': {'data': _devices}
                },
                'type': 'profiles'
            }
        }

        url = f'{BASE_URL}/profiles'
        response = dohttp("POST", url, headers=self._headers, data=data)
        data = response.json().get("data")
        return data

    def delete_profile(self, profile_id):
        url = f'{BASE_URL}/profiles/{profile_id}'
        dohttp("DELETE", url, headers=self._headers)
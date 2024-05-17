import json
from enum import Enum, auto


class Platform(Enum):
    IOS = auto()
    MAC_OS = auto()


class CertificateType(Enum):
    IOS_DEVELOPMENT = auto()
    IOS_DISTRIBUTION = auto()
    MAC_APP_DISTRIBUTION = auto()
    MAC_INSTALLER_DISTRIBUTION = auto()
    MAC_APP_DEVELOPMENT = auto()
    DEVELOPER_ID_KEXT = auto()
    DEVELOPER_ID_APPLICATION = auto()
    DEVELOPMENT = auto()
    DISTRIBUTION = auto()
    PASS_TYPE_ID = auto()
    PASS_TYPE_ID_WITH_NFC = auto()


class ProfileType(Enum):
    IOS_APP_DEVELOPMENT = auto()
    IOS_APP_STORE = auto()
    IOS_APP_ADHOC = auto()
    IOS_APP_INHOUSE = auto()
    MAC_APP_DEVELOPMENT = auto()
    MAC_APP_STORE = auto()
    MAC_APP_DIRECT = auto()
    TVOS_APP_DEVELOPMENT = auto()
    TVOS_APP_STORE = auto()
    TVOS_APP_ADHOC = auto()
    TVOS_APP_INHOUSE = auto()
    MAC_CATALYST_APP_DEVELOPMENT = auto()
    MAC_CATALYST_APP_STORE = auto()
    MAC_CATALYST_APP_DIRECT = auto()


class HTTPResponse:
    def __init__(self, content: bytes) -> None:
        self.content = content

    def json(self):
        return json.loads(self.content)

    @property
    def text(self):
        return self.content.decode("utf-8", errors="ignore")


class BaseInfo:
    def __init__(self, _id: str, _type: str) -> None:
        self._id = _id
        self._type = _type

    def json(self):
        return {
            "id": self._id,
            "type": self._type
        }


class CertificateInfo(BaseInfo):
    pass


class BundleInfo(BaseInfo):
    pass


class DeviceInfo(BaseInfo):
    pass


class WildCardProfileResult:
    def __init__(self, profile_id: str, bundle_info: BundleInfo) -> None:
        self.profile_id = profile_id
        self.bundle_info = bundle_info

    def json(self):
        return {
            "profile_id": self.profile_id,
            "bundle_info": self.bundle_info.json()
        }
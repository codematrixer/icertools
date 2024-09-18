# icertools

A pure Python 3 implementation for **iOS certificate management** and **IPA re-signing**, Don't need to login the https://developer.apple.com/account/resources/devices/list for related operations. The principle reference to https://www.jianshu.com/p/035ae1f1e563.

Before this tool, using a personal developer account to re-sign an IPA required logging into the Apple Developer Website (with a verification code), adding new devices, generating a profile file, exporting it, and then using some re-signing tools. It was quite cumbersome. Now, with this tool, you can complete the re-signing with just one API call, making it extremely efficient.


[中文](README.md)

# Requirements

- Python3.6+
- MacOS


# Features

- IPA re-signing
- Add registered devices
- Retrieve device list
- Retrieve certificate list
- Retrieve Bundle ID list
- Create Bundle ID
- Retrieve Profile list
- Create Profile
- Delete certificates


# Usage

## Auth
- You need to create a certificate on the https://developer.apple.com/account/resources/devices/list and install it on your computer (only once, no need to repeat).
- Refer to [API Authentication.md](/docs/Authentication.md) to obtain API authentication information: `key_file`, `key_id`, `issuer_id`, `user_id`.


## Code Example

```python3
import json
from icertools.api import Api
from icertools.resign import Resign

# Auth info
key_file = '/Users/xx/AuthKey_xxx.p8'  # replace with your key file path
key_id = "xxx"   # replace with your key id
issuer_id = "xxx"   # replace with your issuer id
user_id = "xxx"   # replace with your user id


api = Api(
    key_file=key_file,
    key_id=key_id,
    issuer_id=issuer_id,
    user_id=user_id)


# List Devices
data = api.list_devices()
print(json.dumps(data, indent=4))


# List Bundle ID
data = api.list_bundle_ids()
print(json.dumps(data, indent=4))


# Create Bundle ID
data = api.create_bundle_id("test", "*")
print(json.dumps(data, indent=4))


# List Certificates
data = api.list_certificates()
print(json.dumps(data, indent=4))


# Create Certificate
csr_path = "/Users/xx/CertificateSigningRequest.certSigningRequest"    # replace with your certSigningRequest path
data = api.create_certificate(csr_path)
print(json.dumps(data, indent=4))


# List Profiles
data = api.list_profiles()
print(json.dumps(data, indent=4))


# Delete Profile
api.delete_profile("8SX4Z2FBUL")


# Register Device
data = api.register_device("00008030-0004598921BB802E", "iPhone")
print(json.dumps(data, indent=4))


# Resign IPA
input_ipa_path = "/Users/develop/tmp/ios-test.ipa"
output_ipa_path = "/Users/develop/tmp/resgin/r-ios-test.ipa"
r = Resign(api, input_ipa_path, output_ipa_path)
r.resign_ipa()
```


# Refer to
- https://www.jianshu.com/p/035ae1f1e563
- https://github.com/Ponytech/appstoreconnectapi
- https://developer.apple.com/documentation/appstoreconnectapi
- https://developer.apple.com/documentation/appstoreconnectapi/creating_api_keys_for_app_store_connect_api
import json
from icertools.api import Api
from icertools.resign import Resign


if __name__ == '__main__':
    key_file = '/Users/xx/AuthKey_xxx.p8'  # replace with your key file path
    key_id = "xxx"   # replace with your key id
    issuer_id = "xxx"   # replace with your issuer id
    user_id = "xxx"   # replace with your user id

    api = Api(
        key_file=key_file,
        key_id=key_id,
        issuer_id=issuer_id,
        user_id=user_id)

    data = api.list_devices()
    print(json.dumps(data, indent=4))

    data = api.list_bundle_ids()
    print(json.dumps(data, indent=4))

    data = api.create_bundle_id("test", "*")
    print(json.dumps(data, indent=4))

    # data = api.register_device("00008030-0004598921BB802E", "iPhone")
    # print(json.dumps(data, indent=4))

    # data = api.list_certificates()
    # print(json.dumps(data, indent=4))

    # csr_path = "/Users/xx/CertificateSigningRequest.certSigningRequest"    # replace with your certSigningRequest path
    # data = api.create_certificate(csr_path)
    # print(json.dumps(data, indent=4))

    # data = api.list_profiles()
    # print(json.dumps(data, indent=4))

    # api.delete_profile("8SX4Z2FBUL")

    input_ipa_path = "/Users/develop/tmp/ios-test.ipa"
    output_ipa_path = "/Users/develop/tmp/resgin/r-ios-test.ipa"
    r = Resign(api, input_ipa_path, output_ipa_path)
    r.resign_ipa()
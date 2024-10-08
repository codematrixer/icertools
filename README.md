# icertools

纯Python3实现的**iOS证书管理**和**IPA重签名工具**，无需提前登录[苹果开发者网站](https://developer.apple.com/account/resources/devices/list) 进行相关操作。原理参考[XCode自动管理证书](https://www.jianshu.com/p/035ae1f1e563)


没有这个工具前, 使用个人开发者账号对IPA`重签`时，需要进入苹果开发者网站（输入验证码登录），添加新设备，然后生成profile文件, 然后导出profile文件, 再用一些重签名工具进行重签, 非常麻烦。 现在有了这个工具，只需调用一个API即可完成重签，非常之高效。

[English](README_EN.md)

# Requirements

- Python3.6+
- MacOS


# Features

- IPA重签名
- 添加注册设备
- 查找设备列表
- 查找证书列表
- 查找BundleId列表
- 创建BundleId
- 查找Profile列表
- 创建Profile
- 删除证书


# Usage

## Auth
- 需提前去[苹果开发者网站](https://developer.apple.com/account/resources/devices/list)创建一个证书，安装到电脑上（只用执行这一次，以后都不用）
- 参考 [API Authentication.md](/docs/Authentication.md) 获取API鉴权信息, `key_file`, `key_id`, `issuer_id`, `user_id`


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
- [Xcode自动管理证书](https://www.jianshu.com/p/035ae1f1e563)
- https://github.com/Ponytech/appstoreconnectapi
- https://developer.apple.com/documentation/appstoreconnectapi
- https://developer.apple.com/documentation/appstoreconnectapi/creating_api_keys_for_app_store_connect_api
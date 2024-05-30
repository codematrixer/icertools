# icertools

纯Python3实现的**iOS证书管理**和**IPA重签名工具**，无需登录[苹果开发者网站](https://developer.apple.com/account/resources/devices/list) 进行任何操作，原理参考自[XCode自动管理证书](https://www.jianshu.com/p/035ae1f1e563)

**使用场景**

没有这个工具前, 使用个人开发者账号对IPA重签时，需要先登录苹果开发者网站，添加新设备，然后生成profile文件, 然后导出profile文件, 再用一些重签名工具进行重签, 非常麻烦。 现在有了这个工具，只需调用一个API即可完成重签，非常之高效。

在iOS自动化工具WDA的打包场景非常实用。


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
## 前置步骤
- 需提前去[苹果开发者网站](https://developer.apple.com/account/resources/devices/list)创建一个证书，安装到电脑上（只用执行这一次，以后都不用）
- 参考 [API Authentication.md](/docs/Authentication.md) 获取API鉴权信息, `key_file`, `key_id`, `issuer_id`, `user_id`

## 代码示例

```python3
import json
from icertools.api import Api
from icertools.resign import Resign

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

# data = api.create_bundle_id("test", "*")
# print(json.dumps(data, indent=4))

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

# 重签名
input_ipa_path = "/Users/develop/tmp/ios-test.ipa"
output_ipa_path = "/Users/develop/tmp/resgin/r-ios-test.ipa"
r = Resign(api, input_ipa_path, output_ipa_path)
r.resign_ipa()
```


# TODO
支持命令行
```bash
icertools devices --add --name xx --udid xxx
icertools cert --list
icertools cert --add
icertools cert --delete
icertools resign --app your/ipa/path --output your/output/path
```

# 参考文档
- [Xcode自动管理证书](https://www.jianshu.com/p/035ae1f1e563)
- https://github.com/Ponytech/appstoreconnectapi
- https://developer.apple.com/documentation/appstoreconnectapi
- https://developer.apple.com/documentation/appstoreconnectapi/creating_api_keys_for_app_store_connect_api
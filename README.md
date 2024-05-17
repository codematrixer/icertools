# icertools
纯Python3实现的iOS证书管理和IPA重签名工具，无需在[苹果开发者网站](https://developer.apple.com/account/resources/devices/list) 进行操作, 免去了登录, 验证码等步骤。

举一个场景: 没有这个工具前, 对ipa使用个人开发者账号重签时，需要先登录苹果开发者网站，添加新设备，然后生成profile文件, 再用一些重签名工具进行重签。 现在有了这个工具，只需调用一个API即可完成重签。

在iOS自动化工具WDA的打包场景非常实用。


# Requirements

- Python3.6+


# Features

- IPA重签名
- 添加设备
- 查找证书列表
- 查找BundleId列表
- 查找设备列表
- 查找Profile列表
- 创建Profile
- 删除证书


# Usage
参考[文档](https://developer.apple.com/documentation/appstoreconnectapi/creating_api_keys_for_app_store_connect_api) 获取`API KEY`, 使用`key_file`, `key_id`, `issuer_id`创建 API instance

```python3
import json
from icertools.api import Api
from icertools.resign import Resign

api = Api(
    key_file=key_file,
    key_id=key_id,
    issuer_id=issuer_id)

data = api.list_bundle_ids()
print(json.dumps(data, indent=4))

data = api.list_devices()
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
- https://github.com/Ponytech/appstoreconnectapi
- https://developer.apple.com/documentation/appstoreconnectapi
- https://developer.apple.com/documentation/appstoreconnectapi/creating_api_keys_for_app_store_connect_api
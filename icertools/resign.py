import os
import base64
import shutil
import subprocess
from typing import List, Tuple

from .api import Api
from ._utils import *
from ._proto import *


class Resign:
    def __init__(self, api: Api, input_ipa_path: str, output_ipa_path) -> None:
        self.api = api
        self.input_ipa_path = input_ipa_path
        self.output_ipa_path = output_ipa_path

        self.workspace = None
        self._tmp_path = None
        self._init_workspace_path()

    def _init_workspace_path(self):
        # Check input path
        if not os.path.exists(self.input_ipa_path):
            raise RuntimeError(f"Ipa file not exists.<{self.input_ipa_path}>")

        # Init output dir
        output_dir = os.path.dirname(self.output_ipa_path)
        if not output_dir:
            raise RuntimeError(f"Invaild output path.<{self.output_ipa_path}>")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)

        self.workspace = output_dir
        self._tmp_path = os.path.join(self.workspace, "_tmp")

    def _find_wildcard_profile_and_bundle(self) -> WildCardProfileResult:
        """
        Searches the current account for a profile with an identifier of "*".
        Retrieves the bundle through the profile, then obtains the identifier.
        """
        print("list profiles...")
        profiles = self.api.list_profiles()
        profile_id = None
        wildcard_bundle_info: BundleInfo = None

        for profile in profiles:
            profile_id = profile.get("id")
            bundleid_data = self.api.gete_bundleid_related_profile(profile_id)

            identifier = bundleid_data['attributes']['identifier']
            if '*' == identifier:
                print(f"Match identifier == '*' profile: <{profile_id}>")
                wildcard_bundle_info = BundleInfo(_id=bundleid_data['id'], _type=bundleid_data['type'])
                return WildCardProfileResult(profile_id, wildcard_bundle_info)

        if wildcard_bundle_info is None:
            print('No profile matched identifier == "*"!')

        return WildCardProfileResult(None, None)

    def _get_or_create_wildcard_bundle(self) -> BundleInfo:
        """
        Search the current account for a bundle with an identifier of "*".
        If not found, create one.

        Returns:
            BundleInfo: The bundle information if a bundle is found or created.

        Raises:
            RuntimeError: If no bundle is found and creation fails.
        """
        bundles = self.api.list_bundle_ids()

        for bundle in bundles:
            identifier = bundle['attributes']['identifier']
            if identifier == '*':
                print(f"Matched identifier == '*' bundle: <{bundle['id']}>")
                return BundleInfo(_id=bundle['id'], _type=bundle['type'])

        print('No bundle_id matched identifier == "*"!, so Create one')
        try:
            self.api.create_bundle_id(name="API Wildcard", bundle_id="*")
        except Exception as e:
            print('Failed to create bundle_id: identifier == "*"')
            raise RuntimeError('No bundle matched identifier == "*" and failed to create one!')

    def _get_all_certificates_info(self) -> Tuple[List[str], List[CertificateInfo]]:
        """
        Retrieves all certificates' UUIDs and info.
        Returns a tuple containing a list of UUIDs and a list of CertificateInfo objects.

        Raises:
            RuntimeError: If there are no valid certificates in the current account.
        """
        certificates = self.api.list_certificates()
        if not certificates:
            raise RuntimeError("No valid certificates found in the current account!")

        cer_uuids = []
        cer_infos = []
        for certificate in certificates:
            certificateContent = certificate['attributes']['certificateContent']
            uuid = extract_uuid_from_certificate_v2(certificateContent)
            cer_uuids.append(uuid)
            certificate_info = CertificateInfo(
                _id=certificate['id'],
                _type=certificate['type']
            )
            cer_infos.append(certificate_info)

        return cer_uuids, cer_infos

    def _get_all_device_infos(self) -> List[DeviceInfo]:
        """
        Retrieves all devices info.

        Returns:
            List[DeviceInfo]: deivces info.
        """
        devices = self.api.list_devices()
        devices_infos: List[DeviceInfo] = []
        for device in devices:
            info = DeviceInfo(_id=device['id'], _type=device['type'])
            devices_infos.append(info)

        return devices_infos

    def _create_wildcard_profile(
        self,
        wildcard_bundle_info: BundleInfo,
        certificate_infos: List[CertificateInfo],
        device_infos: List[DeviceInfo],
        output_dir: str
    ) -> str:
        """
        Creates a new profile with identifier == "*".

        Args:
            wildcard_cer_info (BundleInfo): Information about the matched wildcard.
            certificate_infos (List[CertificateInfo]): Information about the certificates to be bound to the profile.
            device_infos (List[DeviceInfo]): Information about the devices to be bound to the profile.
            workspace (str): Directory for temporary workspace storage.

        Returns:
            str: Path where the profile was saved.
        """
        wildcard_profile = self.api.create_profile("wildcard-auto", wildcard_bundle_info, certificate_infos, device_infos)
        profile_content = wildcard_profile['attributes']['profileContent']
        profile_name = wildcard_profile['attributes']['name']

        profile_path = os.path.join(output_dir, f"{profile_name}.mobileprovision")
        with open(profile_path, 'wb') as file:
            file.write(base64.b64decode(profile_content))

        print(f"Profile saved successfully: {profile_path}")
        return profile_path

    def _gen_entitlements_plist(self, profile_path: str, plist_dir: str) -> str:
        """
        Generates entitlements plist from the profile path.

        Args:
            profile_path (str): Path to the profile.
            plist_dir (str): Directory to save the generated plist.

        Returns:
            str: Path to the generated entitlements plist.
        """
        embedded_plist_path: str = os.path.join(plist_dir, 'embedded.plist')
        entitlements_plist_path: str = os.path.join(plist_dir, 'entitlements.plist')

        # Run 'security cms -D -i' command to extract the plist content
        subprocess.run(
            ["security", "cms", "-D", "-i", profile_path],
            stdout=open(embedded_plist_path, 'w'),
            check=True
        )

        # Run 'PlistBuddy' command to extract entitlements
        subprocess.run(
            ["/usr/libexec/PlistBuddy", "-x", "-c", "Print:Entitlements", embedded_plist_path],
            stdout=open(entitlements_plist_path, 'w'),
            check=True
        )

        return entitlements_plist_path

    def _codesign_file(self, app_dir: str, cer_uuid: str, entitlements_plist_path: str) -> None:
        """
        Codesigns the specified app directory.

        Args:
            app_dir (str): Directory of the app to be codesigned.
            cer_uuid (str): UUID of the certificate.
            entitlements_plist_path (str): Path to the entitlements plist.
        """
        frameworks_dir: str = os.path.join(app_dir, "Frameworks")
        plugIns_dir: str = os.path.join(app_dir, "PlugIns")

        _apps: List[str] = find_executable_files(app_dir, maxdepth=1)
        _frameworks: List[str] = find_executable_files(frameworks_dir) if os.path.exists(frameworks_dir) else []
        _plugIns: List[str] = find_executable_files(plugIns_dir) if os.path.exists(plugIns_dir) else []

        for item in _frameworks + _plugIns + _apps:
            subprocess.run([
                "codesign", "-f", "-s", cer_uuid,
                f"--entitlements={entitlements_plist_path}",
                item
            ], check=True)

    def _pack_ipa(self, unzipped_ipa_dir: str, profile_path: str, entitlements_plist_path: str, cer_uuid: str):
        """
        Re-signs the unpacked IPA file and compresses it back into a new IPA file.

        Args:
            unzipped_ipa_dir (BundleInfo): Information about the matched wildcard.
            unzipped_ipa_dir (str): Path to the unpacked original IPA file
            profile_path (str): Path to the newly generated profile file
            entitlements_plist_path (str): Path to the entitlements plist file
            cer_uuid (str): UUID of the certificate for re-signing the IPA file

        Returns:
        """

        def __get_app_directory() -> str:
            """
            Gets the directory of the .app file inside the unzipped IPA directory.
            """
            payload_dir = os.path.join(unzipped_ipa_dir, 'Payload')
            if not os.path.exists(payload_dir):
                raise RuntimeError("Payload directory does not exist in the unzipped IPA!")

            app_dirs = [os.path.join(payload_dir, f) for f in os.listdir(payload_dir) if f.endswith('.app')]

            if not app_dirs:
                raise RuntimeError(".app directory not found!")
            return app_dirs[0]

        app_dir = __get_app_directory()   # eg. ~/develop/icertools/_tmp/_tmp/Payload/ios-wda.app

        app_profile = f'{app_dir}/embedded.mobileprovision'
        if os.path.exists(app_profile):
            os.remove(app_profile)

        shutil.copy(profile_path, app_profile)

        print("Codesigning app file...")
        self._codesign_file(app_dir, cer_uuid, entitlements_plist_path)

        print("Zipping app file to IPA...")
        zip_directory(unzipped_ipa_dir, self.output_ipa_path)

    def resign_ipa(self):
        """
        Resigns the IPA file by performing the following steps:
        1. Extracts the contents of the IPA file to a temporary directory.
        2. Searches for a wildcard profile and bundle.
        3. If a profile is found, deletes it; otherwise, searches for a wildcard bundle.
        4. Retrieves information about all certificates and finds a matching local certificate.
        5. Retrieves information about all devices.
        6. Creates a wildcard profile using the found or generated bundle, certificates, and devices.
        7. Generates entitlements plist based on the created profile.
        8. Raises a RuntimeError if entitlements.plist creation fails.
        9. Packs the IPA file using the unzipped contents, created profile, entitlements plist, and local certificate.
        10. Prints the path to the output IPA file once the process is done.
        """

        extract_to = os.path.join(self._tmp_path, '__tmp')
        if os.path.exists(extract_to):
            shutil.rmtree(extract_to)

        unzipped_ipa_dir = unzip_file(self.input_ipa_path, extract_to)  # eg. ~/develop/icertools/_tmp/__tmp

        print("Find wildcard profile and bundle")
        result: WildCardProfileResult = self._find_wildcard_profile_and_bundle()
        profile_id = result.profile_id
        wildcard_bundle_info = result.bundle_info

        if profile_id:
            print(f"Delete profile: {profile_id}")
            self.api.delete_profile(profile_id)
        else:
            wildcard_bundle_info: BundleInfo = self._get_or_create_wildcard_bundle()

        cer_uuids, cer_infos = self._get_all_certificates_info()
        local_cer_uuid = find_matching_local_certificate(cer_uuids)   # eg. B87C5FAC4EX30EE46...BE79BE2DE916E8503F4X

        devices_info: List[DeviceInfo] = self._get_all_device_infos()
        print("Create wildcard profile...")
        profile_path = self._create_wildcard_profile(wildcard_bundle_info, cer_infos, devices_info, self._tmp_path)

        print("Generate entitlements plist...")
        entitlements_plist_path = self._gen_entitlements_plist(profile_path, self._tmp_path)

        if not os.path.exists(entitlements_plist_path):
            raise RuntimeError("Faild to created entitlements.plist!!")

        self._pack_ipa(unzipped_ipa_dir, profile_path, entitlements_plist_path, local_cer_uuid)
        print(f"Done: output IPA: {self.output_ipa_path}")
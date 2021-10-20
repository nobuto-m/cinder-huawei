# Copyright 2016 Canonical Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import absolute_import
from __future__ import print_function

import charmhelpers

import charm.openstack.cinder_huawei as cinder_huawei

import charms_openstack.test_utils as test_utils


class TestCinderHuaweiCharm(test_utils.PatchHelper):
    def _patch_config_and_charm(self, config):
        self.patch_object(charmhelpers.core.hookenv, "config")

        def cf(key=None):
            if key is not None:
                return config[key]
            return config

        self.config.side_effect = cf
        c = cinder_huawei.CinderHuaweiCharm()
        return c

    def test_cinder_base(self):
        charm = self._patch_config_and_charm({})
        self.assertEqual(charm.name, "cinder_huawei")
        self.assertEqual(charm.version_package, "cinder-common")
        self.assertEqual(charm.packages, ["", "multipath-tools", "sysfsutils"])

    def test_cinder_configuration(self):
        self.patch_object(charmhelpers.core.hookenv, "service_name")
        self.service_name.return_value = "cinder-myapp-name"
        charm = self._patch_config_and_charm(
            {
                "volume-backend-name": "my_backend_name",
                "protocol": "iscsi",
                "rest-url": "https://my.example.com:8088/deviceManager/rest/",
                "username": "myuser",
                "password": "mypassword",
            }
        )
        config = charm.cinder_configuration()
        self.assertEqual(
            config,
            [
                ("volume_backend_name", "my_backend_name"),
                (
                    "volume_driver",
                    "cinder.volume.drivers.huawei.huawei_driver.HuaweiISCSIDriver",  # noqa
                ),
                (
                    "cinder_huawei_conf_file",
                    "/etc/cinder/huawei/cinder-myapp-name.xml",
                ),
            ],
        )

    def test_cinder_configuration_missing_mandatory_config(self):
        charm = self._patch_config_and_charm(
            {
                "volume-backend-name": "my_backend_name",
                "protocol": "iscsi",
                "rest-url": "https://my.example.com:8088/deviceManager/rest/",
                "username": "myuser",
                "password": None,
            }
        )
        config = charm.cinder_configuration()
        self.assertEqual(config, None)

    def test_cinder_configuration_fc(self):
        self.patch_object(charmhelpers.core.hookenv, "service_name")
        self.service_name.return_value = "cinder-myapp-name"
        charm = self._patch_config_and_charm(
            {
                "volume-backend-name": "my_backend_name",
                "protocol": "fc",
                "rest-url": "https://my.example.com:8088/deviceManager/rest/",
                "username": "myuser",
                "password": "mypassword",
            }
        )
        config = charm.cinder_configuration()
        self.assertEqual(
            config,
            [
                ("volume_backend_name", "my_backend_name"),
                (
                    "volume_driver",
                    "cinder.volume.drivers.huawei.huawei_driver.HuaweiFCDriver",  # noqa
                ),
                (
                    "cinder_huawei_conf_file",
                    "/etc/cinder/huawei/cinder-myapp-name.xml",
                ),
            ],
        )

    def test_cinder_configuration_no_explicit_backend_name(self):
        self.patch_object(charmhelpers.core.hookenv, "service_name")
        self.service_name.return_value = "cinder-myapp-name"
        charm = self._patch_config_and_charm(
            {
                "volume-backend-name": None,
                "protocol": "iscsi",
                "rest-url": "https://my.example.com:8088/deviceManager/rest/",
                "username": "myuser",
                "password": "mypassword",
            }
        )
        config = charm.cinder_configuration()
        self.assertEqual(
            config,
            [
                ("volume_backend_name", "cinder-myapp-name"),
                (
                    "volume_driver",
                    "cinder.volume.drivers.huawei.huawei_driver.HuaweiISCSIDriver",  # noqa
                ),
                (
                    "cinder_huawei_conf_file",
                    "/etc/cinder/huawei/cinder-myapp-name.xml",
                ),
            ],
        )

    def test_cinder_configuration_use_multipath(self):
        self.patch_object(charmhelpers.core.hookenv, "service_name")
        self.service_name.return_value = "cinder-myapp-name"
        charm = self._patch_config_and_charm(
            {
                "volume-backend-name": "my_backend_name",
                "protocol": "iscsi",
                "rest-url": "https://my.example.com:8088/deviceManager/rest/",
                "username": "myuser",
                "password": "mypassword",
                "use-multipath": True,
            }
        )
        config = charm.cinder_configuration()
        self.assertEqual(
            config,
            [
                ("volume_backend_name", "my_backend_name"),
                (
                    "volume_driver",
                    "cinder.volume.drivers.huawei.huawei_driver.HuaweiISCSIDriver",  # noqa
                ),
                (
                    "cinder_huawei_conf_file",
                    "/etc/cinder/huawei/cinder-myapp-name.xml",
                ),
                ("use_multipath_for_image_xfer", True),
                ("enforce_multipath_for_image_xfer", True),
            ],
        )

import os

import charmhelpers.core.hookenv as ch_hookenv  # noqa
import charmhelpers.core.host as ch_host
import charmhelpers.core.templating
import charms_openstack.charm

charms_openstack.charm.use_defaults("charm.default-select-release")

MULTIPATH_PACKAGES = [
    "multipath-tools",  # installed by default for disco+
    "sysfsutils",  # LP: #1947063
]

HUAWEI_DRIVER_ISCSI = "{}.{}".format(
    "cinder.volume.drivers.huawei.huawei_driver", "HuaweiISCSIDriver"
)
HUAWEI_DRIVER_FC = "{}.{}".format(
    "cinder.volume.drivers.huawei.huawei_driver", "HuaweiFCDriver"
)


class CinderHuaweiCharm(charms_openstack.charm.CinderStoragePluginCharm):

    # The name of the charm
    name = "cinder_huawei"

    # Package to determine application version. Use "cinder-common" when
    # the driver is in-tree of Cinder upstream.
    version_package = "cinder-common"

    # Package to determine OpenStack release name
    release_pkg = "cinder-common"

    # this is the first release in which this charm works
    release = "ussuri"

    # List of packages to install
    packages = [""]

    # make sure multipath related packages are installed
    packages.extend(MULTIPATH_PACKAGES)

    stateless = True

    # Specify any config that the user *must* set.
    mandatory_config = [
        "protocol",
        "rest-url",
        "username",
        "password",
        "storage-pool",
    ]

    def cinder_configuration(self):
        mandatory_config_values = map(self.config.get, self.mandatory_config)
        if not all(list(mandatory_config_values)):
            return []

        protocol = self.config.get("protocol").lower()
        if protocol == "iscsi":
            volume_driver = HUAWEI_DRIVER_ISCSI
        elif protocol == "fc":
            volume_driver = HUAWEI_DRIVER_FC

        service_name = ch_hookenv.service_name()
        if self.config.get("volume-backend-name"):
            volume_backend_name = self.config.get("volume-backend-name")
        else:
            volume_backend_name = service_name

        huawei_conf_file = os.path.join(
            "/etc/cinder/huawei", "{}.xml".format(service_name)
        )
        self._render_huawei_conf_file(huawei_conf_file)

        driver_options = [
            ("volume_backend_name", volume_backend_name),
            ("volume_driver", volume_driver),
            ("cinder_huawei_conf_file", huawei_conf_file),
        ]

        if self.config.get("use-multipath"):
            driver_options.extend(
                [
                    ("use_multipath_for_image_xfer", True),
                    ("enforce_multipath_for_image_xfer", True),
                ]
            )

        return driver_options

    def _render_huawei_conf_file(self, target_file):
        owner, group = "root", "cinder"
        ch_host.mkdir(
            os.path.dirname(target_file),
            owner=owner,
            group=group,
            perms=0o750,
        )

        charmhelpers.core.templating.render(
            source="cinder_huawei_conf.xml",
            target=target_file,
            context=self.config,
            owner=owner,
            group=group,
            perms=0o640,
        )

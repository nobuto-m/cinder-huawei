Huawei Storage Backend for Cinder
---------------------------------

Overview
========

This charm provides a Huawei storage backend for use with the Cinder
charm.

Please refer to [Huawei storage driver's documentation in Cinder
project](https://docs.openstack.org/cinder/latest/configuration/block-storage/drivers/huawei-storage-driver.html)
for supported models and functionalities.

To use:

    juju deploy cinder
    juju deploy cinder-huawei
    juju add-relation cinder-huawei cinder

Configuration
=============

See config.yaml for details of configuration options.

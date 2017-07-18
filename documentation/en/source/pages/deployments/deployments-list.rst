.. Copyright (c) 2007-2016 UShareSoft, All rights reserved

.. _deployments-list:

Listing the Deployments
=======================

You can check all your deployments by running ``deploy list``:

.. code-block:: shell

	$ hammr deploy list
	Getting all deployments for [root] ...
        Deployments:
        +---------------------+---------------+----------------+-----------+---------------+---------+
        |   Deployment name   | Deployment ID |    Hostname    |  Region   |  Source used  | Status  |
        +=====================+===============+================+===========+===============+=========+
        | myappliance-deploy  | zybkrv99m0    | 54.154.148.149 | eu-west-1 | Stack ID: 104 | running |
        +---------------------+---------------+----------------+-----------+---------------+---------+
        | myscan-deploy       | jjfn9ev5m3    | 38.253.202.47  | eu-west-1 | Scan ID: 1    | running |
        +---------------------+---------------+----------------+-----------+---------------+---------+
        | wordpress           | csb02f4fty    | None           | None      | None          | on-fire |
        +---------------------+---------------+----------------+-----------+---------------+---------+

        Found 3 deployments

The table lists the deployment ID, which you will need to terminate the instance, the hostname, region, source used and the status.

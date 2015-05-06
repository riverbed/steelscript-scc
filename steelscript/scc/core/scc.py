# Copyright (c) 2014 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

import os

from sleepwalker.service import Service
from sleepwalker.connection import Connection
from reschema.servicedef import ServiceDef


class SCC(object):
    """The SCC class is the main interface to interact with a SteelCentral
    Controller.
    """
    def __init__(self, host):
        """Use sleepwalker Service API and reschema ServiceDef class
        to access resources in SCC.stats API.

        :param host: string, hostname or IP address of SCC, need to provide
            URL scheme, http or https, i.e. http://hostname.domain.com
        """
        dir = os.path.dirname(__file__)
        service_file = os.path.join(dir, 'servicedef/service.yml')
        svc_def = ServiceDef.create_from_file(service_file)
        conn = Connection(host)
        self._svc = Service(svc_def, host, connection=conn)

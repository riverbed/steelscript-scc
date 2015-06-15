# Copyright (c) 2015 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

"""
Provides sleepwalker ConnectionManager that doesn't verify SSL for
appliances with self signed certificates.

"""

from steelscript.common.service import Service

import sleepwalker


class ServerConnectionHook(sleepwalker.connection.ConnectionHook):

    _service = None

    def connect(self, host, auth):
        svc = Service(self._service, host=host, auth=auth)
        return svc.conn

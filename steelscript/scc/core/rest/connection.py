# Copyright (c) 2015 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.


""" 
Provides sleepwalker ConnectionManager that doesn't verify SSL for
appliances with self signed certificates.

"""

from __future__ import (unicode_literals, print_function, division,
                        absolute_import)

import sleepwalker


class UnVerifiedSSLConnectionHook(sleepwalker.connection.ConnectionHook):
    """ Connection hook for creating unverified SSL connections
    Always turn off verify because the SSL certs don't verify by default.
    """

    def connect(self, host, auth):
        connection = sleepwalker.Connection(host, auth=auth)
        connection.conn.verify = False
        return connection

# Copyright (c) 2015 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

"""
This module defines abstraction of classes and methods dealing with
a RESTful server, including instantiating connection manager, service_def
manager, service manager and requesting data from the Restful server.
"""

import importlib

from steelscript.scc.core.rest.auth import RvbdOAuth2
from steelscript.common.service import OAuth
from steelscript.common.service import Service
from steelscript.common.datastructures import Singleton


class SleepWalkerServerBase(object):
    """Base class for interacting with a REST server. Should only be
    inherited to use methods, such as initialization and requesting
    data from the REST server.
    """

    def __init__(self, host, auth):
        self.host = host
        self.auth = auth

        mod = importlib.import_module(self._svcmgr_cls_module)

        _svcmgr_cls = mod.__dict__[self._svcmgr_cls_name]
        self._svcmgr = _svcmgr_cls()

    def request(self, service, resource, link, criteria=None):
        """Send request to the REST Server and expects a response
        immediately.

        :param service: string, name of the service, e.g. cmc.stats
        :param resource: string, name of the resource to query
        :param link: string, name of the link method to query
        :param criteria: dict, criteria fields to query
        """
        svc = self._svcmgr.find_by_name(host=self.host, name=service,
                                        auth=self.auth, version=self.version)
        data_rep = svc.bind(resource)
        resp = data_rep.execute(link, criteria)
        try:
            return resp.data['response_data']
        except:
            return resp.data
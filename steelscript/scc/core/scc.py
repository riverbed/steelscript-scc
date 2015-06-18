# Copyright (c) 2015 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

import os
import logging

from sleepwalker.service import ServiceManager
from sleepwalker.connection import ConnectionManager
from steelscript.common.datastructures import Singleton
from steelscript.common.service import Service


import reschema.servicedef as ServiceDef
import sleepwalker

logger = logging.getLogger(__name__)

SERVICE_ID = 'https://support.riverbed.com/apis/{0}/{1}'


class SCCException(Exception):
    pass


class ServiceDefLoader(ServiceDef.ServiceDefLoadHook):
    """This class serves as the custom hook for service manager."""

    def find_by_id(self, id):
        """
        This method generates service schema corresponding to the id

        :param id: Service id specified in service definition file
        """
        # Convert id from http format to file name first
        service = id.rstrip('/').rsplit('/', 2)[1]
        current_dir = os.path.dirname(__file__)
        filename = os.path.join(current_dir,
                                'servicedef/{0}.yml'.format(service))
        if os.path.isfile(filename):
            return ServiceDef.ServiceDef.create_from_file(filename)
        else:
            raise ValueError("Invalid id: %s" % id)

    def find_by_name(self, name, version, provider):
        """
        Method used to discover service from service map based upon
        service name, version and service provider

        :param name: Name of the service
        :param version: Version of service
        :param provider: Name of service provider
        """
        assert(provider == 'riverbed')
        service_id = SERVICE_ID.format(name, version)
        return self.find_by_id(service_id)


class SCCServerConnectionHook(sleepwalker.connection.ConnectionHook):

    def connect(self, host, auth):
        svc = Service("scc", host=host, auth=auth)
        return svc.conn


class SCCServiceManager(ServiceManager):
    """This class encapsulates the storage of SCC services
    and connection with the SCC device.
    """
    __metaclass__ = Singleton

    def __new__(cls):
        # Construct service loader
        svcdef_loader = ServiceDefLoader()

        # Derive service def manager
        svcdef_manager = ServiceDef.ServiceDefManager()
        svcdef_manager.add_load_hook(svcdef_loader)

        # Obtain connection manager
        conn_manager = ConnectionManager()
        conn_manager.add_conn_hook(SCCServerConnectionHook())

        # Initialize the instance of service manager
        logger.info("Initializing service manager")
        return ServiceManager(servicedef_manager=svcdef_manager,
                              connection_manager=conn_manager)


class SCC(object):
    """This class is the main interface to interact with a SteelCentral
    Controller.
    """

    def __init__(self, host, port=None, auth=None):
        svcmgr = SCCServiceManager()
        self.stats = svcmgr.find_by_name(host=host, name='cmc.stats',
                                         version='1.0', auth=auth)
        self.appliance = svcmgr.find_by_name(
            host=host, name='cmc.appliance_inventory', version='1.0',
            auth=auth)

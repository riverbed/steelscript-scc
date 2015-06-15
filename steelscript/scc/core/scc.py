# Copyright (c) 2015 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

import os
import logging

from sleepwalker.service import ServiceManager
from sleepwalker.connection import ConnectionManager
from steelscript.scc.core.rest.connection import ServerConnectionHook
from steelscript.scc.core.rest.server import SleepWalkerServerBase
from steelscript.common.datastructures import Singleton

import reschema.servicedef as ServiceDef

logger = logging.getLogger(__name__)

SERVICE_NAMES = ['cmc.appliance_inventory', 'cmc.stats']

VERSION = '1.0'

SERVICE_ID = 'https://support.riverbed.com/apis/{0}/{1}'


def get_filename(service):
    current_dir = os.path.dirname(__file__)
    service_file = os.path.join(current_dir,
                                'servicedef/{0}.yml'.format(service))
    return service_file


class SCCException(Exception):
    pass


class ServiceDefLoader(ServiceDef.ServiceDefLoadHook):
    """This class serves as the custom hook for service manager."""

    service_map = {}

    @classmethod
    def register_servicedef(cls, id, filename):
        """
        Adds service into the service map

        :param cls: Service Def hook class name
        :param id: Service id specified in service definition file
        :param filename: File name of service definition file
        """
        cls.service_map[id] = filename

    def find_by_id(self, id_):
        """
        This method finds service schema by id from the service map

        :param id_: Service id specified in service definition file
        """
        if id_ in self.service_map:
            return ServiceDef.ServiceDef.create_from_file(
                self.service_map[id_])
        else:
            raise KeyError("Invalid id: %s" % id_)

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


class SCCServerConnectionHook(ServerConnectionHook):
    _service = 'scc'


class SCCServiceManager(ServiceManager):
    """This class encapsulates the storage of SCC services
    and connection with the SCC device.
    """
    __metaclass__ = Singleton

    def __new__(cls):
        # Construct service loader
        svcdef_loader = ServiceDefLoader()
        for svc in SERVICE_NAMES:
            ServiceDefLoader.register_servicedef(
                SERVICE_ID.format(svc, VERSION),  get_filename(svc))

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


class SCC(SleepWalkerServerBase):
    """This class is the main interface to interact with a SteelCentral
    Controller.
    """
    _svcmgr_cls_module = 'steelscript.scc.core.scc'
    _svcmgr_cls_name = 'SCCServiceManager'
    version = VERSION

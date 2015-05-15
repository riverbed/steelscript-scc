# Copyright (c) 2015 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

import os

from sleepwalker.service import ServiceManager
from sleepwalker.connection import ConnectionManager, ConnectionHook

import reschema.servicedef as ServiceDef
import steelscript.common.service


SERVICE_ID = 'https://support.riverbed.com/apis/{0}/{1}'

SERVICE_NAMES = ['cmc.appliance_inventory', 'cmc.stats']

VERSION = '1.0'


def get_filename(service):
    current_dir = os.path.dirname(__file__)
    service_file = os.path.join(current_dir,
                                'servicedef/{0}.yml'.format(service))
    return service_file


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


class SCCServiceManager(ServiceManager):
    """This class encapsulates the storage of SCC services
    and connection with the SCC device.
    """
    _instance = None

    @classmethod
    def create(cls):
        if cls._instance is None:
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
            conn_manager.add_conn_hook(ConnectionHook())

            # Initialize the instance of service manager
            cls._instance = ServiceManager(servicedef_manager=svcdef_manager,
                                           connection_manager=conn_manager)
        return cls._instance


class SCC(steelscript.common.service.Service):
    """This class is the main interface to interact with a SteelCentral
    Controller.
    """
    def __init__(self, host, port=None, auth=None):
        super(SCC, self).__init__("scc", host=host)
        self._svcmgr = SCCServiceManager.create()

    def request(self, service, resource, link, criteria=None):
        """Send request to the scc device and expects a response
        immediately.

        :param service: string, name of the service, e.g. cmc.stats
        :param resource: string, name of the resource to query
        :param link: string, name of the link method to query
        :param criteria: dict, criteria fields to query
        """
        svc = self._svcmgr.find_by_name(host=self.host, name=service,
                                        version=VERSION)
        data_rep = svc.bind(resource)
        resp = data_rep.execute(link, criteria)
        try:
            return resp.data['response_data']
        except:
            return resp.data

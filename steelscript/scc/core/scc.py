# Copyright (c) 2015 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

import os

from sleepwalker.service import ServiceManager
from sleepwalker.connection import Connection, ConnectionManager

import reschema.servicedef as ServiceDef


SERVICE_ID = 'https://support.riverbed.com/apis/cmc.{0}/{1}'

SERVICE_NAMES = ['appliance_inventory', 'stats']

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


class SCCConnectionHook(object):
    def connect(self, host, auth=None):
        return Connection(host)


class SCCServiceManager(ServiceManager):
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
            conn_manager.add_conn_hook(SCCConnectionHook())

            # Initialize the instance of service manager
            cls._instance = ServiceManager(servicedef_manager=svcdef_manager,
                                           connection_manager=conn_manager)
        return cls._instance

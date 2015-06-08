# Copyright (c) 2015 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

import reschema.servicedef as ServiceDef


SERVICE_ID = 'https://support.riverbed.com/apis/{0}/{1}'


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



# Copyright (c) 2015 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.


import pkg_resources

from steelscript.appfwk.apps.plugins import Plugin


class SCCPlugin(Plugin):
    title = 'SteelCentral Controller Datasource Plugin'
    description = 'A Portal datasource plugin with example report'
    version = pkg_resources.get_distribution('steelscript.scc').version
    author = 'Riverbed Technology'

    enabled = True
    can_disable = True

    devices = ['devices']
    datasources = ['datasources']
    reports = ['reports']

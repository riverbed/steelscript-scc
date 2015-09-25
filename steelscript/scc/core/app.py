# Copyright (c) 2015 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

from steelscript.common.app import Application
from steelscript.scc.core import SCC
from steelscript.common.service import OAuth


class SCCApp(Application):
    """Class to wrap common command line parsing"""
    def __init__(self, *args, **kwargs):
        super(SCCApp, self).__init__(*args, **kwargs)
        self.scc = None

    def parse_args(self):
        super(SCCApp, self).parse_args()

    def add_positional_args(self):
        self.add_positional_arg(
            'host',
            'SCC hostname or IP address '
            '(including scheme, i.e. http:// or https://)')

        self.add_positional_arg(
            'access_code',
            'access code, manually obtained via web UI of the SCC')

    def add_options(self, parser):
        super(SCCApp, self).add_options(parser)

    def setup(self):
        super(SCCApp, self).setup()
        self.scc = SCC(host=self.options.host,
                       auth=OAuth(self.options.access_code))

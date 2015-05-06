# Copyright (c) 2015 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

from steelscript.scc.core.app import SCCApp
from steelscript.scc.core.report import *
from steelscript.netprofiler.core.filters import TimeFilter

import pprint


class ThroughputStatsReportApp(SCCApp):

    def add_options(self, parser):
        super(ThroughputStatsReportApp, self).add_options(parser)

        parser.add_option('--timefilter', dest='timefilter', default='last 1 hour',
            help='Time range to analyze (defaults to "last 1 hour") '
            'other valid formats are: "4/21/13 4:00 to 4/21/13 5:00" '
            'or "16:00:00 to 21:00:04.546"')

        parser.add_option('--traffic_type', dest='traffic_type', default='peak',
            help='Type of traffic to query, either for peak or p95')

        parser.add_option('--device', dest='device', default=None,
            help='Device ID')

        parser.add_option('--port', dest='port', default=None)

    def validate_args(self):
        super(ThroughputStatsReportApp, self).validate_args()

        if not self.options.device:
            self.parser.error("Device (serial ID) is required")

    def main(self):
        with ThroughputStatsReport(self.scc) as report:
            report.run(timefilter=self.options.timefilter,
                       traffic_type=self.options.traffic_type,
                       device=self.options.device,
                       port=self.options.port)
            pprint.pprint(report.data)
            print('')

if __name__=='__main__':
    ThroughputStatsReportApp().run()

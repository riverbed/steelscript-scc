# Copyright (c) 2015 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

from steelscript.scc.core.app import SCCApp
from steelscript.scc.core.report import *

import pprint


class MultiDevStatsReportApp(SCCApp):

    def add_options(self, parser):
        super(MultiDevStatsReportApp, self).add_options(parser)

        parser.add_option(
            '--timefilter', dest='timefilter', default='last 1 hour',
            help='Time range to analyze (defaults to "last 1 hour") '
            'other valid formats are: "4/21/13 4:00 to 4/21/13 5:00" '
            'or "16:00:00 to 21:00:04.546"')

        parser.add_option(
            '--devices', dest='devices', default=None,
            help='An array of devices being queried on. None implies all '
            'devices. If multiple devices are queried on, the data points '
            'are the sum across all the devices.')

    def main(self):
        with ConnectionPoolingStatsReport(self.scc) as report:
            report.run(timefilter=self.options.timefilter,
                       devices=self.options.devices)
            pprint.pprint(report.data)
            print('')

        with ConnectionForwardingStatsReport(self.scc) as report:
            report.run(timefilter=self.options.timefilter,
                       devices=self.options.devices)
            pprint.pprint(report.data)
            print('')

        with DNSUsageStatsReport(self.scc) as report:
            report.run(timefilter=self.options.timefilter,
                       devices=self.options.devices)
            pprint.pprint(report.data)
            print('')

        with DNSCacheHitsStatsReport(self.scc) as report:
            report.run(timefilter=self.options.timefilter,
                       devices=self.options.devices)
            pprint.pprint(report.data)
            print('')

        with HTTPStatsReport(self.scc) as report:
            report.run(timefilter=self.options.timefilter,
                       devices=self.options.devices)
            pprint.pprint(report.data)
            print('')

        with NFSStatsReport(self.scc) as report:
            report.run(timefilter=self.options.timefilter,
                       devices=self.options.devices)
            pprint.pprint(report.data)
            print('')

        with SSLStatsReport(self.scc) as report:
            report.run(timefilter=self.options.timefilter,
                       devices=self.options.devices)
            pprint.pprint(report.data)
            print('')

        with DiskLoadStatsReport(self.scc) as report:
            report.run(timefilter=self.options.timefilter,
                       devices=self.options.devices)
            pprint.pprint(report.data)
            print('')

if __name__ == '__main__':
    MultiDevStatsReportApp().run()

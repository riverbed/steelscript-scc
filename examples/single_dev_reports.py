# Copyright (c) 2015 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

from steelscript.scc.core.app import SCCApp
from steelscript.scc.core import report as report_module

import pprint


class SingleDevStatsReportApp(SCCApp):

    def add_options(self, parser):
        super(SingleDevStatsReportApp, self).add_options(parser)

        parser.add_option(
            '--timefilter', dest='timefilter', default='last 1 hour',
            help='Time range to analyze (defaults to "last 1 hour") '
            'other valid formats are: "4/21/13 4:00 to 4/21/13 5:00" '
            'or "16:00:00 to 21:00:04.546"')

        parser.add_option('--device', dest='device', default=None,
                          help='Device ID')

    def validate_args(self):
        super(SingleDevStatsReportApp, self).validate_args()

        if not self.options.device:
            self.parser.error("Device (serial ID) is required")

    def main(self):
        with report_module.SDRAdaptiveStatsReport(self.scc) as report:
            report.run(timefilter=self.options.timefilter,
                       device=self.options.device)
            pprint.pprint(report.data)
            print('')

        with report_module.MemoryPagingStatsReport(self.scc) as report:
            report.run(timefilter=self.options.timefilter,
                       device=self.options.device)
            pprint.pprint(report.data)
            print('')

        with report_module.CpuUtilizationStatsReport(self.scc) as report:
            report.run(timefilter=self.options.timefilter,
                       device=self.options.device)
            pprint.pprint(report.data)
            print('')

        with report_module.PFSStatsReport(self.scc) as report:
            report.run(timefilter=self.options.timefilter,
                       device=self.options.device)
            pprint.pprint(report.data)

if __name__ == '__main__':
    SingleDevStatsReportApp().run()

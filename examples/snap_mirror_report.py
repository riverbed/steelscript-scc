# Copyright (c) 2015 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

from steelscript.scc.core.app import SCCApp
from steelscript.scc.core import report as report_module

import pprint


class SnapMirrorStatsReportApp(SCCApp):

    def add_options(self, parser):
        super(SnapMirrorStatsReportApp, self).add_options(parser)

        parser.add_option(
            '--timefilter', dest='timefilter', default='last 1 hour',
            help='Time range to analyze (defaults to "last 1 hour") '
            'other valid formats are: "4/21/13 4:00 to 4/21/13 5:00" '
            'or "16:00:00 to 21:00:04.546"')

        parser.add_option(
            '--traffic_type', dest='traffic_type', default='regular',
            help='Type of traffic to query, either for regular or peak')

        parser.add_option('--filer_id', dest='filer_id', default=None,
                          help='Integer value')

        parser.add_option('--device', dest='device', default=None,
                          help='Device ID')

    def validate_args(self):
        super(SnapMirrorStatsReportApp, self).validate_args()

        if not self.options.device:
            self.parser.error("Device (serial ID) is required")

        if self.options.filer_id and not self.options.filer_id.isdigit():
            self.parser.error("Filer ID '%s' is not an integer" %
                              self.options.filer_id)

    def main(self):
        with report_module.SnapMirrorStatsReport(self.scc) as report:
            filer_id = (int(self.options.filer_id)
                        if self.options.filer_id else None)

            report.run(timefilter=self.options.timefilter,
                       traffic_type=self.options.traffic_type,
                       device=self.options.device,
                       filer_id=filer_id)

            pprint.pprint(report.data)


if __name__ == '__main__':
    SnapMirrorStatsReportApp().run()

# Copyright (c) 2015 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

from steelscript.scc.core.app import SCCApp
from steelscript.scc.core import report as report_module

import pprint


class LUNIOStatsReportApp(SCCApp):

    def add_options(self, parser):
        super(LUNIOStatsReportApp, self).add_options(parser)

        parser.add_option(
            '--timefilter', dest='timefilter', default='last 1 hour',
            help='Time range to analyze (defaults to "last 1 hour") '
            'other valid formats are: "4/21/13 4:00 to 4/21/13 5:00" '
            'or "16:00:00 to 21:00:04.546"')

        parser.add_option(
            '--traffic_type', dest='traffic_type', default='io',
            help='Type of traffic to query, io/iops/io_time')

        parser.add_option('--lun_subclass_id', dest='lun_subclass_id',
                          default=None,
                          help='Integer value')

        parser.add_option('--device', dest='device', default=None,
                          help='Device ID')

    def validate_args(self):
        super(LUNIOStatsReportApp, self).validate_args()

        if not self.options.device:
            self.parser.error("Device (serial ID) is required")

        if (self.options.lun_subclass_id and
                not self.options.lun_subclass_id.isdigit()):
            self.parser.error("LUN subclass ID '%s' is not an integer" %
                              self.options.lun_subclass_id)

    def main(self):
        with report_module.SteelFusionLUNIOReport(self.scc) as report:
            lun_subclass_id = (int(self.options.lun_subclass_id)
                               if self.options.lun_subclass_id else None)

            report.run(timefilter=self.options.timefilter,
                       traffic_type=self.options.traffic_type,
                       device=self.options.device,
                       lun_subclass_id=lun_subclass_id)

            pprint.pprint(report.data)


if __name__ == '__main__':
    LUNIOStatsReportApp().run()

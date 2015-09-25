# Copyright (c) 2015 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

from steelscript.scc.core.app import SCCApp
import steelscript.scc.core.report as report_classes

import pprint


class ThroughputStatsReportApp(SCCApp):

    class_map = {'single': 'ThroughputStatsReport',
                 'multiple': 'ThroughputPerApplStatsReport'}

    traffic_types = ['peak', 'p95']

    def add_options(self, parser):
        super(ThroughputStatsReportApp, self).add_options(parser)

        parser.add_option(
            '--report', dest='report',
            help='Report name should be one of the following: %s.' %
            ', '.join(self.class_map.keys()))

        parser.add_option(
            '--timefilter', dest='timefilter', default='last 1 hour',
            help='Time range to analyze (defaults to "last 1 hour") '
            'other valid formats are: "4/21/13 4:00 to 4/21/13 5:00" '
            'or "16:00:00 to 21:00:04.546"')

        parser.add_option(
            '--traffic_type', dest='traffic_type', default='peak',
            help='Type of traffic to query, either for peak or p95')

        parser.add_option(
            '--device', dest='device', default=None,
            help='Device ID, required when running report "single"')

        parser.add_option('--port', dest='port', default=None)

        parser.add_option(
            '--devices', dest='devices', default=None,
            help='An array of devices being queried on. None implies all '
            'devices. If multiple devices are queried on, the data points '
            'are the sum across all the devices, required when running '
            'report "multiple"')

    def validate_args(self):
        super(ThroughputStatsReportApp, self).validate_args()

        r = self.options.report

        if not r:
            self.parser.error("Report name is required")
        elif r not in self.class_map:
            self.parser.error("Report should be one of the following: %s." %
                              ', '.join(self.class_map.keys()))

        if self.options.traffic_type not in self.traffic_types:
            self.parser.error("Traffic type should be one of the following: "
                              "%s." % ', '.join(self.traffic_types))

        if r == 'single' and not self.options.device:
            self.parser.error("Device (serial ID) is required")
        elif r == 'multiple' and not self.options.devices:
            self.parser.error("Comma separated device IDs are required.")

    def main(self):
        """Below is an abstracted behavior of how a report is run.

        First a report class definition is obtained from the class_map,
        then the report object is initialized using self.scc, which stands
        for the SCC device's service.

        Then by iterating valid_options, the parameter set kwargs is populated
        by not-None parameters.

        report.run(**kwargs) will run the report with parameters and response
        data is stored in report.data
        """
        report_class = getattr(report_classes,
                               self.class_map[self.options.report])
        report = report_class(self.scc)
        kwargs = {}
        valid_options = (['timefilter'] + report.required_fields +
                         report.non_required_fields)
        for opt in valid_options:
            v = getattr(self.options, opt, None)
            if v:
                kwargs[opt] = v

        report.run(**kwargs)
        pprint.pprint(report.data)

if __name__ == '__main__':
    ThroughputStatsReportApp().run()

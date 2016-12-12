# Copyright (c) 2015 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

"""
This file defines a single report of multiple tables and widgets.

The typical structure is as follows:

    report = Report.create('Stock Report')
    report.add_section()

    table = SomeTable.create(name, table_options...)
    table.add_column(name, column_options...)
    table.add_column(name, column_options...)
    table.add_column(name, column_options...)

    report.add_widget(yui3.TimeSeriesWidget, table, name, width=12)

See the documeantion or sample plugin for more details
"""
from steelscript.appfwk.apps.report.models import Report
import steelscript.appfwk.apps.report.modules.c3 as c3

# Import the datasource module for this plugin (if needed)
import steelscript.scc.appfwk.datasources.scc as scc


report = Report.create("SCC Device Throughput", position=10)

report.add_section()

table = scc.SCCThroughputTable.create(name='throughputtable')

table.add_column('timestamp', 'Time', datatype='time', iskey=True)
table.add_column('wan_in', 'inbound wan traffic', units='B/s')
table.add_column('wan_out', 'outbound wan traffic', units='B/s')
table.add_column('lan_in', 'inbound lan traffic', units='B/s')
table.add_column('lan_out', 'outbound lan traffic', units='B/s')

report.add_widget(c3.TimeSeriesWidget, table, "SCC Device Throughput",
                  height=300, width=12)

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
import steelscript.appfwk.apps.report.modules.tables as tables

# Import the datasource module for this plugin (if needed)
import steelscript.scc.appfwk.datasources.scc as scc


report = Report.create("SCC Appliance List", position=10)

report.add_section()

table = scc.SCCAppliancesTable.create(name='appltable')

table.add_column('address', 'Appliance IP', iskey=True, datatype="string")
table.add_column('hostname', 'Appliance Host Name', datatype="string")
table.add_column('serial', 'Appliance Serial Number', datatype="string")
table.add_column('time_zone', 'Appliance Time Zone', datatype="string")

report.add_widget(tables.TableWidget, table, "Appliance List",
                  height=300, width=12)

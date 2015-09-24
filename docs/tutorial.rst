.. py:currentmodule:: steelscript.scc.core

SteelScript SCC Tutorial
========================

This tutorial presents a step-by-step description of how to use
SteelScript SCC package to develop scripts to retrieve data from
target SCC device.


Background
----------

SCC provides centralized reporting and analysis of the states of
other connected riverbed appliances (i.e., SteelHead). SteelScript
for SCC makes this wealth of data easily accessible via Python.

SCC Objects
-----------

Interacting with a SCC leverages two key classes:

* :py:class:`SCC <scc.SCC>` - provides the primary interface to the
  appliance, handling initialization, setup and communication via REST API calls.

* :py:class:`BaseStatsReport <report.BaseStatsReport>` - leverages the SCC
  object to pull data and create new reports.

In most cases you will not use :py:class:`BaseStatsReport <report.BaseStatsReport>`
directly -- your scripts will use a more helpful object tailored to the
desired report, such as a
:py:class:`BWTimeSeriesStatsReport <report.BWTimeSeriesStatsReport>` or a
:py:class:`ThroughputStatsReport <report.ThroughputStatsReport>`.
We will cover those shortly.

Startup
-------

As with any Python code, the first step is to import the modules involved.
The SteelScript code for working with SCC appliances resides in a module
:py:mod:`steelscript.scc.core`. The main class in this module is
:py:class:`SCC <scc.SCC>`. This object represents a connection to an
SCC appliance. Let's see how easy it is to create an SCC object.

.. code-block:: python

   >>> from steelscript.scc.core import SCC
   >>> from steelscript.common.service import OAuth
   >>> scc = SCC(host='$hostname', auth=OAuth('$access_code'))

Replace the first argument ``$hostname`` with the hostname or IP address
of the SCC appliance. The second argument is an access code,
which is required for OAuth 2.0 authentication. The access code is usually
obtained on the web UI of the SCC appliance (See the "Enabling REST API Access"
section in your SCC documentation for more information).

Generating Reports
------------------
After an SCC object has been instantiated, now it is time to use it to
retrieve some data from the SCC appliance. Good news is that
SteelScript-SCC comes with a comprehensive coverage of all resources
underneath the ``cmc.stats`` service. One just needs to browse through
classes defined in the :py:mod:`steelscript.scc.core<steelscript.scc.core>`
module to use the report class matching current needs. For example, in order to get
optimized bandwidth at different times of all devices associated with the SCC appliance,
:py:class:`BWTimeSeriesStatsReport <report.BWTimeSeriesStatsReport>` is the one to use.

.. code-block:: python

    >>> from steelscript.scc.core import BWTimeSeriesStatsReport
    >>> import pprint
    >>> report = BWTimeSeriesStatsReport(scc)
    >>> report.run(timefilter="last 1 hour", traffic_type='optimized')

Note that ``timefilter`` specifies the time range of the query and ``traffic_type``
determines the type of traffic to query.

Now that the report has been run, we can fetch the data by accessing the data attribute:

.. code-block:: python

    >>> pprint.pprint(report.data)
    [{u'data': [7308580.0, 16571400.0, 13216600.0, 68872900.0],
      u'timestamp': 1440780000},
     {u'data': [6002410.0, 23606000.0, 10935900.0, 52749800.0],
      u'timestamp': 1440780300},
     {u'data': [4056250.0, 16865900.0, 6394300.0, 37789200.0],
      u'timestamp': 1440780600},
     {u'data': [5850490.0, 44258800.0, 11690500.0, 104962000.0],
      u'timestamp': 1440780900},
     {u'data': [7468290.0, 24188900.0, 12829400.0, 84234000.0],
      u'timestamp': 1440781200},
     {u'data': [13041800.0, 34822600.0, 17672900.0, 77343300.0],
      u'timestamp': 1440781500},
     {u'data': [182396000.0, 206378000.0, 195764000.0, 261148000.0],
      u'timestamp': 1440781800},
     {u'data': [178387000.0, 194976000.0, 199298000.0, 235883000.0],
      u'timestamp': 1440782100},
     {u'data': [177016000.0, 203324000.0, 190545000.0, 261889000.0],
      u'timestamp': 1440782400},
     {u'data': [187747000.0, 416022000.0, 197363000.0, 450196000.0],
      u'timestamp': 1440782700},
     {u'data': [151403000.0, 334982000.0, 216453000.0, 422683000.0],
      u'timestamp': 1440783000},
     {u'data': [159875000.0, 409043000.0, 190787000.0, 451655000.0],
      u'timestamp': 1440783300}]


Extending the Example
---------------------

As a last item to help get started with your own scripts, we will extend
our example with command-line options.

Below is an example script with ability to accept command-line options and
present data in a table-like format.

.. code-block:: python

    #!/usr/bin/env python

    import pprint

    from steelscript.scc.core.app import SCCApp
    from steelscript.scc.core import BWTimeSeriesStatsReport


    class BWTimeSeriesStatsReportApp(SCCApp):

        traffic_types = ['optimized', 'passthrough']

        def add_options(self, parser):
            super(BWTimeSeriesStatsReportApp, self).add_options(parser)

            parser.add_option(
                '--timefilter', dest='timefilter', default='last 1 hour',
                help='Time range to analyze (defaults to "last 1 hour") '
                'other valid formats are: "4/21/13 4:00 to 4/21/13 5:00" '
                'or "16:00:00 to 21:00:04.546"')

            parser.add_option(
                '--traffic_type', dest='traffic_type', default='optimized',
                help='Type of traffic to query, either optimized or passthrough')

            parser.add_option(
                '--devices', dest='devices', default=None,
                help='An array of devices being queried on. None implies all '
                'devices. If multiple devices are queried on, the data points '
                'are the sum across all the devices.')

            parser.add_option('--port', dest='port', default=None)

        def main(self):
            report = BWTimeSeriesStatsReport(self.scc)
            report.run(traffic_type=self.options.traffic_type,
                       timefilter=self.options.timefilter,
                       devices=self.options.devices,
                       port=self.options.port)
            pprint.pprint(report.data)

    if __name__ == '__main__':
        BWTimeSeriesStatsReportApp().run()

Copy the above code into a new file, and now you can run the file to display the data.

.. code-block:: python

   > python myreport.py $hostname $access_code --devices $serial_numbers --traffic_type 'optimized' --timefilter 'last 1 hour'
    [{u'data': [7308580.0, 16571400.0, 13216600.0, 68872900.0],
      u'timestamp': 1440780000},
     {u'data': [6002410.0, 23606000.0, 10935900.0, 52749800.0],
      u'timestamp': 1440780300},
     {u'data': [4056250.0, 16865900.0, 6394300.0, 37789200.0],
      u'timestamp': 1440780600},
     {u'data': [5850490.0, 44258800.0, 11690500.0, 104962000.0],
      u'timestamp': 1440780900},
     {u'data': [7468290.0, 24188900.0, 12829400.0, 84234000.0],
      u'timestamp': 1440781200},
     {u'data': [13041800.0, 34822600.0, 17672900.0, 77343300.0],
      u'timestamp': 1440781500},
     {u'data': [182396000.0, 206378000.0, 195764000.0, 261148000.0],
      u'timestamp': 1440781800},
     {u'data': [178387000.0, 194976000.0, 199298000.0, 235883000.0],
      u'timestamp': 1440782100},
     {u'data': [177016000.0, 203324000.0, 190545000.0, 261889000.0],
      u'timestamp': 1440782400},
     {u'data': [187747000.0, 416022000.0, 197363000.0, 450196000.0],
      u'timestamp': 1440782700},
     {u'data': [151403000.0, 334982000.0, 216453000.0, 422683000.0],
      u'timestamp': 1440783000},
     {u'data': [159875000.0, 409043000.0, 190787000.0, 451655000.0],
      u'timestamp': 1440783300}]

Now let us walk through the above script in detail.

First we need to import some modules.

.. code-block:: python

    #!/usr/bin/env python

    import pprint

    from steelscript.scc.core.app import SCCApp
    from steelscript.scc.core import BWTimeSeriesStatsReport

The first line is called a shebang, it tells the system that the script should
be executed using the program after '#!'. The ``SCCApp`` is imported for ease
of writing scripts to generate reports for SCC. The
:py:class:`BWTimeSeriesStatsReport <report.BWTimeSeriesStatsReport>` is
imported to facilitate reporting data retrieved at resource ``bw_timeseries``, which
belongs to the ``cmc.stats`` service on a SCC device.

.. code-block:: python

    class BWTimeSeriesStatsReportApp(SCCApp):

        def add_options(self, parser):
            super(BWTimeSeriesStatsReportApp, self).add_options(parser)

            parser.add_option(
                '--timefilter', dest='timefilter', default='last 1 hour',
                help='Time range to analyze (defaults to "last 1 hour") '
                'other valid formats are: "4/21/13 4:00 to 4/21/13 5:00" '
                'or "16:00:00 to 21:00:04.546"')

            parser.add_option(
                '--traffic_type', dest='traffic_type', default='optimized',
                help='Type of traffic to query, either optimized or passthrough')

            parser.add_option(
                '--devices', dest='devices', default=None,
                help='An array of devices being queried on. None implies all '
                'devices. If multiple devices are queried on, the data points '
                'are the sum across all the devices.')

            parser.add_option('--port', dest='port', default=None)

This section begins with definition of the ``BWTimeSeriesStatsReportApp`` class,
which inherits from the class :py:class:`SCCApp<app.SCCApp>`. The inheritence
saves work of adding hostname option as well as access code option, both of which
are required for fetching data from SCC device.

The ``add_options`` method introduces options to the report, including time filter,
traffic type, devices and port. The help text for each option can be seen using the
'--help' option.

.. code-block:: python

        def main(self):
            report = BWTimeSeriesStatsReport(self.scc)
            report.run(traffic_type=self.options.traffic_type,
                       timefilter=self.options.timefilter,
                       devices=self.options.devices,
                       port=self.options.port)
            pprint.pprint(report.data)

    if __name__ == '__main__':
        BWTimeSeriesStatsReportApp().run()

This is the main part of the script. The ``run`` method of the
:py:class:`BWTimeSeriesStatsReport <report.BWTimeSeriesStatsReport>`
class will execute its ``main`` method. In the ``main`` method, ``self.scc`` represents
the SCC object, which has been created by :py:class:`SCCApp<app.SCCApp>` class.
``report.run`` will use all the input options and retrieve data via the SCC object.
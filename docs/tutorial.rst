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
:py:class:`BWUsageStatsReport <report.BWUsageStatsReport>` or a
:py:class:`ThroughputStatsReport <report.ThroughputStatsReport>`.
We will cover those shortly.

Startup
-------

As with any Python code, the first step is to import the modules involved.
The SteelScript code for working with SCC appliances resides in a module
:py:mod:`steelscript.scc.core`. The main class in this module is
:py:class:`SCC <scc.SCC>`. This object represents a connection to an
SCC appliance. Let us see how easy it is to create an SCC object.

.. code-block:: python

   >>> from steelscript.scc.core import SCC
   >>> from steelscript.common.service import OAuth
   >>> scc = SCC(host='$hostname', auth=OAuth('$access_code'))

Replace the first argument ``$hostname`` with the hostname or IP address
of the SCC appliance. Note that a URI scheme needs to be included in
``$hostname``, e.g. ``https://``. The second argument is an access code,
which is required for OAuth 2.0 authentication. The access code is usually
obtained on the web UI of the SCC appliance.

Generating Reports
------------------
After an SCC object has been instantiated, now it is time to use it to
retrieve some data from the SCC appliance. Good news is that
SteelScript-SCC comes with a comprehensive coverage of all resources
underneath the ``cmc.stats`` service. One just needs to browse through
classes defined in the :py:mod:`steelscript.scc.core<steelscript.scc.core>`
module to use the report class matching current needs. For example, in order to get
optimized bandwidth usage of all devices associated with the SCC appliance,
:py:class:`BWUsageStatsReport <report.BWUsageStatsReport>` is the one to use.

.. code-block:: python

    >>> from steelscript.scc.core import BWUsageStatsReport
    >>> import pprint
    >>> report = BWUsageStatsReport(scc)
    >>> report.run(timefilter="last 1 hour", traffic_type='optimized')
    >>> pprint.pprint(report.data)
    [{u'data': [7533.0, 7068.0, 51163.0, 46908.0], u'port': 5357},
     {u'data': [2892232.0, 2922770700.0, 135907.0, 3087530900.0], u'port': 8080},
     {u'data': [141073800.0, 1219051.0, 179353770.0, 17400.0], u'port': 20000},
     {u'data': [90910214.0, 828152.0, 124303120.0, 11840.0], u'port': 20001},
     {u'data': [87283800.0, 773560.0, 117157580.0, 11480.0], u'port': 20002},
     {u'data': [115996420.0, 1045455.0, 154281210.0, 14480.0], u'port': 20003},
     {u'data': [103978370.0, 904177.0, 136756050.0, 13360.0], u'port': 20004},
     {u'data': [84806410.0, 791903.0, 120069113.0, 12240.0], u'port': 20005},
     {u'data': [110010958.0, 983224.0, 146348590.0, 14120.0], u'port': 20006},
     {u'data': [56573288.0, 588490.0, 89552774.0, 8760.0], u'port': 20007},
     {u'data': [83459250.0, 776085.0, 117758570.0, 10880.0], u'port': 20008},
     {u'data': [72793617.0, 731987.0, 111386053.0, 10880.0], u'port': 20009},
     {u'data': [101631357.0, 889462.0, 131271187.0, 12800.0], u'port': 20010},
     {u'data': [101687340.0, 918534.0, 137246030.0, 13240.0], u'port': 20011},
     {u'data': [138074650.0, 1159541.0, 172217020.0, 15440.0], u'port': 20012},
     {u'data': [92761940.0, 937590.0, 140369910.0, 13480.0], u'port': 20013},
     {u'data': [121041660.0, 1059131.0, 155970970.0, 15080.0], u'port': 20014},
      ...
     {u'data': [72989030.0, 686568.0, 104896060.0, 10760.0], u'port': 20249}]

Note that ``timefilter`` specifies the time range of the query and ``traffic_type``
determines the type of traffic to query.

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
    from steelscript.scc.core import BWUsageStatsReport


    class BWUsageStatsReportApp(SCCApp):

        traffic_types = ['optimized', 'passthrough']

        def add_options(self, parser):
            super(BWUsageStatsReportApp, self).add_options(parser)

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
            report = BWUsageStatsReport(self.scc)
            report.run(traffic_type=self.options.traffic_type,
                       timefilter=self.options.timefilter,
                       devices=self.options.devices,
                       port=self.options.port)
            pprint.pprint(report.data)

    if __name__ == '__main__':
        BWUsageStatsReportApp().run()

Copy the above code into a new file, and now you can run the file to display the data.

.. code-block:: python

   > python myreport.py $hostname $access_code --devices $serial_numbers --traffic_type 'optimized' --timefilter 'last 10 min'
    [{u'data': [0, 0, 0, 0], u'port': 8080},
     {u'data': [31550200.0, 238201.0, 33113300.0, 3080.0], u'port': 20000},
     {u'data': [17476320.0, 186590.0, 25823480.0, 2720.0], u'port': 20001},
     {u'data': [16470080.0, 160966.0, 22293780.0, 2320.0], u'port': 20002},
     {u'data': [9187440.0, 87432.0, 12095170.0, 1440.0], u'port': 20003},
     {u'data': [13492540.0, 111126.0, 15268660.0, 1840.0], u'port': 20004},
     {u'data': [25354800.0, 224038.0, 31030400.0, 3080.0], u'port': 20005},
     {u'data': [15778460.0, 152416.0, 20889110.0, 2640.0], u'port': 20006},
     {u'data': [7519940.0, 73920.0, 10178730.0, 1120.0], u'port': 20007},
     {u'data': [45202700.0, 384284.0, 53517400.0, 4840.0], u'port': 20008},
     {u'data': [17490280.0, 154565.0, 21514590.0, 2200.0], u'port': 20009},
     {u'data': [25921920.0, 203100.0, 28269880.0, 2720.0], u'port': 20010},
     {u'data': [31410490.0, 225853.0, 31247250.0, 3040.0], u'port': 20011},
     {u'data': [17721410.0, 153212.0, 21216240.0, 2200.0], u'port': 20012},
     {u'data': [22082020.0, 190754.0, 26339980.0, 2640.0], u'port': 20013},
     {u'data': [31591550.0, 248953.0, 34635500.0, 3320.0], u'port': 20014},
     {u'data': [17336960.0, 138849.0, 19120030.0, 2080.0], u'port': 20015},
     {u'data': [32534700.0, 247688.0, 34171100.0, 3560.0], u'port': 20016},
     ...
     {u'data': [16553200.0, 157697.0, 21735970.0, 2320.0], u'port': 20249}]]

Now let us walk through the above script in detail.

First we need to import some modules.

.. code-block:: python

    #!/usr/bin/env python

    import pprint

    from steelscript.scc.core.app import SCCApp
    from steelscript.scc.core import BWUsageStatsReport

The first line is called a shebang, it tells the system that the script should
be executed using the program after '#!'. The ``SCCApp`` is imported for ease
of writing scripts to generate reports for SCC. The
:py:class:`BWUsageStatsReport <report.BWUsageStatsReport>` is
imported to facilitate reporting data retrieved at resource 'bw_usage', which
belongs to the 'cmc.stats' service on a SCC device.

.. code-block:: python

    class BWUsageStatsReportApp(SCCApp):

        def add_options(self, parser):
            super(BWUsageStatsReportApp, self).add_options(parser)

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

This section begins with definition of the ``BWUsageStatsReportApp`` class,
which inherits from the class :py:class:`SCCApp<app.SCCApp>`. The inheritence
saves work of adding hostname option as well as access code option, both of which
are required for fetching data from SCC device.

The ``add_options`` method introduces options to the report, including time filter,
traffic type, devices and port. The help text for each option can be seen using the
'--help' option.

.. code-block:: python

        def main(self):
            report = BWUsageStatsReport(self.scc)
            report.run(traffic_type=self.options.traffic_type,
                       timefilter=self.options.timefilter,
                       devices=self.options.devices,
                       port=self.options.port)
            pprint.pprint(report.data)

    if __name__ == '__main__':
        BWUsageStatsReportApp().run()

This is the main part of the script. The ``run`` method of the
:py:class:`BWUsageStatsReport <report.BWUsageStatsReport>`
class will execute its ``main`` method. In the ``main`` method, ``self.scc`` represents
the SCC object, which has been created by :py:class:`SCCApp<app.SCCApp>` class.
``report.run`` will use all the input options and retrieve data via the SCC object.
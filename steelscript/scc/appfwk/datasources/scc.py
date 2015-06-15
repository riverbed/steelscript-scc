# Copyright (c) 2015 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.


import logging

import pandas

from django import forms

from steelscript.appfwk.apps.datasource.models import \
    DatasourceTable, TableQueryBase
from steelscript.appfwk.apps.devices.devicemanager import DeviceManager
from steelscript.appfwk.apps.devices.forms import fields_add_device_selection
from steelscript.appfwk.apps.datasource.forms import fields_add_time_selection
from steelscript.common.timeutils import datetime_to_seconds
from steelscript.appfwk.apps.datasource.models import TableField
from steelscript.scc.core.scc import SCCException


logger = logging.getLogger(__name__)


class BaseSCCTable(DatasourceTable):
    """Base class for SCC report tables, can not be directly used
    in report definitions.
    """
    class Meta:
        proxy = True

    _query_class = 'BaseSCCQuery'

    def post_process_table(self, field_options):
        fields_add_device_selection(self, keyword='scc_device',
                                    label='SCC', module='scc',
                                    enabled=True)


class BaseSCCStatsTable(BaseSCCTable):
    """Base class for SCC stats service report tables, can not be directly
    used in report definitions.
    """
    class Meta:
        proxy = True

    _query_class = 'BaseSCCStatsQuery'

    # default field parameters
    FIELD_OPTIONS = {'duration': 60,
                     'durations': ('15 min', '1 hour',
                                   '2 hours', '4 hours', '12 hours',
                                   '1 day', '1 week', '4 weeks'),
                     }

    def post_process_table(self, field_options):
        super(BaseSCCStatsTable, self).post_process_table(field_options)

        duration = field_options['duration']
        if isinstance(duration, int):
            duration = "%d min" % duration

        fields_add_time_selection(self,
                                  initial_duration=duration,
                                  durations=field_options['durations'])


class SCCThroughputTable(BaseSCCStatsTable):
    """This class defines the table fields and query class for the throughput
    resource underneath cmc.stats service.
    """
    class Meta:
        proxy = True

    _query_class = 'SCCThroughputQuery'

    def post_process_table(self, field_options):
        super(SCCThroughputTable, self).post_process_table(field_options)

        # Add device ID field
        field = TableField(keyword='device_id',
                           label='Device Serial ID',
                           required=True)
        field.save()
        self.fields.add(field)

        # Add traffic_type field
        traffic_types = ('peak', 'p95')
        field = TableField(keyword='traffic_type',
                           label='Traffic Type',
                           field_cls=forms.ChoiceField,
                           field_kwargs={'choices':
                                         zip(traffic_types, traffic_types)})
        field.save()
        self.fields.add(field)


class BaseSCCApplInvtTable(BaseSCCTable):
    """Base class for SCC appliance_interval service report tables, can not be
    directly used in reports"""
    class Meta:
        proxy = True

    _query_class = 'BaseSCCApplInvtQuery'


class SCCAppliancesTable(BaseSCCApplInvtTable):
    """This class defines table and the query class for the appliances
    resource underneath cmc.appliance_inventory service.
    """
    class Meta:
        proxy = True

    _query_class = 'SCCAppliancesQuery'


class BaseSCCQuery(TableQueryBase):
    """Base class for SCC device query, can not be directly used"""
    criteria = None

    def fill_criteria(self, criteria):
        pass

    def df_ready(self, data):
        return data

    def run(self):

        criteria = self.job.criteria

        if criteria.scc_device == '':
            logger.debug('%s: No scc device selected' % (self.table))
            self.job.mark_error("No SCC Device Selected")
            return False

        self.fill_criteria(criteria)

        columns = [col.name for col in self.table.get_columns(synthetic=False)]

        scc = DeviceManager.get_device(criteria.scc_device)
        data = scc.request(service=self.service,
                           resource=self.resource,
                           link=self.link,
                           criteria=self.criteria)
        if not data:
            raise SCCException("No data returned")
        # Convert to a DataFrame to make it easier to work with
        df = pandas.DataFrame(self.df_ready(data))

        for col in columns:
            if col not in df:
                raise KeyError("Table %s has no column '%s'" %
                               (self.job.table.name, col))

        df = df.ix[:, columns]

        self.data = df

        logger.info("SCC job %s returning %d rows of data" %
                    (self.job, len(self.data)))
        return True


class BaseSCCStatsQuery(BaseSCCQuery):
    """Base class for query of cmc.stats service.

    :param service: string, the name of service
    :param link: string, link name to get the response
    :param val_cols: list of name of non-key columns
    :param key_col: string, name of key column
    """
    service = 'cmc.stats'
    link = 'report'
    val_cols = []
    key_col = None

    def df_ready(self, resp_data):
        """convert the response data to a list of dicts, so that the data
        can be easily converted into pandas dataframe.

        :param resp_data: list of dicts, each dict is as
           { key: val, 'data': [v1, v2, ...] }

        example:
           { key: val, 'data': [v1, v2, v3, v4]}
           val_cols: ['wan_in', 'wan_out', 'lan_in', 'lan_out']

        result: {key: val, 'wan_in': v1, 'wan_out': v2,
                 'lan_in': v3, 'lan_out': v4}
        """
        ret = []
        if self.val_cols and self.key_col:
            for rec in resp_data:
                _dict = (dict((k, v)
                         for k, v in zip(self.val_cols, rec['data'])))
                _dict[self.key_col] = rec[self.key_col]
                ret.append(_dict)
        return ret

    def fill_criteria(self, criteria):
        """Add start_time and end_time to the criteria dict"""
        self.criteria = {'start_time': datetime_to_seconds(criteria.starttime),
                         'end_time': datetime_to_seconds(criteria.endtime)}


class SCCThroughputQuery(BaseSCCStatsQuery):
    """This class run the query to get the throughput data of a SCC device"""
    resource = 'throughput'
    val_cols = ['wan_in', 'wan_out', 'lan_in', 'lan_out']
    key_col = 'timestamp'

    def fill_criteria(self, criteria):
        super(SCCThroughputQuery, self).fill_criteria(criteria)

        self.criteria['device'] = criteria.device_id


class BaseSCCApplInvtQuery(BaseSCCQuery):
    """Base class for SCC appliance_inventory service query"""
    service = 'cmc.appliance_inventory'
    link = 'get'


class SCCAppliancesQuery(BaseSCCApplInvtQuery):
    """This class run the query to get the appliances data of a SCC device"""
    resource = 'appliances'

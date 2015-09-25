# Copyright (c) 2015 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.


from steelscript.scc.core import SCC


def new_device_instance(*args, **kwargs):
    # Used by DeviceManager to create a SCC Service instance
    return SCC(*args, **kwargs)

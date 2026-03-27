# coding=utf-8
"""Methods to write Dragonfly Energy Transfer Stations (ETS) to OpenStudio."""
from __future__ import division


def heat_pump_ets_to_openstudio(ets_dict, os_model):
    """Convert a dictionary of building with fifth_gen_ets_parameters to OpenStudio.

    Args:
        ets_dict: A building dictionary with a "Fifth Gen Heat Pump"
            ets_model to be converted into building-side thermal loops.
        os_model: The OpenStudio Model to which the loops will be added.
    """
    return


def heat_exchanger_ets_to_openstudio(ets_dict, os_model):
    """Convert a dictionary of building with ets_indirect_parameters to OpenStudio.

    Args:
        ets_dict: A building dictionary with a "Indirect Heating and Cooling"
            ets_model to be converted into building-side thermal loops.
        os_model: The OpenStudio Model to which the loops will be added.
    """
    return

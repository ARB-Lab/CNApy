"""UI independent computations"""

from typing import Dict, Tuple

import cobra
import numpy
from cobra.util.array import create_stoichiometric_matrix

import efmtool_link.efmtool4cobra as efmtool4cobra
import efmtool_link.efmtool_extern as efmtool_extern
from cnapy.flux_vector_container import FluxVectorMemmap

def efm_computation(model: cobra.Model, scen_values: Dict[str, Tuple[float, float]], constraints: bool):
    stdf = create_stoichiometric_matrix(
        model, array_type='DataFrame')
    reversible, irrev_backwards_idx = efmtool4cobra.get_reversibility(
        model)
    if len(irrev_backwards_idx) > 0:
        irrev_back = numpy.zeros(len(reversible), dtype=numpy.bool)
        irrev_back[irrev_backwards_idx] = True
    scenario = {}
    if constraints:
        for r in scen_values.keys():
            (vl, vu) = scen_values[r]
            if vl == vu and vl == 0:
                r_idx = stdf.columns.get_loc(r)
                reversible = numpy.delete(reversible, r_idx)
                del stdf[r]
                if len(irrev_backwards_idx) > 0:
                    irrev_back = numpy.delete(irrev_back, r_idx)
                scenario[r] = (0, 0)
    if len(irrev_backwards_idx) > 0:
        irrev_backwards_idx = numpy.where(irrev_back)[0]
        stdf.values[:, irrev_backwards_idx] *= -1
    work_dir = efmtool_extern.calculate_flux_modes(
        stdf.values, reversible, return_work_dir_only=True)
    reac_id = stdf.columns.tolist()
    if work_dir is None:
        ems = None
    else:
        ems = FluxVectorMemmap('efms.bin', reac_id,
                                containing_temp_dir=work_dir)
        if len(irrev_backwards_idx) > 0:
            ems.fv_mat[:, irrev_backwards_idx] *= -1

    return (ems, scenario)

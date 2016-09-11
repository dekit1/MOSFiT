from math import isnan

import astropy.constants as c
import astropy.units as u
import numpy as np

from ...constants import DAY_CGS, FOUR_PI
from ..module import Module

CLASS_NAME = 'Diffusion'


class Diffusion(Module):
    """Diffusion transform.
    """

    N_INT_TIMES = 100

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def process(self, **kwargs):
        self._t_explosion = kwargs['texplosion']
        self._kappa = kwargs['kappa']
        self._kappa_gamma = kwargs['kappagamma']
        self._m_ejecta = kwargs['mejecta']
        self._v_ejecta = kwargs['vejecta']
        self._times = kwargs['times']
        self._luminosities = kwargs['luminosities']
        self._times_since_exp = [x - self._t_explosion for x in self._times]
        self._tau_diff = np.sqrt(2.0 * self._kappa * self._m_ejecta * c.M_sun /
                                 (13.7 * c.c *
                                  (self._v_ejecta * u.km / u.s))).cgs.value
        self._trap_coeff = (3.0 * self._kappa_gamma * self._m_ejecta *
                            c.M_sun / (FOUR_PI *
                                       (self._v_ejecta * u.km /
                                        u.s)**2)).cgs.value
        td, A = self._tau_diff, self._trap_coeff

        new_lum = []
        for tse in self._times_since_exp:
            if tse <= 0.0:
                new_lum.append(0.0)
                continue
            te = tse * DAY_CGS
            int_times = np.linspace(0.0, tse, self.N_INT_TIMES)
            int_lums = np.interp(int_times, self._times_since_exp,
                                 self._luminosities)
            int_times = [x * DAY_CGS for x in int_times]
            int_arg = [
                2.0 * l * t / td**2 *
                np.exp((t**2 - te**2) / td**2) * (1.0 - np.exp(-A / te**2))
                for t, l in zip(int_times, int_lums)
            ]
            int_arg = [0.0 if isnan(x) else x for x in int_arg]
            new_lum.append(np.trapz(int_arg, int_times))
        return {'luminosities': new_lum}

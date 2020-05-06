# Epidexus - Agent Based Location-Graph Epidemic Simulation
# One Location - A simple scenario, emulating basic SEIR models.
#
# Copyright (C) 2020  Karl D. Hansen, Aalborg University <kdh@es.aau.dk>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
import numpy as np
from datetime import datetime, timedelta
from .. import EpidexusModel
from ..world_creation import create_family

class OneLocation:
    def __init__(self, num_people: int, num_infected_people: int,
                 infection_rate: float,
                 start_date: datetime, sim_time_step=timedelta(hours=1)):
        self.sim_model = EpidexusModel(start_date, sim_time_step=sim_time_step)
        self._people, self._home_location = create_family(self.sim_model, num_people)
        for i in range(num_infected_people):
            self._people[i].infect()
        self._initial_rate = infection_rate
        self._home_location.infection_rate = infection_rate

    def set_seed(self, new_seed: int):
        np.random.seed(new_seed)

    @property
    def control_variable(self):
        return self._u

    @control_variable.setter
    def control_variable(self, u):
        self._u = u
        self._home_location.infection_rate = self._initial_rate * (1-u)

    def simulate(self, interval: timedelta):
        sim_until = self.sim_model.current_date + interval
        while(self.sim_model.current_date < sim_until):
            self.sim_model.step()



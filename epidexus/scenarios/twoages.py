# Epidexus - Agent Based Location-Graph Epidemic Simulation
# Two Ages - A simple scenario, emulating basic SEIR models for two age groups.
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
from ..itinerary_entries import DailyItineraryEntry
from ..world_creation import create_family

class TwoAges:
    def __init__(self, num_young: int, num_old: int,
                 infection_rate_young: float, infection_rate_old: float,
                 start_date: datetime, sim_time_step=timedelta(hours=1),
                 meeting_duration=timedelta(hours=3),
                 num_infected_young = 0, num_infected_old = 0):

        self.sim_model = EpidexusModel(start_date, sim_time_step=sim_time_step)

        self._old_people, self._old_location = create_family(self.sim_model, num_old)
        for p in self._old_people:
            p.age = 80
        for i in range(num_infected_old):
            self._old_people[i].infect()
        self._initial_rate_old = infection_rate_old
        self._old_location.infection_rate = infection_rate_old
        self.restriction_old = 0

        self._meet_old_it = DailyItineraryEntry(self._old_location, start_date, start_date+meeting_duration)
        self._initial_meeting_duration = meeting_duration
        self.restriction_young_to_old = 0

        self._young_people, self._young_location = create_family(self.sim_model, num_young)
        for p in self._young_people:
            p.age = 30
            p.itinerary.add_entry(self._meet_old_it)
        for i in range(num_infected_young):
            self._young_people[i].infect()
        self._initial_rate_young = infection_rate_young
        self._young_location.infection_rate = infection_rate_young
        self.restriction_young = 0

    def set_seed(self, new_seed: int):
        np.random.seed(new_seed)

    @property
    def restriction_young(self):
        return self._u11

    @restriction_young.setter
    def restriction_young(self, u):
        self._u11 = u
        self._young_location.infection_rate = self._initial_rate_young * (1-u)

    @property
    def restriction_old(self):
        return self._u11

    @restriction_old.setter
    def restriction_old(self, u):
        self._u22 = u
        self._old_location.infection_rate = self._initial_rate_old * (1-u)

    @property
    def restriction_young_to_old(self):
        return self._u12

    @restriction_young_to_old.setter
    def restriction_young_to_old(self, u):
        self._u12 = u
        self._meet_old_it.leave_when = self._meet_old_it.go_when + self._initial_meeting_duration * (1-u)

    def simulate(self, interval: timedelta):
        sim_until = self.sim_model.current_date + interval
        while(self.sim_model.current_date < sim_until):
            self.sim_model.step()



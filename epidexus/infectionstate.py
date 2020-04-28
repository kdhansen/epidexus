# Epidexus - Agent Based Location-Graph Epidemic Simulation
# Infection State - Tracks the infection in a person
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

from datetime import datetime, timedelta
from enum import Enum


class SEIR(Enum):
    """Enumeration of the standard parameters for
    susceptible, exposed, infected and recovered.
    """
    SUSCEPTIBLE = 0
    EXPOSED = 1
    INFECTED = 2
    RECOVERED = 3


class InfectionState:
    """Tracks and updates the infection of a person."""

    def __init__(self, seir=SEIR.SUSCEPTIBLE, incubation_time=timedelta(days=4),
                 recovering_time=timedelta(days=10)):
        self.seir = seir
        self.infected_when = None
        self.incubation_time = incubation_time
        self.recovering_time = recovering_time

    def __str__(self):
        return self.seir.name.capitalize()

    def is_suceptible(self) -> bool:
        if self.seir == SEIR.SUSCEPTIBLE:
            return True
        else:
            return False

    def infect(self, when: datetime) -> bool:
        if self.seir == SEIR.SUSCEPTIBLE:
            self.seir = SEIR.EXPOSED
            self.infected_when = when
            return True
        else:
            return False

    def is_infected(self) -> bool:
        if self.seir == SEIR.INFECTED:
            return True
        else:
            return False

    def update(self, current_time):
        if (self.seir is SEIR.EXPOSED and
                self.infected_when + self.incubation_time < current_time):
            self.seir = SEIR.INFECTED
        elif (self.seir is SEIR.INFECTED and
                self.infected_when + self.incubation_time + self.recovering_time < current_time):
            self.seir = SEIR.RECOVERED
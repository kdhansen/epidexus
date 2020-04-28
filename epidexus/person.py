# Epidexus - Agent Based Location-Graph Epidemic Simulation
# Person - The main character of this simulation
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

from enum import Enum
from mesa import Agent
import numpy.random
from .model import EpidexusModel
from .infectionstate import InfectionState, SEIR
from .itinerary import Itinerary
from .location import Location


class Gender(Enum):
    UNKNOWN = 0
    MALE = 1
    FEMALE = 2

    def __str__(self):
        return self.name.capitalize() # pylint: disable=no-member


class Person(Agent):
    """The main character in this simulation."""

    def __init__(self, model: EpidexusModel,
                 home_location: Location, seir=SEIR.SUSCEPTIBLE,
                 age=0, gender=Gender.UNKNOWN):
        super().__init__(model.next_id(), model)

        self.age = age
        self.gender = gender

        self.itinerary = Itinerary()

        # SEIR(D)
        self.infection_state = InfectionState(seir)

        # Setup home location
        self.home_location = home_location
        if not home_location.go_here(self):
            raise Exception("Home location is not available initially.")
        self.current_location = home_location

    def __str__(self):
        return ("Person id: {}, age: {}, gender: {}, infection state: {}".format(self.unique_id, self.age, self.gender, self.infection_state))

    def infect(self):
        self.infection_state.infect(self.model.current_date)

    def advance(self):
        """The agent moves in the advance function."""
        self.infection_state.update(self.model.current_date) # Internal inf. state is updated before moving.

        scheduled_location = self.itinerary.get_location(
            self.model.current_date)
        if scheduled_location is None:  # If there is no place to go; go home.
            self.__change_location(self.home_location)
        else:
            self.__change_location(scheduled_location)

    def __change_location(self, new_location):
        """Changes location of the agent."""
        if new_location is not self.current_location:
            if new_location.go_here(self):
                self.current_location.leave_here(self)
                self.current_location = new_location

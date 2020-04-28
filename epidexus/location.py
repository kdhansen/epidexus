# Epidexus - Agent Based Location-Graph Epidemic Simulation
# Location - The base class for locations where Agents go.
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

import numpy.random
from functools import reduce
from mesa import Agent
from .model import EpidexusModel

class Location(Agent):
    """Represents a physical location persons can go to.

    Together with Person, this is one of the main classes
    in this simulation.

    It inherits Agent, in that the Location-Agents are drivers
    for evaluating infections. Person-Agents are drivers in moving
    persons between locations.
    """

    def __init__(self, model: EpidexusModel, name="", infection_probability=0.0):
        # Initially, everybody is allowed in.
        super().__init__(model.next_id(), model)
        self.access_policy = lambda person: True
        self.name = name
        self.persons_here = []
        self.infection_probability = infection_probability

    def __str__(self):
        return ("Location id: {}, name: {}".format(self.unique_id, self.name))

    def set_access_policy(self, policy) -> None:
        """Sets the access policy of this location.

        Arguments:
        policy -- function taking a person as parameter,
                  returning true if they are allowed to enter the location.
        """
        self.access_policy = policy

    def go_here(self, person) -> bool:
        """Registers an agent at this location.

        If this function returns False, the agent is
        not allowed to come in and must relocate
        itself.
        """
        is_person_allowed = self.access_policy(person)
        if is_person_allowed:
            self.persons_here.append(person)
        return is_person_allowed

    def leave_here(self, person) -> None:
        """Unregisters a person at the location."""
        self.persons_here.remove(person)

    # def step(self):
    #     """Infections are evaluated in the step function."""
    #     susceptible_people = []
    #     num_infectious_people = 0
    #     for p in self.persons_here:
    #         if p.infection_state.is_suceptible():
    #             susceptible_people.append(p)
    #         elif p.infection_state.is_infected():
    #             num_infectious_people += 1

    #     prob_of_no_infection = (1-self.infection_probability)**num_infectious_people
    #     for p in susceptible_people:
    #         if numpy.random.uniform() > prob_of_no_infection:
    #             p.infect()
    def step(self):
        """Infections are evaluated in the step function."""
        num_infectious_people = reduce(lambda x,p: x+1 if p.infection_state.is_infected() else x,
                                       self.persons_here, 0)
        if num_infectious_people == 0:
            return

        prob_of_no_infection = (1-self.infection_probability)**num_infectious_people
        for p in self.persons_here:
            if (p.infection_state.is_suceptible()
                    and numpy.random.uniform() > prob_of_no_infection):
                p.infect()

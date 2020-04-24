# Epidexus - Agent Based Location-Graph Epidemic Simulation
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

from bisect import insort
from copy import copy
from datetime import datetime, timedelta
from enum import Enum
from mesa import Agent, Model
from mesa.time import SimultaneousActivation
from mesa.datacollection import DataCollector
import numpy.random
import logging


class EpidexusModel(Model):
    """The main simulation model.

    This is the entry point for MESA-based simulations.
    """
    def __init__(self, start_date: datetime, sim_time_step=timedelta(minutes=15)):
        super().__init__()
        self.schedule = SimultaneousActivation(self)
        self.current_date = start_date
        self.sim_time_step = sim_time_step

        self.datacollector = DataCollector(model_reporters={"S": self.report_s,
                                                            "E": self.report_e,
                                                            "I": self.report_i,
                                                            "R": self.report_r})
        self.seir_counts = [0, 0, 0, 0]

        logging.basicConfig(filename='debug.log',level=logging.DEBUG)
        logging.info("-- Started Epidexus Simulation --")
        logging.info("Current date: " + str(self.current_date))
        logging.info("Simulation time step: " + str(self.sim_time_step))
        logging.info("---------------------------------")

    def step(self):
        last_date = copy(self.current_date)
        self.current_date = self.current_date + self.sim_time_step

        # Report SEIR only once a day
        if self.current_date.date() > last_date.date():
            self.count_seir()
            self.datacollector.collect(self)

        self.schedule.step()

    def add_person(self, person: Agent):
        self.schedule.add(person)
        logging.debug("Added person: " + str(person))

    def count_seir(self):
        """Count the agents in each bin.

        Run this function before the report_x functions to update
        the counts. This is to avoid iterating over all agent for
        each of the four reporters.
        """
        self.seir_counts = [0, 0, 0, 0]
        for a in self.schedule.agents:
            self.seir_counts[a.infection_state.seir.value] += 1

    def report_s(self, model):
        return self.seir_counts[0]

    def report_e(self, model):
        return self.seir_counts[1]

    def report_i(self, model):
        return self.seir_counts[2]

    def report_r(self, model):
        return self.seir_counts[3]


class Location:
    """Represents a physical location persons can go to.

    Together with Person, this is one of the main classes
    in this simulation.
    """

    def __init__(self, name="", infection_probability=0.0):
        # Initially, everybody is allowed in.
        self.access_policy = lambda person: True
        self.name = name
        self.persons_here = []
        self.infection_probability = infection_probability

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


class ItineraryEntry:
    """Entry to insert into an Itinerary.

    The entry tells when the person should go to a Location and for how
    long to stay. It also has a rescheduling function to continuously
    keep the persons itinerary filled.

    Arguments:
    location -- the Location the person is sent to
    go_when -- the time the person should go to the location
    leave_when -- the amount of time the person should stay
    """
    def __init__(self, location: Location, go_when: datetime, leave_when: datetime):
        self.location = location
        self.go_when = go_when
        self.leave_when = leave_when

    def __lt__(self, other):
        return self.go_when < other.go_when

    def reschedule(self, current_time: datetime):
        """Reschedules a new appointment on the itinerary

        This base class returns None, meaning it is not a recurring
        event. Subclasses can return a new ItineraryEntry.
        """
        return None


class Itinerary:
    """Holds the weekly itinerary for a person."""

    def __init__(self):
        self.the_itinerary = []

    def add_entry(self, new_entry: ItineraryEntry):
        """Add a new entry on the itinerary.

        The entry is sorting-inserted into the itinerary according
        to the start time of the entries, so that the next relevant
        entry is always first in the list.
        """
        insort(self.the_itinerary, new_entry)

    def get_location(self, at_time: datetime):
        """Get the next location on the itinerary.

        If there is no active next location in the itinerary,
        the function returns None, meaning that the Person should
        go to their default location (probably home).
        """
        while len(self.the_itinerary) > 0:
            # If there is an item but it is not time yet, go home.
            if self.the_itinerary[0].go_when > at_time:
                return None
            # If it is time and it's not yet time to go home, go to location.
            if self.the_itinerary[0].go_when <= at_time < self.the_itinerary[0].leave_when:
                return self.the_itinerary[0].location
            # Time is up, delete the item and add a rescheduled one, check the itinerary again.
            if self.the_itinerary[0].leave_when <= at_time:
                new_entry = self.the_itinerary[0].reschedule(at_time)
                del self.the_itinerary[0]
                self.add_entry(new_entry)
        # If there is no items, go home
        return None


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


class Gender(Enum):
    UNKNOWN = 0
    MALE = 1
    FEMALE = 2

    def __str__(self):
        return self.name.capitalize() # pylint: disable=no-member


class Person(Agent):
    """The main character in this simulation."""

    def __init__(self, unique_id: int, model: EpidexusModel,
                 home_location: Location, seir=SEIR.SUSCEPTIBLE,
                 age=0, gender=Gender.UNKNOWN):
        super().__init__(unique_id, model)

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

    def step(self):
        """Infections are evaluated in the step function."""
        if self.infection_state.is_suceptible():
            for p in self.current_location.persons_here:
                if (p.infection_state.is_infected()
                        and numpy.random.uniform() < self.current_location.infection_probability):
                    self.infect()

        self.infection_state.update(self.model.current_date)

    def advance(self):
        """The agent moves in the advance function."""
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

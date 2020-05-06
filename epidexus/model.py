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

from copy import copy
from datetime import datetime, timedelta
from mesa import Agent, Model
from mesa.time import SimultaneousActivation
from mesa.datacollection import DataCollector
import logging
from typing import List


class EpidexusModel(Model):
    """The main simulation model.

    This is the entry point for MESA-based simulations.
    """
    def __init__(self, start_date: datetime, sim_time_step=timedelta(minutes=15)):
        super().__init__()
        self.schedule = SimultaneousActivation(self)
        self.current_date = start_date
        self.sim_time_step = sim_time_step

        self.datacollector = DataCollector(model_reporters={"Date": self.report_current_date,
                                                            "S": self.report_s,
                                                            "E": self.report_e,
                                                            "I": self.report_i,
                                                            "R": self.report_r})
        self.seir_counts = [0, 0, 0, 0]
        self.persons = []
        self.locations =[]

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
        self.persons.append(person)
        logging.debug("Added person: " + str(person))

    def add_location(self, location: Agent):
        self.schedule.add(location)
        self.locations.append(location)
        logging.debug("Added location: " + str(location))

    def add_locations(self, locations: List[Agent]):
        for l in locations:
            self.add_location(l)

    def count_seir(self):
        """Count the agents in each bin.

        Run this function before the report_x functions to update
        the counts. This is to avoid iterating over all agent for
        each of the four reporters.
        """
        self.seir_counts = [0, 0, 0, 0]
        for a in self.persons:
            self.seir_counts[a.infection_state.seir.value] += 1

    def report_s(self, model):
        return self.seir_counts[0]

    def report_e(self, model):
        return self.seir_counts[1]

    def report_i(self, model):
        return self.seir_counts[2]

    def report_r(self, model):
        return self.seir_counts[3]

    def report_current_date(self, model):
        return self.current_date
# Epidexus - Agent Based Location-Graph Epidemic Simulation
# World Creators Module - Facilities to generate virtual worlds of locations and agents.
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

from typing import List
from epidexus import EpidexusModel, Location, Person, ItineraryEntry
from numpy.random import normal


def create_family(sim_model: EpidexusModel, num_people: int):
    """Creates a home and people living in it.

    Creates the [num_people] number of family members with a common home
    location. The people are added to the simulation model scheduler. A list of
    people are also returned, e.g. to be used in subsequent claiming from
    schools and workplaces.

    In addition the home location is also returned.

    The home is named after the first person's unique id.
    """
    if num_people < 1:
        raise ValueError(
            "Number of people in a family should be greater than 1.")

    people = []
    primary_id = sim_model.next_id()
    home_loc = Location("Home-" + str(primary_id), infection_probability=0.05)
    primary_person = Person(primary_id, sim_model, home_loc)
    sim_model.add_person(primary_person)
    people.append(primary_person)
    for i in range(num_people-1):  # pylint: disable=unused-variable
        p = Person(sim_model.next_id(), sim_model, home_loc)
        sim_model.add_person(p)
        people.append(p)
    return people, home_loc

def create_family_prob(sim_model: EpidexusModel,
                       num_adult_mean: float, num_adult_sd: float,
                       age_adult_mean: float, age_adult_sd: float,
                       num_children_mean: float, num_children_sd: float,
                       age_children_mean: float, age_children_sd: float):
    """Creates a home and people living in it according to probability distributions.

    Like the create_family, this function creates the a number of family
    members with a common home location. The people are added to the simulation
    model scheduler. A list of people are also returned, e.g. to be used in
    subsequent claiming from schools and workplaces. In addition the home
    location is also returned.

    TODO: The age distribution probably should be a gamma or other non-negative distribution.

    The home is named after the first person's unique id.
    """
    people = []
    primary_id = sim_model.next_id()
    home_loc = Location("Home-" + str(primary_id), infection_probability=0.1)
    #Generate adults (at least one)
    num_adults = round(normal(num_adult_mean, num_adult_sd))
    age = round(normal(age_adult_mean, age_adult_sd))
    if age < 0:
        age = 0
    primary_person = Person(primary_id, sim_model, home_loc, age=age)
    sim_model.add_person(primary_person)
    people.append(primary_person)
    for i in range(num_adults-1):  # pylint: disable=unused-variable
        age = round(normal(age_adult_mean, age_adult_sd))
        if age < 0:
            age = 0
        p = Person(sim_model.next_id(), sim_model, home_loc, age=age)
        sim_model.add_person(p)
        people.append(p)
    #Generate kids
    num_kids = round(normal(num_children_mean, num_children_sd))
    for i in range(num_kids):  # pylint: disable=unused-variable
        age = round(normal(age_children_mean, age_children_sd))
        if age < 0:
            age = 0
        p = Person(sim_model.next_id(), sim_model, home_loc, age=age)
        sim_model.add_person(p)
        people.append(p)

    return people, home_loc


def claim_by_age(people: List[Person], it_entry: ItineraryEntry, min_age: int, max_age: int, max_num=1):
    """Location makes a claim on a number of people by age.

    Returns -- A list with the claimed persons removed"""
    count = 0
    unclaimed = []
    for p in people:
        if ((min_age <= p.age <= max_age) and count < max_num):
            p.itinerary.add_entry(it_entry)
            count +=1
        else:
            unclaimed.append(p)
    return unclaimed
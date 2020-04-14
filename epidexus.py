from bisect import insort
from datetime import datetime, timedelta
from enum import Enum
from mesa import Agent, Model
from mesa.time import SimultaneousActivation
import logging


class EpidexusModel(Model):
    def __init__(self, start_date: datetime, sim_time_step=timedelta(minutes=15)):
        self.schedule = SimultaneousActivation(self)
        self.current_date = start_date
        self.sim_time_step = sim_time_step

        logging.basicConfig(filename='debug.log',level=logging.DEBUG)
        logging.info("-- Started Epidexus Simulation --")
        logging.info("Current date: " + str(self.current_date))
        logging.info("Simulation time step: " + str(self.sim_time_step))
        logging.info("---------------------------------")

    def step(self):
        self.current_date = self.current_date + self.sim_time_step
        print(str(self.current_date))
        self.schedule.step()

    def add_person(self, person: Agent):
        self.schedule.add(person)
        logging.debug("Added person: " + str(person))


class Location:
    """Represents a physical location persons can go to

    Together with Person, this is one of the main classes
    in this simulation.
    """

    def __init__(self, name=""):
        # Initially, everybody is allowed in.
        self.access_policy = lambda person: True
        self.name = name
        self.persons_here = []

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
        not allowed to come in and must relocalize
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
    """Entry to insert into an Itinerary

    The entry tells when the person should go to a Location and for how
    long to stay. It also has a rescheduling function to continously
    keep the persons itinerary filled.

    Arguments:
    location -- the Location the person is sent to
    go_when -- the time the person should go
    for_how_long -- the amount of time the person should stay
    rescheduling_func -- a function taking the current time when the
                         person leaves returning a tuple of go_when and
                         for_how_long for the next time.
    """

    def __init__(self, location: Location, go_when: datetime, for_how_long: timedelta, reschedule_func):
        self.location = location
        self.go_when = go_when
        self.go_until = go_when + for_how_long
        self.__reschedule_func = reschedule_func

    def __lt__(self, other):
        return self.go_when < other.go_when

    def reschedule(self, current_time: datetime):
        t, dt = self.__reschedule_func(current_time)
        return ItineraryEntry(self.location, t, dt, self.__reschedule_func)


class Itinerary:
    """Holds the weekly itinerary for a person."""

    def __init__(self):
        self.the_itinerary = []

    def add_entry(self, new_entry: ItineraryEntry):
        insort(self.the_itinerary, new_entry)

    def get_location(self, at_time: datetime):
        while len(self.the_itinerary) > 0:
            # If there is an item but it is not time yet, go home.
            if self.the_itinerary[0].go_when > at_time:
                return None
            # If it is time and it's not yet time to go home, go to location.
            if self.the_itinerary[0].go_when <= at_time < self.the_itinerary[0].go_until:
                return self.the_itinerary[0].location
            # Time is up, delete the item and add a rescheduled one, check the itinerary again.
            if self.the_itinerary[0].go_until <= at_time:
                new_entry = self.the_itinerary[0].reschedule(at_time)
                del self.the_itinerary[0]
                self.add_entry(new_entry)
        # If there is no items, go home
        return None


class SEIR(Enum):
    """Enumeration of the standard parameters for
    susceptible, exposed, infected, recovered
    """
    SUSCEPTIBLE = 1
    EXPOSED = 2
    INFECTED = 3
    RECOVERED = 4


class InfectionState:
    """Tracks and updates the infection of a person"""

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
        return self.name.capitalize()


class Person(Agent):
    """The main character in this simulation"""

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
        """Infections are evaluated in the step function"""
        if self.infection_state.is_suceptible():
            for p in self.current_location.persons_here:
                if p.infection_state.is_infected():
                    # TODO: add probability here
                    self.infect()
                    print(str(self.unique_id) + " got exposed.")

        self.infection_state.update(self.model.current_date)

    def advance(self):
        """The agent moves in the advance function"""
        scheduled_location = self.itinerary.get_location(
            self.model.current_date)
        if scheduled_location is None:  # If there is no place to go; go home.
            self.__change_location(self.home_location)
        else:
            self.__change_location(scheduled_location)

    def __change_location(self, new_location):
        """Changes location of the agent"""
        if new_location is not self.current_location:
            if new_location.go_here(self):
                print("Agent-" + str(self.unique_id) + "@" +
                      self.current_location.name + " going to " + new_location.name)
                self.current_location.leave_here(self)
                self.current_location = new_location

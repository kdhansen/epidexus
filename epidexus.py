from bisect import insort
from datetime import datetime, timedelta
from mesa import Agent, Model
from mesa.time import SimultaneousActivation


class EpidexusModel(Model):
    def __init__(self):
        self.schedule = SimultaneousActivation(self)
        self.current_date = datetime(year=2020, month=4, day=1)
        self.sim_time_step = timedelta(minutes=15)

    def step(self):
        self.current_date += self.sim_time_step
        self.schedule.step()

    def add_person(self, person: Agent):
        self.schedule.add(person)



class Location:
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


class NormalDistribution:
    def __init__(self, mean, std_deviation):
        self.mean = mean
        self.std_deviation = std_deviation


class StaysHours(NormalDistribution):
    """Defines how long people usually stay at a location"""

    def __init__(self, mean, std_deviation):
        super().__init__(mean, std_deviation)


class ItenaryEntry:
    """Entry to insert into an Itenary

    The entry tells when the person should go to a Location and for how
    long to stay. It also has a rescheduling function to continously
    keep the persons itenary filled.
    """
    def __init__(self, location: Location, go_when: datetime, for_how_long: timedelta, reschedule_func):
        self.location = location
        self.go_when = go_when
        self.go_until = go_when + for_how_long
        self.reschedule_func = reschedule_func

    def __lt__(self, other):
        return self.go_when < other.go_when


class Itenary:
    """Holds the weekly itenary for a person."""

    def __init__(self):
        self.the_itenary = []

    def add_entry(self, new_entry: ItenaryEntry):
        insort(self.the_itenary, new_entry)

    def get_location(self, at_time: datetime):
        while len(self.the_itenary) > 0:
            # If there is an item but it is not time yet, go home.
            if self.the_itenary[0].go_when > at_time:
                return None
            # If it is time and it's not yet time to go home, go to location.
            if self.the_itenary[0].go_when < at_time < self.the_itenary[0].go_until:
                return self.the_itenary[0].location
            # Time is up, delete the item and add a rescheduled one, check the itenary again.
            if self.the_itenary[0].go_until < at_time:
                new_entry = self.the_itenary[0].reschedule_func()
                del self.the_itenary[0]
                self.add_entry(new_entry)
        # If there is no items, go home
        return None


class Person(Agent):
    def __init__(self, unique_id: int, home_location: Location, model: EpidexusModel):
        super().__init__(unique_id, model)

        # Affiliated locations
        self.itenary = Itenary()

        # SEIR(D)
        self.susceptible = True
        self.exposed = False
        self.incubation_ends = datetime()
        self.infected = False
        self.recovered = False
        self.deceased = False

        # Setup home location
        self.home_location = home_location
        if not home_location.go_here(self):
            raise Exception("Home location is not available initially.")
        self.current_location = home_location

    def step(self):
        """Infections are evaluated in the step function"""
        # Susceptible -> Exposed
        if self.susceptible:
            for p in self.current_location.persons_here:
                if p.infected:
                    # TODO: add probability here
                    self.susceptible = False
                    self.exposed = True
                    # TODO: probability and parameter for incubation time here
                    self.incubation_ends = self.model.current_date + \
                        timedelta(days=2)
                    print(str(self.unique_id) + " got exposed.")
        # Exposed -> Infected
        if self.exposed and self.incubation_ends < self.model.current_date:
            self.exposed = False
            self.infected = True
            # TODO: probability and parameter for infection time here
            self.infection_ends = self.model.current_date + timedelta(days=10)
            print(str(self.unique_id) + " got infected.")
        # Infected -> Recovered
        if self.infected and self.infection_ends < self.model.current_date:
            self.infected = False
            self.recovered = True
            print(str(self.unique_id) + " recovered.")
            # TODO: Maybe they died?

    def advance(self):
        """The agent moves in the advance function"""
        scheduled_location = self.itenary.get_location(self.model.current_date)
        if scheduled_location is None: # If there is no place to go; go home.
            self.__change_location(self.home_location)
        else:
            self.__change_location(scheduled_location)

    def __change_location(self, new_location):
        """Changes location of the agent"""
        if new_location is not self.current_location:
            if new_location.go_here():
                self.current_location.leave_here()
                self.current_location = new_location

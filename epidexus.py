from mesa import Agent, Model
from mesa.time import SimultaneousActivation

class Location:
  def __init__(self, name=""):
    self.is_closed = False
    self.name = name

  def set_policy(self, location_closed) -> None:
    """Sets the access policy of this location.

    Arguments:
    location_closed -- true if location is being closed.
    """
    self.is_closed = location_closed

  def go_here(self) -> bool:
    """Registers an agent at this location.

    If this function returns False, the agent is
    not allowed to come in and must relocalize
    itself.
    """
    return not self.closed

class NormalDistribution:
  def __init__(self, mean, std_deviation):
    self.mean = mean
    self.std_deviation = std_deviation

class StaysHours(NormalDistribution):
  """Defines how long people usually stay at a location"""
  def __init__(self, mean, std_deviation):
    super().__init__(mean, std_deviation)

class Schedule:
  """Describes when a person goes to a location and for how long"""
  def __init__(self):
    self.open_hours =[]
    self.stays_hours =[]
    for i in range(7):
      self.open_hours.append((0.0, 0.0))
      s = StaysHours(0.0, 0.0)
      self.stays_hours.append(s)

class Person(Agent):
  def __init__(self, unique_id, model):
    super().__init__(unique_id, model)
    self.locations = []

  def add_location(self, location, schedule) -> None:
    self.locations.append((location, schedule))

  def step(self):
    """Infections are evaluated in the step function"""
    print("Phew, didn't get infected!")

  def advance(self):
    """The agent moves in the advance function"""
    print("Moving on...")

class EpidexusModel(Model):
  def __init__(self):
    self.schedule = SimultaneousActivation(self)

    sh = Schedule()
    for i in range(7):
      sh.open_hours[i] = (0.0,24.0)

    ls = Location("Some School")
    ss = Schedule()
    for i in range(5):
      ss.open_hours[i] = (8,15)
      ss.stays_hours[i] = StaysHours(6, 1)
    for i in range(2):
      p = Person(i, self)
      h = Location("Home" + str(i))
      p.add_location(h, sh)
      p.add_location(ls,ss)
      self.schedule.add(p)

  def step(self):
    self.schedule.step()


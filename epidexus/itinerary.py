# Epidexus - Agent Based Location-Graph Epidemic Simulation
# Itinerary - List of locations the Agents visit
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
from datetime import datetime
from . import Location

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
                if new_entry is not None:
                    self.add_entry(new_entry)
        # If there is no items, go home
        return None
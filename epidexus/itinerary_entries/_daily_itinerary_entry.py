# Epidexus - Agent Based Location-Graph Epidemic Simulation
# Daily Itinerary Entry - Reschedules every day.
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
from typing import Tuple
from datetime import date, datetime, time, timedelta
from epidexus import Location, ItineraryEntry


class DailyItineraryEntry (ItineraryEntry):
    """A schedule that repeats every day."""

    def __init__(self, location: Location,
                 go_when: datetime, leave_when: datetime):
        super().__init__(location, go_when, leave_when)

    def reschedule(self, current_time: datetime):
        new_entry = copy(self)
        new_entry.go_when = self.go_when + timedelta(days=1)
        new_entry.leave_when = self.leave_when + timedelta(days=1)
        return new_entry

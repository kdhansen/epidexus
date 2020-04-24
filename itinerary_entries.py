# Epidexus - Agent Based Location-Graph Epidemic Simulation
# Itinerary Entries Module - Template Itinerary Entries for common uses.
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
from datetime import date, datetime, time, timedelta
from epidexus import Location, ItineraryEntry


class FixedWeekItineraryEntry (ItineraryEntry):
    """A fixed week schedule

    Set each day as a 2-tuple of come and go hour in datetime.time-format.
    E.g. FixedWeekItineraryEntry(date(2020, 4, 23) monday=(time(8,15),time(15)))
    will set a recurring schedule for every monday from 8.15 to 15.00 at the
    first monday after april 23rd 2020.

    Caution: The class does not check if the start date is in the past.
    It will happily place an itinerary entry in the past.
    """
    def __init__(self, location: Location, start_date: date, monday=None, tuesday=None, wednesday=None, thursday=None, friday=None, saturday=None, sunday=None):
        self._week_schedule = [monday, tuesday,
                               wednesday, thursday, friday, saturday, sunday]
        # Check if any hours were given
        if all(d is None for d in self._week_schedule):
            raise Exception("No come and go hours were defined.")

        valid_start_date = self.__next_valid_date(start_date)
        hours = self._week_schedule[valid_start_date.weekday()]
        # Minus operator is not available on time only datetime, so we'll convert
        come_at = datetime.combine(valid_start_date, hours[0])
        leave_at = datetime.combine(valid_start_date, hours[1])
        super().__init__(location, come_at, leave_at)

    def __next_valid_date(self, from_date: date):
        """Find the next day for which the hours are set.

        Arguments:
        from_date -- date to start the search from
        """
        for d in range(7):
            if self._week_schedule[(from_date.weekday()+d)%7] is not None:
                return from_date + timedelta(days=d)

    def reschedule(self, current_time: datetime):
        new_entry = copy(self)
        next_day = self.__next_valid_date(current_time.date())
        #If the next day is the current day and the come hours has passed,
        #then we will search on from tomorrow.
        if datetime.combine(next_day, self._week_schedule[next_day.weekday()][0]) < current_time:
            next_day = self.__next_valid_date(current_time.date() + timedelta(days=1))

        hours = self._week_schedule[next_day.weekday()]
        new_entry.go_when = datetime.combine(next_day, hours[0])
        new_entry.leave_when = datetime.combine(next_day, hours[1])
        return new_entry

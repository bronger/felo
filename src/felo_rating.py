#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#    felo_rating.py - Core library of the Felo program
#
#    Copyright © 2006 Torsten Bronger <bronger@physik.rwth-aachen.de>
#
#    This file is part of the Felo program.
#
#    Felo is free software; you can redistribute it and/or modify it under
#    the terms of the MIT licence:
#
#    Permission is hereby granted, free of charge, to any person obtaining a
#    copy of this software and associated documentation files (the "Software"),
#    to deal in the Software without restriction, including without limitation
#    the rights to use, copy, modify, merge, publish, distribute, sublicense,
#    and/or sell copies of the Software, and to permit persons to whom the
#    Software is furnished to do so, subject to the following conditions:
#
#    The above copyright notice and this permission notice shall be included in
#    all copies or substantial portions of the Software.
#
#    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
#    THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#    FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#    DEALINGS IN THE SOFTWARE.
#

"""Core library for the Felo program, with the Felo numbers calculating code.

Exported functions:

parse_felo_file() -- reads from a Felo file parameters, fencers, and bouts
write_felo_file() -- writes parameters, fencers, and bouts to a Felo file
calculate_felo_ratings() -- update the Felo ratings of fencers
expectation_value() -- returns the mean winning value of a fencer in a bout
prognosticate_bout() -- calculates the winning chance and the result in a bout

Exported classes:

Bout -- fencing bout
Fencer -- fencer and his/her Felo number

Exported variables: None

"""

__all__ = ["Bout", "Fencer", "parse_felo_file", "write_felo_file", "calculate_felo_ratings",
           "expectation_value", "prognosticate_bout"]

__version__ = "$Revision:  $"
# $Source:  $

import codecs, re, os.path, time
from subprocess import call, Popen, PIPE

datapath = os.path.abspath(os.path.dirname(__file__))

separator = "\s*\t+\s*"
"""Column separator in a Felo file"""

def clean_up_line(line):
    """Removes leading and trailing whitespace and comments from the line.
    """
    hash_position = line.find("#")
    if hash_position != -1:
        line = line[:hash_position]
    line = line.strip()
    return line
    
def parse_items(input_file, linenumber=0):
    """Parses key--value pairs in the input_file.  It stops parsing if a line
    starts with a special character.  Normally, this is a line made of
    e.g. equal signs that acts as a separator between the sections in the Felo
    file.

    Parameters:
    input_file -- an open file object where the items are read from.
    linenumer -- number of already read lines in the input_file.

    Return value:
    A dictionary with the key--value pairs, and the new number of already read
        lines.
    The new current number of lines aready read in the file.
    """
    items = {}
    line_pattern = re.compile("\s*(?P<name>[^\t]+?)"+separator+"(?P<value>.+?)\s*\\Z")
    for line in input_file:
        linenumber += 1
        line = clean_up_line(line)
        if not line: continue
        if line[0] in u"-=._:;,+*'~\"`´/\\%$!": break
        match = line_pattern.match(line)
        if not match:
            raise Error('Zeile muss nach dem Muster "Name <TAB> Anfangszahl" sein', input_file.name, linenumber)
        name, value = match.groups()
        try:
            items[name] = value
            items[name] = float(value)
            items[name] = int(value)
        except ValueError:
            pass
    return items, linenumber

class Bout(object):
    """Class for single bouts.

    It is not very active in the sense that is has many methods.  Actually it's
    just a container for the attributes of a bout.
    """
    def __init__(self, year, month, day, first_fencer="", second_fencer="",
                 points_first=0, points_second=0, fenced_to=10):
        """Class constructor.

        Parameters:
        year -- year of the bout.
        month -- month of the bout.
        day -- day of te bout.  This is a float because it may contain some
            sort of sub-index in order to bring the bouts of a day in an
            order.  It may have two digits after the decimal point.
        first_fencer -- name of the first fencer.
        second_fencer -- name of the second fencer.
        points_first -- points won by the first fencer.
        points_second -- points won by the second fencer.
        fenced_to -- winning points of the bout.  May be 0, 5, 10, or 15.  "0"
            means that the bout was part of a relay team competition.
        """
        self.year = int(year)
        self.month = int(month)
        self.day = float(day)
        self.first_fencer = first_fencer
        self.second_fencer = second_fencer
        self.points_first = int(points_first)
        self.points_second = int(points_second)
        self.fenced_to = int(fenced_to)

    def __cmp__(self, other):
        """If bouts are sorted with "sort()", they are sorted by their date,
        with early bouts first.
        """
        if cmp(self.year, other.year):
            return cmp(self.year, other.year)
        elif cmp(self.month, other.month):
            return cmp(self.month, other.month)
        else:
            return cmp(self.day, other.day)

    def __get_date(self):
        if self.day - int(self.day) < 0.001:
            return "%04d/%02d/%02d" % (self.year, self.month, self.day)
        elif 10*self.day - int(10*self.day) < 0.01:
            return "%04d/%02d/%04.1f" % (self.year, self.month, self.day)
        else:
            return "%04d/%02d/%05.2f" % (self.year, self.month, self.day)
    def __set_date(self, date):
        date_pattern = re.compile("\s*(?P<year>\\d{4})/(?P<month>\\d{1,2})/(?P<day>[\\d.]{1,5})\s*\\Z")
        match = date_pattern.match(date)
        if not match:
            raise Error("Ungueltiger Datumsstring")
        year, month, day = match.groups()
        self.year, self.month = int(year), int(month)
        self.day = float(day)
        try:
            self.day = int(day)
        except:
            pass
    date = property(__get_date, __set_date, doc="""The date of the bout in its
        string representation YYYY/MM/TT.II, where ".II" is the optional index.""")

    def daynumber(self):
        """The Julian day of the bout, not counting the sub-day fraction."""
        return julian_date(self.year, self.month, self.day)

def julian_date(year, month, day):
        """The Julian day of the date, not counting the sub-day fraction."""
        if month <= 2:
            month += 12
            year -= 1
        B = int(year/400) - int(year/100)
        return int(365.25*year) + int(30.6001*(month+1)) + B + 1720996 + int(day)

def calendar_date(daynumber):
    """The calendar date of a Julian day.  This function is the inverse of
    Bout.daynumber().

    Parameters:
    daynumber -- the Julian day of the date in question.

    Result:
    year, month, and day for the given date.  All integers.
    """
    a = int(daynumber + 0.5)
    b = int((a - 1867216.25) / 36524.25)
    c = a + b - int(b/4.0) + 1525
    d = int((c - 122.1) / 365.25)
    e = int(365.25 * d)
    f = int((c - e) / 30.6001)
    day = c - e - int(30.6001 * f)
    month = f - 1 - 12 * int(f/14.0)
    year = d - 4715 - int((7 + month) / 10.0)
    return year, month, day

def set_preliminary_felo_ratings(fencers, bout, parameters):
    """Calculates the new Felo numbers of the two fencers of a given bout and
    stores them at preliminary places in the fencer objects.  More accurately,
    the new Felo numbers are stored in the felo_rating_preliminary attribute of
    the fencers.  The reason is that some bouts may take place on the same day,
    without knowing the order.  Then only preliminary values are determined and
    merged with the real ones when all bouts of that day have been considered.

    Parameters:
    fencers -- a dictionary containing all fencers.  The two fencers in it
        which take part in the bout are modified.
    bout -- the bout that is to be calculated.
    parameters -- a dictionary with all Felo parameters.

    Result: None
    """
    first_fencer, second_fencer, points_first, points_second = \
        bout.first_fencer, bout.second_fencer, \
        bout.points_first, bout.points_second
    weightings = [1.0, 1.0, parameters["Gewichtung 10-er Gefecht"], parameters["Gewichtung 15-er Gefecht"]]
    weighting = weightings[bout.fenced_to/5]
    total_points = points_first + points_second
    if total_points == 0:
        result_first = 0.5
    else:
        result_first = float(points_first) / total_points
    if fencers[first_fencer].freshman and fencers[second_fencer].freshman:
        # Two freshmen, so the bout cannot be counted at all
        return
    if fencers[first_fencer].freshman:
        fencers[first_fencer].total_weighting += weighting
        fencers[first_fencer].total_result += (result_first - 0.5) * weighting
        fencers[first_fencer].total_felo_rating_opponents += \
            fencers[second_fencer].felo_rating_exact * weighting
        return
    elif fencers[second_fencer].freshman:
        fencers[second_fencer].total_weighting += weighting
        Freshman.freshmen[second_fencer].total_result += (0.5 - result_first) * weighting
        Freshman.freshmen[second_fencer].total_felo_rating_opponents += \
            fencers[first_fencer].felo_rating_exact * weighting
        return
    # Use current (rather than preliminary) numbers for the calculation.  Just
    # don't *store* the results in the real attributes.
    felo_first = fencers[first_fencer].felo_rating_exact
    felo_second = fencers[second_fencer].felo_rating_exact
    expectation_first = 1 / (1 + 10**((felo_second - felo_first)/400.0))
    improvement_first = (result_first - expectation_first) * weighting
    fencers[first_fencer].felo_rating_preliminary += fencers[first_fencer].k_factor * improvement_first
    fencers[second_fencer].felo_rating_preliminary -= fencers[second_fencer].k_factor * improvement_first
    Fencer.fencers_with_preliminary_felo_rating.add(fencers[first_fencer])
    Fencer.fencers_with_preliminary_felo_rating.add(fencers[second_fencer])

    fencers[first_fencer].fenced_points_preliminary += total_points
    fencers[second_fencer].fenced_points_preliminary += total_points

def parse_bouts(input_file, linenumber, fencers, parameters):
    """Reads bouts from a Felo file, starting at the current position in that file.
    It reads till the end of the file since the bouts are the last section in a
    Felo file.

    Parameters:
    input_file -- an open file object where the items are read from.
    linenumber -- number of already read lines in the input_file.
    fencers -- a dictionary with all fencers.  It remains untouched.
    parameters -- a dictionary with all Felo parameters.

    Return values:
    A list with all bouts that were read.
    """
    line_pattern = re.compile("\s*(?P<year>\\d{4})/(?P<month>\\d{1,2})/(?P<day>[\\d.]{1,5})"
                               +separator+
                               "(?P<erster>.+?)\s*--\s*(?P<zweiter>.+?)"+separator+
                               "(?P<points_first>\\d+):(?P<points_second>\\d+)"+
                               "(?:/(?P<fenced_to>\\d+))?\s*\\Z")
    bouts = []
    for line in input_file:
        linenumber += 1
        line = clean_up_line(line)
        if not line: continue
        match = line_pattern.match(line)
        if not match:
            raise Error('Zeile muss nach dem Muster "JJJJ/MM/TT <TAB> Name1 -- Name2 <TAB> Punkte1:Punkte2" sein',
                        input_file.name, linenumber)
        year, month, day, first_fencer, second_fencer, points_first, points_second, fenced_to = \
            match.groups()
        points_first, points_second = int(points_first), int(points_second)
        if not fenced_to:
            fenced_to = max(points_first, points_second)
        else:
            fenced_to = int(fenced_to)
        if fenced_to not in (0, 5, 10, 15):
            raise Error("Gefecht wurde nicht auf 5, 10 oder 15 gefochten", input_file.name, linenumber)
        if fenced_to > 0 and (points_first > fenced_to or points_second > fenced_to):
            raise Error("Einer hat mehr Punkte als die Siegerpunktezahl", input_file.name, linenumber)
        if first_fencer not in fencers:
            raise Error('Fencer "%s" is unknown' % first_fencer, input_file.name, linenumber)
        if second_fencer not in fencers:
            raise Error('Fencer "%s" is unknown' % second_fencer, input_file.name, linenumber)
        bouts.append(Bout(year, month, day, first_fencer, second_fencer,
                                points_first, points_second, fenced_to))
    return bouts

def parse_felo_file(filename):
    """Reads from a Felo file parameters, fencers, and bouts.

    Parameters:
    filename -- path of the Felo file.

    Return values:
    Felo parameters as a dictionary, a list with all really in the file given
    parameters, fencers as a dictionary (name: Fencer object), bouts as a list.
    """
    felo_file = codecs.open(filename, "r", "utf-8")

    parameters, linenumber = parse_items(felo_file)
    given_parameters = list(parameters)
    parameters.setdefault(u"k-Faktor Top-Fechter", 25)
    parameters.setdefault(u"Elo-Zahl Top-Fechter", 2400)
    parameters.setdefault(u"k-Faktor Rest", 32)
    parameters.setdefault(u"k-Faktor Einsteiger", 40)
    parameters.setdefault(u"Einzeltreffer Einsteiger", 100)
    parameters.setdefault(u"Minimum Elo-Zahl", 1200)
    parameters.setdefault(u"Gewichtung 10-er Gefecht", 1.73)
    parameters.setdefault(u"Gewichtung 15-er Gefecht", 3.0)
    parameters.setdefault(u"Minimal-Gewichtung Einsteiger", 10.0)
    # The groupname is used e.g. for the file names of the plots.  It defaults
    # to the name of the Felo file.
    parameters.setdefault(u"Gruppenname", os.path.splitext(os.path.split(filename)[1])[0].capitalize())
    parameters.setdefault(u"Ausgabeverzeichnis", os.path.abspath(os.path.dirname(filename)))
    parameters.setdefault(u"Plot-Tics Mindestabstand", 7)
    parameters.setdefault(u"Plot Mindestdatum", "1500/00/00")
    parameters.setdefault(u"Plot maximale Tage", "366")

    initial_felo_ratings, linenumber = parse_items(felo_file, linenumber)
    fencers = {}
    for name, initial_felo_rating in initial_felo_ratings.items():
        aktueller_fechter = Fencer(name, initial_felo_rating, parameters)
        fencers[aktueller_fechter.name] = aktueller_fechter

    bouts = parse_bouts(felo_file, linenumber, fencers, parameters)
    felo_file.close()
    return parameters, given_parameters, fencers, bouts

def fill_with_tabs(text, tab_col):
    """Adds tabs to a string until a certain column is reached.

    Parameters:
    text -- the string that should be expanded to a certain column.
    tab_col -- the tabulator column to which should be filled up.  It is *not*
        a character column, so a value of, say, "4" means character column 32.

    Return value:
    The expanded string, i.e., "text" plus one or more tabs.
    """
    number_of_tabs = tab_col - len(text.expandtabs()) / 8
    return text + max(number_of_tabs, 1) * "\t"

def write_felo_file(filename, parameters, fencers, bouts):
    """Write Felo parameters, fencers, and bouts to a Felo file, which is
    overwritten if already existing.

    Parameters:
    filename -- path to the Felo file to be written.
    parameters -- dictionary containing Felo parameters.
    fencers -- dictionary with all fencers.
    bouts -- list of all bouts.

    Return values: None
    """
    felo_file = codecs.open(filename, "w", "utf-8")
    print>>felo_file, "# Parameter"
    print>>felo_file
    parameterslist = parameters.items()
    # sort case-insensitively
    parameterslist.sort(lambda x,y: cmp(x[0].upper(),y[0].upper()))
    for name, value in parameterslist:
        print>>felo_file, fill_with_tabs(name, 4) + str(value)
    print>>felo_file
    print>>felo_file, 52 * "="
    print>>felo_file, "# Anfangswerte"
    print>>felo_file, "# Namen der Fechter, die versteckt bleiben wollen,"
    print>>felo_file, "# in Klammern"
    print>>felo_file
    fencerslist = fencers.items()
    fencerslist.sort()
    for fencer in [entry[1] for entry in fencerslist]:
        if fencer.hidden:
            name = "(" + fencer.name + ")"
        else:
            name = fencer.name
        print>>felo_file, fill_with_tabs(name, 3) + str(fencer.initial_felo_rating)
    print>>felo_file
    print>>felo_file, 52 * "="
    print>>felo_file, "# Gefechte"
    print>>felo_file
    bouts.sort()
    for i, bout in enumerate(bouts):
        # Separate days for clarity
        if i > 0 and bouts[i-1].daynumber() != bout.daynumber():
            print>>felo_file
        line = fill_with_tabs(fill_with_tabs(bout.date, 2) +
                               "%s -- %s" % (bout.first_fencer, bout.second_fencer), 5) + \
                               "%d:%d" % (bout.points_first, bout.points_second)
        if bout.fenced_to == 0 or (bout.points_first != bout.fenced_to and
                                          bout.points_second != bout.fenced_to):
            line += "/" + str(bout.fenced_to)
        print>>felo_file, line
    felo_file.close()

class Error(Exception):
    """Standard error class.
    """
    def __init__(self, description, filename="", linenumber=0):
        """Class constructor.  Filename and linenumber are only given if it is
        about a parsing error in a Felo file.

        Parameters:
        description -- error message.
        filename -- Felo file name.
        linenumber -- number of the line in the Felo file where the error
           occured.
        """
        if filename:
            supplement = filename
            if linenumber:
                supplement += ", Zeile " + unicode(linenumber)
            description = supplement  + ": " + description
        self.description = description
        Exception.__init__(self, description)

def adopt_preliminary_felo_ratings():
    """Take all preliminary numbers (Felo and fenced points) and write them over
    the "real" numbers.  The preliminary numbers remain untouched and can be
    used for further calculations.

    For optimisation, only fencers in the set
    fencers_with_preliminary_felo_rating, which is a class variable in Fencers,
    are visited.

    No Parameters and return values.
    """
    for fencer in Fencer.fencers_with_preliminary_felo_rating:
        fencer.felo_rating = fencer.felo_rating_preliminary
        fencer.fenced_points = fencer.fenced_points_preliminary
    Fencer.fencers_with_preliminary_felo_rating.clear()

class Fencer(object):
    """Class for fencer data.  Basically, it is a mere container for the
    attributes.
    """
    fencers_with_preliminary_felo_rating = set()
    """Set with all fencers which still have their Felo number in
    felo_rating_preliminary, so that it must be copied to felo_rating is a bout
    day is completely processed."""
    def __init__(self, name, felo_rating, parameters):
        """Class constructor.

        Parameters:
        name -- name of the fencer.
        felo_rating -- initial Felo rating.
        parameters -- dictionary with all Felo parameters.
        """
        self.hidden = name.startswith(u"(")
        if self.hidden:
            self.name = name[1:-1]
        else:
            self.name = name
            self.parameters = parameters
        self.fenced_points = self.fenced_points_preliminary = 0
        self.__k_factor = self.parameters[u"k-Faktor Rest"]
        self.freshman = felo_rating == 0
        if not self.freshman:
            self.felo_rating = self.initial_felo_rating = self.felo_rating_preliminary = felo_rating
        else:
            self.total_weighting = 0.0
            self.total_felo_rating_opponents = 0.0
            self.total_result = 0.0
    def __get_felo_rating_exact(self):
        if not self.freshman:
            return self.__felo_rating
        else:
            # Estimate initial Felo number according to the Austrian Method,
            # see http://www.chess.at/bundesspielleitung/OESB/oesb_tuwo_06.pdf
            # section 5.1 on page 43.
            if self.total_weighting < self.parameters[u"Minimal-Gewichtung Einsteiger"]:
                return 0.0
            A = self.total_result / self.total_weighting
            B = self.total_weighting / (self.total_weighting + 2)
            average_felo_rating_opponents = self.total_felo_rating_opponents / self.total_weighting
            return average_felo_rating_opponents + (A * B * 700)
    def __get_felo_rating(self):
        return int(round(self.felo_rating_exact))
    def __set_felo_rating(self, felo_rating):
        if not self.freshman:
            self.__felo_rating = max(felo_rating, self.parameters[u"Minimum Elo-Zahl"])
            if self.__felo_rating >= self.parameters[u"Elo-Zahl Top-Fechter"]:
                self.__k_factor = self.parameters[u"k-Faktor Top-Fechter"]
    felo_rating_exact = property(__get_felo_rating_exact, __set_felo_rating,
                                 doc="""Felo rating with decimal fraction.""")
    felo_rating = property(__get_felo_rating, __set_felo_rating, doc="""Felo rating, rounded to integer.""")
    def __get_k_factor(self):
        if self.fenced_points < self.parameters[u"Einzeltreffer Einsteiger"]:
            return self.parameters[u"k-Faktor Einsteiger"]
        return self.__k_factor
    k_factor = property(__get_k_factor)
    def __cmp__(self, other):
        """Sort by Felo rating, descending."""
        return -cmp(self.felo_rating_exact, other.felo_rating_exact)

def calculate_felo_ratings(parameters, fencers, bouts, plot=False, estimate_freshmen=False,
                           bootstrapping=False, maxcycles=1000):
    """Calculate the new Felo ratings, taking a whole bunch of bouts into
    account.  If wanted, generate plots with the development of the Felo
    numbers.

    Parameters:
    parameters -- dictionary with all Felo parameters.
    fencers -- dictionary with all fencers.
    bouts -- list of bouts, which is sorted chronologically if necessary.
    plot -- if True, plots as PNG and PDF are generated.  The file name is the
        group name in the Felo parameters.
    bootstrapping -- if True, try to estimate good starting Felo numbers by
        going through the bouts multiple times, using the result numbers as new
        starting numbers, until the numbers have converged.
    maxcycles -- the maximal number of cycles in the bootstrapping process.  If
        it is not enough, an exception is raised.
    estimate_freshmen -- if True, try to calculate estimates for freshmen.

    Return values: A list (not a dictionary!) of all visible fencers, sorted by
    descending Felo number.
    If estimate_fresmen is True, a list with all freshmen.    
    """
    def calculate_felo_ratings_core(parameters, fencers, bouts, plot, bouts_base_filename=None):
        """Calculate the new Felo ratings, taking a whole bunch of bouts into
        account.  If wanted, generate plots with the development of the Felo
        numbers.  Some things that are necessary before and after are not done
        here, because it is only the "core" routine.

        Parameters:
        parameters -- dictionary with all Felo parameters.
        fencers -- dictionary with all fencers.
        bouts -- list of bouts, which is sorted chronologically if necessary.
        plot -- If True, plots as PNG and PDF are generated.  The file name is the
            group name in the Felo parameters.
        bouts_base_filename -- just a copy of the variable of the same name
            from the enclosing scope.  It's the filename before the "." of the
            plot graphics files.

        Return values: None if plot==False.  If plot==True, the accumulated
        xtics are returned.
        """
        if plot:
            data_file = open(bouts_base_filename + ".dat", "w")
            # xtics holds the Gnuplot command for the x axis labels (i.e. the dates).
            xtics = ""
            last_xtics_daynumber = 0
        for i, bout in enumerate(bouts):
            set_preliminary_felo_ratings(fencers, bout, parameters)
            if i == len(bouts) - 1 or bout.date != bouts[i+1].date:
                # Not one *day* is over but one set of bouts which took place with
                # unknown order.
                adopt_preliminary_felo_ratings()
            current_bout_daynumber = bout.daynumber()
            year, month, day, _, _, _, _, _, _ = time.localtime()
            current_daynumber = julian_date(year, month, day)
            if plot and (i == len(bouts) - 1 or bouts[i+1].daynumber() != current_bout_daynumber) and \
                    bout.date[:10] >= parameters[u"Plot Mindestdatum"] and current_daynumber - current_bout_daynumber <= parameters[u"Plot maximale Tage"]:
                # Okay, we must generate new data points because one day is over.
                # BTW, the stange thing with "1500" is a cheap way to exclude too
                # old bouts from the plot.  FixMe: It should be removed, because
                # bouts without date can be used for bootstrapping only anyway.
                data_file.write(str(current_bout_daynumber))
                if current_bout_daynumber - last_xtics_daynumber >= parameters[u"Plot-Tics Mindestabstand"]:
                    # Generate tic marks not too densely; labels must be at
                    # least the the minimal tic distance apart.
                    last_xtics_daynumber = current_bout_daynumber
                    xtics += "'%d.%d.%d' %d," % (bout.day, bout.month, bout.year, current_bout_daynumber)
                for fencer in visible_fencers:
                    data_file.write("\t" + str(fencer.felo_rating_exact))
                data_file.write(os.linesep)
        if plot:
            data_file.close()
            return xtics

    visible_fencers = [fencer for fencer in fencers.values() if not fencer.hidden and not fencer.freshman]
    for index, fencer in enumerate(visible_fencers):
        # Store the column index of the data file in the fencer object.  Needed
        # by Gnuplot.
        fencer.columnindex = index + 2
    bouts_base_filename = parameters[u"Gruppenname"].lower()
    bouts.sort()
    if bootstrapping:
        for i in range(maxcycles):
            for fencer in fencers.values():
                fencer.old_felo_rating = fencer.felo_rating_exact
            calculate_felo_ratings_core(parameters, fencers, bouts, plot=False)
            for fencer in fencers.values():
                if abs(fencer.old_felo_rating - fencer.felo_rating_exact) > 0.001:
                    break
            else:
                break
        if i == maxcycles - 1:
            raise Error("Das Bootstrapping ist nicht konvergiert.")
    xtics = calculate_felo_ratings_core(parameters, fencers, bouts, plot, bouts_base_filename)
    visible_fencers.sort()    # Descending by Felo rating
    if plot:
        # Call Gnuplot, convert, and ps2pdf to generate the PNG and PDF plots.
        # Note: We don't generate HTML tables here.  These must be provided
        # separately.
        gnuplot_script = "set term postscript color; set output '" + bouts_base_filename + ".ps';"
        gnuplot_script += "set key outside; set xtics rotate; set grid xtics;"
        gnuplot_script += "set xtics nomirror (%s);" % xtics[:-1]
        gnuplot_script += "plot "
        for i, fencer in enumerate(visible_fencers):
            gnuplot_script += "'%s.dat' using 1:%d with lines lw 5 title '%s'" % \
                (bouts_base_filename, fencer.columnindex, fencer.name)
            if i < len(visible_fencers) - 1:
                gnuplot_script += ", "
        gnuplot = Popen(["gnuplot", "-"], stdin=PIPE, stdout=PIPE, stderr=PIPE)
        gnuplot.communicate(gnuplot_script)
        call(["convert", bouts_base_filename+".ps", "-rotate", "90",
              parameters[u"Ausgabeverzeichnis"] + "/" + bouts_base_filename+".png"])
        call(["ps2pdf", bouts_base_filename+".ps",
              parameters[u"Ausgabeverzeichnis"] + "/" + bouts_base_filename+".pdf"])

    if estimate_freshmen:
        return [fencer for fencer in fencers.values() if fencer.freshman]
    return visible_fencers

def expectation_value(first_fencer, second_fencer):
    """Returns the expected winning value of the first given fencer in a bout
    with the second.  The winning value is actually the fraction of won single
    points.  I.e., an expectation value of 0.7 means that the first fencer will
    make 70% of the points.

    Parameters:
    first_fencer -- first fencer, for whom the expectation value is to be
        calculated.
    second_fencer -- second fencer, opponent in the bout.

    Return value:
    Expected winning value, with 0 <= value <= 1.
    """
    return 1 / (1 + 10**((second_fencer.felo_rating_exact - first_fencer.felo_rating_exact)/400.0))

def prognosticate_bout(first_fencer, second_fencer, fenced_to):
    """Estimates the most probable result of a bout.

    Parameters:
    first_fencer -- first fencer, for whom the winning chance is to be
        calculated.
    second_fencer -- second fencer, opponent in the bout.
    fenced_to -- number of winning points in the bout.  Must be 5, 10, or 15.

    Return values:
    Points of the first fencer, points of the second fencer, and the winning
    probability of the first fencer in percent.
    """
    expectation_first = expectation_value(first_fencer, second_fencer)
    if expectation_first > 0.5:
        points_first = fenced_to
        points_second = int(round(fenced_to * (1/expectation_first - 1)))
    else:
        points_first = int(round(fenced_to / (1/expectation_first - 1)))
        points_second = fenced_to
    for line in file(datapath+"/auf%d.dat" % fenced_to):
        if line[0] != "#":
            result_first, winning_chance_first, _ = line.split()
            result_first, winning_chance_first = float(result_first), float(winning_chance_first)
            if abs(expectation_first - result_first) < 0.0051:
                break
    if points_first == points_second:
        if winning_chance_first > 0.5:
            points_second -= 1
        else:
            points_first -= 1
    return points_first, points_second, int(round(winning_chance_first * 100))

if __name__ == '__main__':
    """If called as a program, it interprets the command line parameters and
    calculates the resulting Felo rankings for each given Felo file.  It prints
    the result lists on the screen or writes them to a file.  It's a quick and
    simple way to calculate numbers, and it may be enough for many purposes.
    """
    import sys, optparse, shutil
    option_parser = optparse.OptionParser()
    option_parser.add_option("-p", "--plots", action="store_true", dest="plots",
                             help=u"Erzeuge Plots der Felo-Zahlen", default=False)
    option_parser.add_option("-b", "--bootstrap", action="store_true", dest="bootstrap",
                             help=u"Versuche, gute Start-Felo-Zahlen fuer alle zu berechnen", default=False)
    option_parser.add_option("--max-cycles", type="int",
                             dest="max_cycles", help=u"Maximale Iterationsschritte beim "
                             "Bootstrapping.  Default: 1000",
                             default=1000, metavar="NUMMER")
    option_parser.add_option("--estimate-freshmen", action="store_true", dest="estimate_freshmen",
                             help=u"Versuche, Neueinsteiger zu bewerten", default=False)
    option_parser.add_option("--write-back", action="store_true", dest="write_back",
                             help=u"Schreibe die neuen Startzahlen zurueck in die Felo-Datei",
                             default=False)
    option_parser.add_option("-o", "--output", type="string",
                             dest="output_file", help=u"Name der Ausgabedatei.  "
                             "Default: Ausgabe auf dem Bildschirm (stdout)",
                             default=None, metavar="DATEINAME")
    options, felo_filenames = option_parser.parse_args()

    try:
        if options.estimate_freshmen and options.bootstrap:
            raise Error("Man kann nicht gleichzeitig bootstrappen und Neueinsteiger bewerten.")
        if options.output_file:
            output_file = codecs.open(options.output_file, "w")
        else:
            output_file = sys.stdout
        for i, felo_filename in enumerate(felo_filenames):
            parameters, given_parameters, fencers, bouts = parse_felo_file(felo_filename)
            resultslist = calculate_felo_ratings(parameters, fencers, bouts, options.plots,
                                                 options.estimate_freshmen,
                                                 options.bootstrap, options.max_cycles)
            if (options.estimate_freshmen or options.bootstrap) and options.write_back:
                for fencer in fencers.values():
                    if options.bootstrap or fencer.freshman:
                        fencer.initial_felo_rating = fencer.felo_rating
                filename_backup = os.path.splitext(felo_filename)[0] + ".bak"
                if os.path.isfile(filename_backup):
                    raise Error(u"Bitte erst die Sicherungskopie (Endung .bak) löschen.")
                shutil.copyfile(felo_filename, filename_backup)
                for parameter in parameters.keys():
                    if parameter not in given_parameters:
                        del parameters[parameter]
                write_felo_file(felo_filename, parameters, fencers, bouts)
            if len(felo_filenames) > 1:
                if i >= 1: print>>output_file
                print>>output_file, parameters["Gruppenname"] + ":"
            for fencer in resultslist:
                print>>output_file, "    " + fencer.name + (19-len(fencer.name))*" " + "\t" + \
                    unicode(fencer.felo_rating)
    except Error, e:
        print>>sys.stderr, "felo_rating:", e.description.encode("utf-8")
        

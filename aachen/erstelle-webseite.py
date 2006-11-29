#!/usr/bin/env python
# -*- coding: utf-8 -*-

__version__ = "$Revision:  $"
# $Source:  $

import codecs, os
from subprocess import call
import shutil, time
import sys
sys.path.append("../src")
from felo_rating import parse_felo_file, calculate_felo_ratings, write_felo_file

os.chdir("../aachen")

def datei_zeitstempel(pfade):
    timestamp = 0
    for pfad in pfade:
        timestamp = max(timestamp, os.stat(pfad).st_mtime)
    return time.strftime(u"%d.&nbsp;%B&nbsp;%Y", time.localtime(timestamp))

def convert_date(date):
    return time.strftime(u"%d.&nbsp;%B&nbsp;%Y", time.strptime(date, "%Y/%m/%d"))

mache_plots = True
ausgabedatei = codecs.open("/home/bronger/aktuell/fechten/Intern/felo-zahlen.html",
                           "w", "iso-8859-1")
foil_parameters, foil_fencers, foil_bouts = parse_felo_file("florett.felo")
epee_parameters, epee_fencers, epee_bouts = parse_felo_file("degen.felo")
foil_bouts.sort()
epee_bouts.sort()

print>>ausgabedatei, u"""<html>
<head>
<title>Felo-Zahlen</title>
<meta name="author" content="Torsten">
<meta name="generator" content="Torstens Fechter-Zahl-Generator">
<link rel=stylesheet type="text/css" href="../Style.css">
</head>
<body>
<div align="center">
<h1>Felo-Zahlen</h1>

<p style="font-size: large">Die <a href="felo-faq.html">Felo-FAQ</a> &ndash;
                            Fragen und Antworten</p>

<table cellspacing="50px" style="background-color: #00a0FF">
<tbody>
<tr style="vertical-align:top">
<td style="text-align:center">
<h2 id="florett">Florett</h2>
<p style="font-size: medium;margin-top:-1ex">vom %s</p>
<p style="font-size:large"><a href="felo-plots.html">Zur Grafik &rarr;</a></p>
<p><table cellspacing="10" style="font-size: large; width:100%%">
<tbody>""" % convert_date(foil_bouts[-1].date[:10])
# write_felo_file("florett_.felo", foil_parameters, foil_fencers, foil_bouts)
for fechter in calculate_felo_ratings(foil_parameters, foil_fencers, foil_bouts, plot=mache_plots):
    felo_zahl = str(fechter.felo_rating)
    if fechter.fenced_points < 50:
        felo_zahl = "&asymp;&nbsp;" + felo_zahl
    print>>ausgabedatei, u"<tr><td>%s</td><td style='text-align:right'>%s</td></tr>" % (fechter.name, felo_zahl)
shutil.copy2("florett.png", "/home/bronger/aktuell/fechten/Intern/")
shutil.copy2("florett.pdf", "/home/bronger/aktuell/fechten/Intern/")
print>>ausgabedatei, u"""</tbody>
</table></p>
</td><!--td style="text-align:center">
<h2 id="degen">Degen</h2>
<p style="font-size: medium;margin-top:-1ex">vom %s</p>
<p style="font-size:large"><a href="felo-plots.html#degen">Zur Grafik &rarr;</a></p>
<table cellspacing="10" style="font-size: large; width:100%%">
<tbody>""" % convert_date(epee_bouts[-1].date[:10])
for fechter in calculate_felo_ratings(epee_parameters, epee_fencers, epee_bouts, plot=mache_plots):
    felo_zahl = str(fechter.felo_rating)
    if fechter.fenced_points < 50:
        felo_zahl = "&asymp;&nbsp;" + felo_zahl
    print>>ausgabedatei, u"<tr><td>%s</td><td style='text-align:right'>%s</td></tr>" % (fechter.name, felo_zahl)
shutil.copy2("degen.png", "/home/bronger/aktuell/fechten/Intern/")
shutil.copy2("degen.pdf", "/home/bronger/aktuell/fechten/Intern/")
print>>ausgabedatei, u"""</tbody>
</table>
</td-->
</tr>
</tbody>
</table>
</div>
<p id="referenztabelle" style="max-width:30%">Als Orientierung:<!-- (Aber bitte nicht zu ernst nehmen, weil sich das
auf internationale Wettkämpfe bezieht.)--></p>
<table cellspacing="5"><tbody>
<tr><td>ab</td></tr>
<tr><td>2500</td><td>Fechten wie ein junger Gott</td></tr>
<tr><td>2400</td><td>Internationale Meister</td></tr>
<tr><td>2200</td><td>Nationale Meister</td></tr>
<tr><td>1800</td><td>sehr gute Vereinsspieler</td></tr>
<tr><td>1600</td><td>starke Freizeitspieler</td></tr>
<tr><td>1400</td><td>Einsteiger</td></tr>
<tr><td>1200</td><td>untere rechnerische Grenze</td></tr>
</tbody></table>
</body>
</html>
"""

shutil.copy2("felo-plots.html", "/home/bronger/aktuell/fechten/Intern/")
shutil.copy2("felo-faq.html", "/home/bronger/aktuell/fechten/Intern/")
call(["sitecopy", "-u", "fechten"])

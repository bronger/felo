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
import locale
locale.setlocale(locale.LC_ALL, '')

def datei_zeitstempel(pfade):
    timestamp = 0
    for pfad in pfade:
        timestamp = max(timestamp, os.stat(pfad).st_mtime)
    return time.strftime(u"%d.&nbsp;%B&nbsp;%Y", time.localtime(timestamp))

def convert_date(date):
    return time.strftime(u"%d.&nbsp;%B&nbsp;%Y", time.strptime(date, "%Y-%m-%d"))

mache_plots = True
ausgabedatei = codecs.open("/home/bronger/aktuell/fechten/Statistics/felo-zahlen.html",
                           "w", "iso-8859-1")
foil_parameters, __, foil_fencers, foil_bouts = parse_felo_file(codecs.open("florett.felo", encoding="utf-8"))
epee_parameters, __, epee_fencers, epee_bouts = parse_felo_file(codecs.open("degen.felo", encoding="utf-8"))
foil_bouts.sort()
epee_bouts.sort()

print>>ausgabedatei, u"""<?xml version="1.0" encoding="iso-8859-1"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<title>Felo-Zahlen</title>
<meta name="author" content="Torsten" />
<meta name="generator" content="Torstens Felo-Zahl-Generator" />
<link rel="stylesheet" type="text/css" href="../Style.css" />
</head>
<body>
<div style="text-align:center">
<h1>Felo-Zahlen</h1>

<p style="font-size: large">Die <a href="felo-faq.html">Felo-FAQ</a> &ndash;
                            Fragen und Antworten</p>

<table cellspacing="50px" style="background-color: #00a0FF" width="100%%">
<tbody>
<tr style="vertical-align:top">
<td>&nbsp;</td>
<td style="text-align:center;width:19em">
<h2 id="florett">Florett</h2>
<p style="font-size: medium;margin-top:-1ex">vom %s</p>
<p style="font-size:large"><a href="felo-plots.html">Zur Grafik &rarr;</a></p>
<table cellspacing="10" style="font-size: large; width:100%%">
<tbody>""" % convert_date(foil_bouts[-1].date_string[:10])
# write_felo_file("florett_.felo", foil_parameters, foil_fencers, foil_bouts)
for fechter in calculate_felo_ratings(foil_parameters, foil_fencers, foil_bouts, plot=mache_plots):
    felo_zahl = str(fechter.felo_rating)
    if fechter.total_weighting < 7:
        felo_zahl = "&asymp;&nbsp;" + felo_zahl
    print>>ausgabedatei, u"<tr><td style='text-align:left'>%s</td><td style='text-align:right'>%s</td></tr>" % (fechter.name, felo_zahl)
shutil.copy2("florett.png", "/home/bronger/aktuell/fechten/Statistics/")
shutil.copy2("florett.pdf", "/home/bronger/aktuell/fechten/Statistics/")
print>>ausgabedatei, u"""</tbody>
</table>
</td><td style="text-align:center;width:19em">
<h2 id="degen">Degen</h2>
<p style="font-size: medium;margin-top:-1ex">vom %s</p>
<p style="font-size:large"><a href="felo-plots.html#degen">Zur Grafik &rarr;</a></p>
<table cellspacing="10" style="font-size: large; width:100%%">
<tbody>""" % convert_date(epee_bouts[-1].date_string[:10])
for fechter in calculate_felo_ratings(epee_parameters, epee_fencers, epee_bouts, plot=mache_plots):
    felo_zahl = str(fechter.felo_rating)
    if fechter.total_weighting < 7:
        felo_zahl = "&asymp;&nbsp;" + felo_zahl
    print>>ausgabedatei, u"<tr><td style='text-align:left'>%s</td><td style='text-align:right'>%s</td></tr>" % (fechter.name, felo_zahl)
shutil.copy2("degen.png", "/home/bronger/aktuell/fechten/Statistics/")
shutil.copy2("degen.pdf", "/home/bronger/aktuell/fechten/Statistics/")
print>>ausgabedatei, u"""</tbody>
</table>
</td>
<td>&nbsp;</td>
</tr>
</tbody>
</table>
</div>
<p id="referenztabelle" style="max-width:30%">Als Orientierung:<!-- (Aber bitte nicht zu ernst nehmen, weil sich das
auf internationale Wettkämpfe bezieht.) --></p>
<table cellspacing="5"><tbody>
<tr><td>ab</td></tr>
<tr><td>2500</td><td>Fechten wie ein junger Gott</td></tr>
<tr><td>2400</td><td>Internationale Meister</td></tr>
<tr><td>2200</td><td>Nationale Meister</td></tr>
<tr><td>1800</td><td>sehr gute Vereinsfechter</td></tr>
<tr><td>1600</td><td>starke Freizeitfechter</td></tr>
<tr><td>1400</td><td>Einsteiger</td></tr>
<tr><td>1200</td><td>untere rechnerische Grenze</td></tr>
</tbody></table>
</body>
</html>
"""

shutil.copy2("felo-plots.html", "/home/bronger/aktuell/fechten/Statistics/")
shutil.copy2("felo-faq.html", "/home/bronger/aktuell/fechten/Statistics/")
call(["sitecopy", "-u", "fechten"])

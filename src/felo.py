#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#    felo.py - Main GUI part of the Felo program
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

import re, os, codecs, sys, time, StringIO, textwrap, platform
import gettext, locale
locale.setlocale(locale.LC_ALL, '')
gettext.install('felo', '.', unicode=True)
import felo_rating
import wx, wx.grid, wx.py.editor, wx.py.editwindow, wx.html

datapath = os.path.abspath(os.path.dirname(__file__))

class HtmlFrame(wx.Frame):
    def __init__(self, parent, file):
        wx.Frame.__init__(self, parent, wx.ID_ANY, _(u"Preview HTML"), size=(400, 600))
        html = wx.html.HtmlWindow(self)
        if "gtk2" in wx.PlatformInfo:
            html.SetStandardFonts()
        html.LoadPage(file)

class Editor(wx.py.editor.EditWindow):
    def __init__(self, parent):
        wx.stc.StyledTextCtrl.__init__(self, parent, wx.ID_ANY)
        self.SetTabWidth(8)
        self.setStyles(wx.py.editwindow.FACES)
        self.SetMarginWidth(0, self.TextWidth(wx.stc.STC_STYLE_LINENUMBER, "00000"))
        self.SetMarginWidth(1, 10)
        self.Bind(wx.stc.EVT_STC_STYLENEEDED, self.OnStyling)
        self.bout_line_pattern = re.compile("\\s*(?P<date>\\d{4}-\\d{1,2}-\\d{1,2}(?:\\.\\d+)?)"
                                            "\\s*\t+\\s*"
                                            "(?P<first>.+?)\\s*--\\s*(?P<second>.+?)\\s*\t+\\s*"
                                            "(?P<score>\\d+:\\d+(?P<fenced_to>/\\d+)?)\\s*\\Z")
        self.item_line_pattern = re.compile("\s*(?P<name>[^\t]+?)\\s*\t+\\s*(?P<value>.+?)\s*\\Z")
    def OnStyling(self, event):
        def apply_style(span, style):
            start, end = span
            self.StartStyling(position+start, 0xff)
            self.SetStyling(end-start, style)
        start, end = self.PositionFromLine(self.LineFromPosition(self.GetEndStyled())), event.GetPosition()
        text = self.GetTextRange(start, end)
        position = start
        lines = text.splitlines(True)
        for line in lines:
            if line.lstrip().startswith("#"):
                apply_style((0, len(line)), 6)
            else:
                match = self.bout_line_pattern.match(line)
                if match:
                    apply_style(match.span(1), 3)
                    apply_style(match.span(2), 5)
                    apply_style(match.span(3), 5)
                    apply_style(match.span(5), 1)
                else:
                    match = self.item_line_pattern.match(line)
                    if match:
                        apply_style(match.span(1), 5)
            position += len(line)

class ResultFrame(wx.Frame):
    def __init__(self, results, *args, **keyw):
        wx.Frame.__init__(self, None, wx.ID_ANY, size=(300, 500), title=_(u"Felo ratings"), *args, **keyw)
        result_box = wx.TextCtrl(self, wx.ID_ANY, results, style=wx.TE_MULTILINE)
        result_box.SetEditable(False)
        
class HTMLDialog(wx.Dialog):
    def __init__(self, directory, *args, **keyw):
        wx.Dialog.__init__(self, None, wx.ID_ANY, size=(300, 180), title=_(u"HTML export"), *args, **keyw)
        wx.StaticText(self, wx.ID_ANY,
                      textwrap.fill(_(u"The web files will be written to the folder %s.") % directory, 41),
                      (20, 20))
        self.plot_switch = wx.CheckBox(self, wx.ID_ANY, _(u"with plot"), (35, 100), (150, 20))
        ok_button = wx.Button(self, wx.ID_OK, _("Okay"), pos=(50, 140))
        ok_button.SetDefault()
        cancel_button = wx.Button(self, wx.ID_CANCEL, _("Cancel"), pos=(150, 140))

class Frame(wx.Frame):
    def __init__(self, *args, **keyw):
        wx.Frame.__init__(self, None, wx.ID_ANY, size=(700, 700), title="Felo", *args, **keyw)
        menu_bar = wx.MenuBar()

        menu_file = wx.Menu()
        open = menu_file.Append(wx.ID_ANY, _(u"&Open"))
        self.Bind(wx.EVT_MENU, self.OnOpen, open)
        save = menu_file.Append(wx.ID_ANY, _(u"&Save"))
        self.Bind(wx.EVT_MENU, self.OnSave, save)
        save_as = menu_file.Append(wx.ID_ANY, _(u"Save &as"))
        self.Bind(wx.EVT_MENU, self.OnSaveAs, save_as)
        menu_file.AppendSeparator()
        exit = menu_file.Append(wx.ID_ANY, _(u"&Quit"))
        self.Bind(wx.EVT_MENU, self.OnExit, exit)
        menu_bar.Append(menu_file, _(u"&File"))

        menu_calculate = wx.Menu()
        calculate_felo_numbers = menu_calculate.Append(wx.ID_ANY, _(u"Calculdate &Felo ratings"))
        self.Bind(wx.EVT_MENU, self.OnCalculateFeloRatings, calculate_felo_numbers)
        generate_html = menu_calculate.Append(wx.ID_ANY, _(u"Generate &HTML"))
        self.Bind(wx.EVT_MENU, self.OnGenerateHTML, generate_html)
        bootstrapping = menu_calculate.Append(wx.ID_ANY, _(u"&Bootstrapping"))
        self.Bind(wx.EVT_MENU, self.OnBootstrapping, bootstrapping)
        estimate_freshmen = menu_calculate.Append(wx.ID_ANY, _(u"&Estimate freshmen"))
        self.Bind(wx.EVT_MENU, self.OnEstimateFreshmen, estimate_freshmen)
        menu_bar.Append(menu_calculate, _(u"&Calculate"))

        menu_help = wx.Menu()
        about = menu_help.Append(wx.ID_ANY, _(u"&About"))
        self.Bind(wx.EVT_MENU, self.OnAbout, about)
        menu_bar.Append(menu_help, _(u"&Help"))

        self.SetMenuBar(menu_bar)

        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)
        self.felo_filename = self.editor = None
        if len(sys.argv) > 1:
            self.open_felo_file(sys.argv[1])
    def OnChange(self, event):
        self.felo_file_changed = True
    def AssureSave(self):
        if self.editor and self.felo_file_changed:
            answer = wx.MessageBox(_(u"The file \"%s\" has changed.  Save it?") % self.felo_filename,
                                   _(u"File changed"), wx.YES_NO | wx.CANCEL | wx.YES_DEFAULT |
                                   wx.ICON_QUESTION, self)
            if answer == wx.YES:
                self.editor.SaveFile(self.felo_filename)
                self.felo_file_changed = False
            elif answer == wx.CANCEL:
                return wx.CANCEL
    def open_felo_file(self, felo_filename):
        self.felo_filename = os.path.abspath(felo_filename)
        if not self.editor:
            self.editor = Editor(self)
            self.editor.SetScrollWidth(self.editor.TextWidth(wx.stc.STC_STYLE_DEFAULT, 68*"0"))
            self.editor.SetLexer(wx.stc.STC_LEX_CONTAINER)
            self.editor.Bind(wx.stc.EVT_STC_CHANGE, self.OnChange)
            self.SendSizeEvent()
        self.editor.LoadFile(self.felo_filename)
        self.felo_file_changed = False
        self.SetTitle(u"Felo – "+os.path.split(self.felo_filename)[1])
        os.chdir(os.path.dirname(self.felo_filename))
    def OnOpen(self, event):
        if self.AssureSave == wx.CANCEL:
            return
        wildcard = _(u"Felo file (*.felo)|*.felo|"
                     "All files (*.*)|*.*")
        dialog = wx.FileDialog(None, _(u"Select Felo file"), os.getcwd(),
                               "", wildcard, wx.OPEN | wx.FILE_MUST_EXIST)
        if dialog.ShowModal() == wx.ID_OK:
            self.open_felo_file(dialog.GetPath())
            dialog.Destroy()
    def OnExit(self, event):
        self.Close()
    def OnCloseWindow(self, event):
        if self.AssureSave() == wx.CANCEL:
            return
        self.Destroy()
    def save_felo_file(self):
        if self.felo_filename:
            self.editor.SaveFile(self.felo_filename)
            self.felo_file_changed = False
            return True
        return False
    def OnSave(self, event):
        self.save_felo_file()
    def OnSaveAs(self, event):
        if self.editor:
            wildcard = _(u"Felo file (*.felo)|*.felo|"
                         "All files (*.*)|*.*")
            dialog = wx.FileDialog(None, _(u"Select Felo file"), os.getcwd(),
                                   "", wildcard, wx.SAVE | wx.OVERWRITE_PROMPT)
            if dialog.ShowModal() == wx.ID_OK:
                self.felo_filename = dialog.GetPath()
                dialog.Destroy()
                self.save_felo_file()
    
    def assure_open_felo_file(self):
        if not self.editor:
            wx.MessageBox(_(u"Please first open a Felo file.") ,
                          _(u"Notification"), wx.OK | wx.ICON_INFORMATION, self)
            return False
        return True
    def parse_editor_contents(self):
        if not self.assure_open_felo_file():
            return {}, {}, []
        felo_file_contents = StringIO.StringIO(self.editor.GetText())
        felo_file_contents.name = self.felo_filename
        try:
            parameters, __, fencers, bouts = felo_rating.parse_felo_file(felo_file_contents)
        except felo_rating.LineError, e:
            self.editor.GotoLine(e.linenumber - 1)
            wx.MessageBox(_(u"Error in line %d: %s") % (e.linenumber, e.naked_description),
                          _(u"Parsing error"), wx.OK | wx.ICON_ERROR, self)
        except felo_rating.FeloFormatError, e:
            wx.MessageBox(e.description, _(u"Parsing error"), wx.OK | wx.ICON_ERROR, self)
        else:
            return parameters, fencers, bouts
        return {}, {}, []
    def OnCalculateFeloRatings(self, event):
        parameters, fencers, bouts = self.parse_editor_contents()
        if not parameters:
            return
        fencerlist = felo_rating.calculate_felo_ratings(parameters, fencers, bouts)
        results = u""
        for fencer in fencerlist:
            results += fencer.name + u"\t\t" + unicode(fencer.felo_rating) + u"\n"
        result_frame = ResultFrame(results)
        result_frame.Show()
    def OnGenerateHTML(self, event):
        if not self.assure_open_felo_file():
            return
        felo_file_contents = StringIO.StringIO(self.editor.GetText())
        felo_file_contents.name = self.felo_filename
        parameters, fencers, bouts = self.parse_editor_contents()
        if not parameters:
            return
        bouts.sort()
        last_date = time.strftime(_(u"%x"), time.strptime(bouts[-1].date_string[:10], "%Y-%m-%d"))
        base_filename = parameters["groupname"].lower()
        html_dialog = HTMLDialog(parameters["output folder"])
        result = html_dialog.ShowModal()
        make_plot = html_dialog.plot_switch.GetValue()
        html_dialog.Destroy()
        if result != wx.ID_OK:
            return
        file_list = u""
        html_filename = os.path.join(parameters["output folder"], base_filename+".html")
        html_file = codecs.open(html_filename, "w", "utf-8")
        file_list += base_filename+".html\n"
        print>>html_file, u"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head><title>%(title)s</title><meta http-equiv="Content-Style-Type" content="text/css" /><style type="text/css">
/*<![CDATA[*/
@import "felo.css";
/*]]>*/
</style></head><body>\n\n<h1>%(title)s</h1>\n<h2>%(date)s</h2>\n\n<table><tbody>""" % \
            {"title": _(u"Felo ratings ")+parameters["groupname"], "date": _(u"as of ")+last_date}
        try:
            fencerlist = felo_rating.calculate_felo_ratings(parameters, fencers, bouts, plot=make_plot)
        except felo_rating.ExternalProgramError, e:
            wx.MessageBox(e.description, _(u"External program not found"), wx.OK | wx.ICON_ERROR, self)
            return
        for fencer in fencerlist:
            print>>html_file, u"<tr><td class='name'>%s</td><td class='felo-rating'>%d</td></tr>" % \
                (fencer.name, fencer.felo_rating)
        print>>html_file, u"</tbody></table>"
        if make_plot:
            print>>html_file, u"<p class='felo-plot'><img class='felo-plot' src='%s.png' alt='%s' /></p>" % \
                (base_filename, _(u"Felo ratings plot for ")+parameters["groupname"])
            print>>html_file, _(u"<p class='printable-notice'>Also in a <a href='%s.pdf'>" \
                "printable version</a>.</p>") % base_filename
            file_list += base_filename+".png\n"
            file_list += base_filename+".pdf\n"
        print>>html_file, u"</body></html>"
        html_file.close()
        html_window = HtmlFrame(self, html_filename)
        html_window.Show()
        wx.MessageBox(_(u"The following files must be uploaded to the web server:\n\n")+file_list,
                      _(u"Upload file list"), wx.OK | wx.ICON_INFORMATION, self)
    def OnBootstrapping(self, event):
        if not self.assure_open_felo_file():
            return
        answer = wx.MessageBox(_(u"The bootstrapping will change the fencer data.  "
                               "Are you sure that you wish to continue?"),
                               u"Bootstrapping", wx.YES_NO | wx.NO_DEFAULT |
                               wx.ICON_QUESTION, self)
        if answer != wx.YES:
            return
        felo_file_contents = StringIO.StringIO(self.editor.GetText())
        felo_file_contents.name = self.felo_filename
        parameters, __, fencers, bouts = felo_rating.parse_felo_file(felo_file_contents)
        felo_rating.calculate_felo_ratings(parameters, fencers, bouts, bootstrapping=True)
        for fencer in fencers.values():
            if not fencer.freshman:
                fencer.initial_felo_rating = fencer.felo_rating
        self.editor.SetText(felo_rating.write_back_fencers(self.editor.GetText(), fencers))
        self.felo_file_changed = True
    def OnEstimateFreshmen(self, event):
        if not self.assure_open_felo_file():
            return
        answer = wx.MessageBox(_(u"Estimating the freshmen will change their initial Felo numbers.  "
                                 u"Are you sure that you wish to continue?"),
                               _(u"Estimating freshmen"), wx.YES_NO | wx.NO_DEFAULT |
                               wx.ICON_QUESTION, self)
        if answer != wx.YES:
            return
        felo_file_contents = StringIO.StringIO(self.editor.GetText())
        felo_file_contents.name = self.felo_filename
        parameters, __, fencers, bouts = felo_rating.parse_felo_file(felo_file_contents)
        felo_rating.calculate_felo_ratings(parameters, fencers, bouts, estimate_freshmen=True)
        for fencer in fencers.values():
            if fencer.freshman:
                fencer.initial_felo_rating = fencer.felo_rating
        self.editor.SetText(felo_rating.write_back_fencers(self.editor.GetText(), fencers))
        self.felo_file_changed = True
    def OnAbout(self, event):
        image = wx.Image(datapath+"/felo-logo.png", wx.BITMAP_TYPE_PNG)
        bitmap = image.ConvertToBitmap()
        wx.SplashScreen(bitmap, wx.SPLASH_CENTRE_ON_PARENT | wx.SPLASH_NO_TIMEOUT, 0, self, wx.ID_ANY)

class App(wx.App):
    def OnInit(self):
        self.frame = Frame()
        self.frame.Show()
        self.SetTopWindow(self.frame)
        return True

app = App()
app.MainLoop()

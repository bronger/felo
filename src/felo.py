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

__version__ = "$Revision$"
# $HeadURL$

import re, os, codecs, sys, time, StringIO, textwrap, platform
import gettext, locale
locale.setlocale(locale.LC_ALL, '')
gettext.install('felo', '.', unicode=True)
import felo_rating
import wx, wx.grid, wx.py.editor, wx.py.editwindow, wx.html, wx.lib.hyperlink

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
        self.SetScrollWidth(self.TextWidth(wx.stc.STC_STYLE_DEFAULT, 68*"0"))
        self.SetLexer(wx.stc.STC_LEX_CONTAINER)
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
        wx.Dialog.__init__(self, None, wx.ID_ANY, title=_(u"HTML export"), *args, **keyw)
        vbox_main = wx.BoxSizer(wx.VERTICAL)
        text = wx.StaticText(self, wx.ID_ANY,
                             textwrap.fill(_(u"The web files will be written to the folder \"%s\".")
                                           % directory, 41))
        vbox_main.Add(text, flag=wx.LEFT | wx.RIGHT | wx.TOP, border=10)
        vbox_checkboxes = wx.BoxSizer(wx.VERTICAL)
        self.plot_switch = wx.CheckBox(self, wx.ID_ANY, _(u"with plot"))
        vbox_checkboxes.Add(self.plot_switch, flag=wx.BOTTOM, border=10)
        self.HTML_preview = wx.CheckBox(self, wx.ID_ANY, _(u"preview the HTML"))
        self.HTML_preview.SetValue(True)
        vbox_checkboxes.Add(self.HTML_preview)
        vbox_main.Add(vbox_checkboxes, flag=wx.ALL, border=20)
        hbox_buttons = wx.BoxSizer(wx.HORIZONTAL)
        ok_button = wx.Button(self, wx.ID_OK, _("Okay"))
        ok_button.SetDefault()
        hbox_buttons.Add(ok_button)
        cancel_button = wx.Button(self, wx.ID_CANCEL, _("Cancel"))
        hbox_buttons.Add(cancel_button, flag=wx.LEFT, border=10)
        vbox_main.Add(hbox_buttons, flag=wx.ALIGN_CENTER)
        hbox_top = wx.BoxSizer(wx.HORIZONTAL)
        hbox_top.Add(vbox_main, flag=wx.ALL | wx.ALIGN_CENTER, border=5)
        self.SetSizer(hbox_top)
        self.Fit()

class AboutWindow(wx.Dialog):
    def __init__(self, *args, **keyw):
        wx.Dialog.__init__(self, None, wx.ID_ANY, title=_(u"About Felo"), *args, **keyw)
        vbox_main = wx.BoxSizer(wx.VERTICAL)
        text1 = wx.StaticText(self, wx.ID_ANY, _(u"version ")+"1.0"+_(u", revision ")+__version__[11:-2])
        vbox_main.Add(text1, flag=wx.ALIGN_CENTER)
        logo = wx.StaticBitmap(self, wx.ID_ANY,
                               wx.BitmapFromImage(wx.Image(datapath+"/felo-logo-small.png", wx.BITMAP_TYPE_PNG)))
        vbox_main.Add(logo, flag=wx.ALIGN_CENTER)
        text2 = wx.StaticText(self, wx.ID_ANY, u"— "+_(u"Estimate fencing strengths of sport fencers")+u" —")
        vbox_main.Add(text2, flag=wx.ALIGN_CENTER | wx.LEFT | wx.RIGHT | wx.TOP, border=10)
        text3 = wx.StaticText(self, wx.ID_ANY, _(u"Brought to you by the sport fencing group at the\n"
                                                 u"University of Technology Aachen (RWTH), Germany."),
                              style=wx.ALIGN_CENTER)
        vbox_main.Add(text3, flag=wx.ALIGN_CENTER | wx.LEFT | wx.RIGHT | wx.TOP, border=10)
        text4 = wx.StaticText(self, wx.ID_ANY, _(u"For bug reports, suggestions, documentation, the\n"
                                                 u"source code, and the mailinglist visit Felo's homepage at"),
                              style=wx.ALIGN_CENTER)
        vbox_main.Add(text4, flag=wx.ALIGN_CENTER | wx.LEFT | wx.RIGHT | wx.TOP, border=10)
        vbox_main.Add(wx.lib.hyperlink.HyperLinkCtrl(self, wx.ID_ANY, "http://felo.sourceforge.net",
                                                     style=wx.ALIGN_CENTER),
                      flag=wx.ALIGN_CENTER | wx.LEFT | wx.RIGHT, border=10)
        text5 = wx.StaticText(self, wx.ID_ANY, _(u"English translation by Torsten Bronger."), style=wx.ALIGN_CENTER)
        vbox_main.Add(text5, flag=wx.ALIGN_CENTER | wx.LEFT | wx.RIGHT | wx.TOP, border=10)
        text6 = wx.StaticText(self, wx.ID_ANY, u"© 2006 Torsten Bronger")
        vbox_main.Add(text6, flag=wx.ALIGN_LEFT | wx.LEFT | wx.RIGHT | wx.TOP, border=10)
        hbox_top = wx.BoxSizer(wx.HORIZONTAL)
        hbox_top.Add(vbox_main, flag=wx.ALL | wx.ALIGN_CENTER, border=5)
        self.SetSizer(hbox_top)
        self.Fit()
        for widget in (self, logo, text1, text2, text3, text4, text5, text6):
            widget.Bind(wx.EVT_LEFT_DOWN, self.OnClick)
    def OnClick(self, event):
        self.Destroy()

class Frame(wx.Frame):
    def __init__(self, *args, **keyw):
        wx.Frame.__init__(self, None, wx.ID_ANY, size=(700, 700), title="Felo", *args, **keyw)
        menu_bar = wx.MenuBar()

        menu_file = wx.Menu()
        new = menu_file.Append(wx.ID_ANY, _(u"&New"))
        self.Bind(wx.EVT_MENU, self.OnNew, new)
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

        self.editor = Editor(self)

        menu_edit = wx.Menu()
        undo = menu_edit.Append(wx.ID_ANY, _(u"&Undo")+"\tCtrl-Z")
        self.Bind(wx.EVT_MENU, self.OnUndo, undo)
        redo = menu_edit.Append(wx.ID_ANY, _(u"&Redo")+"\tCtrl-R")
        self.Bind(wx.EVT_MENU, self.OnRedo, redo)
        menu_edit.AppendSeparator()
        cut = menu_edit.Append(wx.ID_ANY, _(u"&Cut")+"\tCtrl-X")
        self.Bind(wx.EVT_MENU, self.OnCut, cut)
        copy = menu_edit.Append(wx.ID_ANY, _(u"C&opy")+"\tCtrl-C")
        self.Bind(wx.EVT_MENU, self.OnCopy, copy)
        paste = menu_edit.Append(wx.ID_ANY, _(u"&Paste")+"\tCtrl-V")
        self.Bind(wx.EVT_MENU, self.OnPaste, paste)
        delete = menu_edit.Append(wx.ID_ANY, _(u"&Delete")+"\tDEL")
        self.Bind(wx.EVT_MENU, self.OnDelete, delete)
        select_all = menu_edit.Append(wx.ID_ANY, _(u"Select &all")+"\tCtrl-A")
        self.Bind(wx.EVT_MENU, self.OnSelectAll, select_all)
        menu_bar.Append(menu_edit, _(u"&Edit"))

        menu_calculate = wx.Menu()
        calculate_felo_numbers = menu_calculate.Append(wx.ID_ANY, _(u"Calculate &Felo ratings"))
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

        self.felo_filename = _("unnamed.felo")
        self.SetTitle(u"Felo – "+os.path.split(self.felo_filename)[1])
        self.editor.Bind(wx.stc.EVT_STC_CHANGE, self.OnChange)
        self.felo_file_changed = False
        self.SendSizeEvent()
        if len(sys.argv) > 1:
            self.open_felo_file(sys.argv[1])
    def OnUndo(self, event):
        self.editor.Undo()
    def OnRedo(self, event):
        self.editor.Redo()
    def OnCopy(self, event):
        self.editor.Copy()
    def OnCut(self, event):
        self.editor.Cut()
    def OnPaste(self, event):
        self.editor.Paste()
    def OnDelete(self, event):
        self.editor.Clear()
    def OnSelectAll(self, event):
        self.editor.SelectAll()
    def OnChange(self, event):
        self.felo_file_changed = True
    def AssureSave(self):
        if self.felo_file_changed:
            answer = wx.MessageBox(_(u"The file \"%s\" has changed.  Save it?") % self.felo_filename,
                                   _(u"File changed"), wx.YES_NO | wx.CANCEL | wx.YES_DEFAULT |
                                   wx.ICON_QUESTION, self)
            if answer == wx.YES:
                self.editor.SaveFile(self.felo_filename)
                self.felo_file_changed = False
            elif answer == wx.CANCEL:
                return wx.CANCEL
    def open_felo_file(self, felo_filename):
        felo_filename = os.path.abspath(felo_filename)
        path = os.path.dirname(felo_filename)
        try:
            os.chdir(path)
        except OSError:
            wx.MessageBox(_(u"Could not open file because folder '%s' doesn't exist.") % path,
                          _(u"Folder not found"), wx.OK | wx.ICON_ERROR, self)
            return
        self.felo_filename = felo_filename
        if os.path.isfile(self.felo_filename):
            self.editor.LoadFile(self.felo_filename)
        self.felo_file_changed = False
        self.SetTitle(u"Felo – "+os.path.split(self.felo_filename)[1])
    def OnNew(self):
        if self.AssureSave == wx.CANCEL:
            return
        self.felo_filename = _("unnamed.felo")
        self.editor.ClearAll()
        self.SetTitle(u"Felo – "+os.path.split(self.felo_filename)[1])
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
        wildcard = _(u"Felo file (*.felo)|*.felo|"
                     "All files (*.*)|*.*")
        dialog = wx.FileDialog(None, _(u"Select Felo file"), os.getcwd(),
                               "", wildcard, wx.SAVE | wx.OVERWRITE_PROMPT)
        if dialog.ShowModal() == wx.ID_OK:
            self.felo_filename = dialog.GetPath()
            dialog.Destroy()
            self.save_felo_file()
    
    def parse_editor_contents(self):
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
        HTML_preview = html_dialog.HTML_preview.GetValue()
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
        if HTML_preview:
            html_window = HtmlFrame(self, html_filename)
            html_window.Show()
        wx.MessageBox(_(u"The following files must be uploaded to the web server:\n\n")+file_list,
                      _(u"Upload file list"), wx.OK | wx.ICON_INFORMATION, self)
    def OnBootstrapping(self, event):
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
        about_window = AboutWindow()
        about_window.ShowModal()
        about_window.Destroy()

class App(wx.App):
    def OnInit(self):
        self.frame = Frame()
        self.frame.Show()
        self.SetTopWindow(self.frame)
        return True

app = App()
app.MainLoop()

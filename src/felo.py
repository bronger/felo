#!/usr/bin/env python
# -*- coding: utf-8 -*-

import wx, wx.grid, wx.py.editor, wx.py.editwindow
import felo_rating
import re, os, codecs, sys, time

parameters, _, fencers, bouts = felo_rating.parse_felo_file("../aachen/florett.felo")

class Editor(wx.py.editor.EditWindow):
    def __init__(self, parent):
        wx.stc.StyledTextCtrl.__init__(self, parent, wx.ID_ANY)
        self.SetTabWidth(8)
        self.setStyles(wx.py.editwindow.FACES)
        self.SetMarginWidth(0, self.TextWidth(wx.stc.STC_STYLE_LINENUMBER, "00000"))
        self.SetMarginWidth(1, 10)

class ResultFrame(wx.Frame):
    def __init__(self, results, *args, **keyw):
        wx.Frame.__init__(self, None, wx.ID_ANY, size=(300, 500), title="Felo-Zahlen", *args, **keyw)
        result_box = wx.TextCtrl(self, wx.ID_ANY, results, style=wx.TE_MULTILINE)
        result_box.SetEditable(False)
        
class HTMLDialog(wx.Dialog):
    def __init__(self, directory, *args, **keyw):
        wx.Dialog.__init__(self, None, wx.ID_ANY, size=(300, 160), title=u"HTML-Export", *args, **keyw)
        wx.StaticText(self, wx.ID_ANY, u"Die Web-Dateien werden in das Verzeichnis\n%s\ngeschrieben."%directory,
                      (20, 20))
        self.plot_switch = wx.CheckBox(self, wx.ID_ANY, u"mit Plot", (35, 80), (150, 20))
        ok_button = wx.Button(self, wx.ID_OK, "Okay", pos=(50, 120))
        ok_button.SetDefault()
        cancel_button = wx.Button(self, wx.ID_CANCEL, "Abbrechen", pos=(150, 120))

class Frame(wx.Frame):
    def __init__(self, *args, **keyw):
        wx.Frame.__init__(self, None, wx.ID_ANY, size=(700, 700), title="Felo", *args, **keyw)
        menu_bar = wx.MenuBar()

        menu_file = wx.Menu()
        open = menu_file.Append(wx.ID_ANY, u"Ö&ffnen")
        self.Bind(wx.EVT_MENU, self.OnOpen, open)
        save = menu_file.Append(wx.ID_ANY, u"&Speichern")
        self.Bind(wx.EVT_MENU, self.OnSave, save)
        save_as = menu_file.Append(wx.ID_ANY, u"Speichern &unter")
        self.Bind(wx.EVT_MENU, self.OnSaveAs, save_as)
        menu_file.AppendSeparator()
        exit = menu_file.Append(wx.ID_ANY, u"&Beenden")
        self.Bind(wx.EVT_MENU, self.OnExit, exit)
        menu_bar.Append(menu_file, u"&Datei")

        menu_numbers = wx.Menu()
        calculate_felo_numbers = menu_numbers.Append(wx.ID_ANY, u"Felo-Zahlen &berechnen")
        self.Bind(wx.EVT_MENU, self.OnCalculateFeloNumbers, calculate_felo_numbers)
        generate_html = menu_numbers.Append(wx.ID_ANY, u"&HTML erzeugen")
        self.Bind(wx.EVT_MENU, self.OnGenerateHTML, generate_html)
        menu_bar.Append(menu_numbers, u"&Bearbeiten")

        self.SetMenuBar(menu_bar)

        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)
        self.felo_filename = self.editor = None
        if len(sys.argv) > 1:
            self.open_felo_file(sys.argv[1])
    def OnModify(self, event):
        self.felo_file_modified = True
    def AssureSave(self):
        if self.editor and self.felo_file_modified:
            answer = wx.MessageBox(u"Die Datei \"%s\" wurde verändert.  Abspeichern?" % self.felo_filename,
                                   u"Datei modifiziert", wx.YES_NO | wx.CANCEL | wx.YES_DEFAULT |
                                   wx.ICON_QUESTION, self)
            if answer == wx.YES:
                self.editor.SaveFile(self.felo_filename)
                self.felo_file_modified = False
            elif answer == wx.CANCEL:
                return wx.CANCEL
    def open_felo_file(self, felo_filename):
        self.felo_filename = os.path.abspath(felo_filename)
        if not self.editor:
            self.editor = Editor(self)
            self.editor.Bind(wx.stc.EVT_STC_MODIFIED, self.OnModify)
        self.editor.LoadFile(self.felo_filename)
        self.felo_file_modified = False
        self.SetTitle(u"Felo – "+os.path.split(self.felo_filename)[1])
        os.chdir(os.path.dirname(self.felo_filename))
    def OnOpen(self, event):
        if self.AssureSave == wx.CANCEL:
            return
        wildcard = u"Felo-Datei (*.felo)|*.felo|" \
            "Alle Dateien (*.*)|*.*"
        dialog = wx.FileDialog(None, u"Felo-Datei wählen", os.getcwd(),
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
            self.felo_file_modified = False
            return True
        return False
    def OnSave(self, event):
        self.save_felo_file()
    def OnSaveAs(self, event):
        if self.editor:
            wildcard = u"Felo-Datei (*.felo)|*.felo|" \
                "Alle Dateien (*.*)|*.*"
            dialog = wx.FileDialog(None, u"Felo-Datei wählen", os.getcwd(),
                                   "", wildcard, wx.SAVE | wx.OVERWRITE_PROMPT)
            if dialog.ShowModal() == wx.ID_OK:
                self.felo_filename = dialog.GetPath()
                dialog.Destroy()
                self.save_felo_file()
    def OnCalculateFeloNumbers(self, event):
        if not self.save_felo_file():
            wx.MessageBox(u"Bitte öffne erst eine Felo-Datei." ,
                          u"Hinweis", wx.OK | wx.ICON_INFORMATION, self)
            return
        parameters, _, fencers, bouts = felo_rating.parse_felo_file(self.felo_filename)
        fencerlist = felo_rating.calculate_felo_ratings(parameters, fencers, bouts)
        results = u""
        for fencer in fencerlist:
            results += fencer.name + u"\t\t" + unicode(fencer.felo_rating) + u"\n"
        result_frame = ResultFrame(results)
        result_frame.Show()
    def OnGenerateHTML(self, event):
        if not self.save_felo_file():
            wx.MessageBox(u"Bitte öffne erst eine Felo-Datei." ,
                          u"Hinweis", wx.OK | wx.ICON_INFORMATION, self)
            return
        if self.AssureSave() == wx.CANCEL:
            return
        parameters, _, fencers, bouts = felo_rating.parse_felo_file(self.felo_filename)
        bouts.sort()
        last_date = time.strftime(u"%d.&nbsp;%B&nbsp;%Y", time.strptime(bouts[-1].date[:10], "%Y/%m/%d"))
        base_filename = parameters[u"Gruppenname"].lower()
        html_dialog = HTMLDialog(parameters[u"Ausgabeverzeichnis"])
        result = html_dialog.ShowModal()
        make_plot = html_dialog.plot_switch.GetValue()
        html_dialog.Destroy()
        if result != wx.ID_OK:
            return
        html_file = codecs.open(os.path.join(parameters[u"Ausgabeverzeichnis"], base_filename+".html"),
                                "w", "utf-8")
        print>>html_file, u"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head><title>%(title)s</title><meta http-equiv="Content-Style-Type" content="text/css" /><style type="text/css">
/*<![CDATA[*/
@import "felo.css";
/*]]>*/
</style></head><body>\n\n<h1>%(title)s</h1>\n<h2>%(date)s</h2>\n\n<table><tbody>""" % \
            {"title": u"Felo-Zahlen "+parameters[u"Gruppenname"], "date": u"vom "+last_date}
        fencerlist = felo_rating.calculate_felo_ratings(parameters, fencers, bouts, plot=make_plot)
        for fencer in fencerlist:
            print>>html_file, u"<tr><td class='name'>%s</td><td class='felo-rating'>%d</td></tr>" % \
                (fencer.name, fencer.felo_rating)
        print>>html_file, u"</tbody></table>"
        if make_plot:
            print>>html_file, u"<img class='felo-plot' src='%s.png' alt='%s' />" % \
                (base_filename, u"Felo-Zahlen-Plot für "+parameters[u"Gruppenname"])
            print>>html_file, u"<p class='printable-notice'>Auch in einer <a href='%s.pdf'>" \
                "ausdruckbaren Version</a>.<p>" % base_filename
        print>>html_file, u"</body></html>"
        html_file.close()

class App(wx.App):
    def OnInit(self):
        self.frame = Frame()
        self.frame.Show()
        self.SetTopWindow(self.frame)
        return True

app = App()
app.MainLoop()

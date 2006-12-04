#!/usr/bin/env python
# -*- coding: utf-8 -*-

import wx, wx.grid, wx.py.editor, wx.py.editwindow, wx.html
import felo_rating
import re, os, codecs, sys, time, StringIO, textwrap, platform

datapath = os.path.abspath(os.path.dirname(__file__))

class HtmlFrame(wx.Frame):
    def __init__(self, parent, file):
        wx.Frame.__init__(self, parent, wx.ID_ANY, u"HTML Vorschau", size=(400, 600))
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
    def OnStyling(self, event):
        return
        start, end = self.PositionFromLine(self.LineFromPosition(self.GetEndStyled())), event.GetPosition()
        text = self.GetTextRange(start, end)
        position = 0
        lines = text.splitlines(True)
        for line in lines:
            cleaned_line = line.lstrip()
            if cleaned_line[0].isdigit():
                # A bout line
                pass
        self.StartStyling(start, 0xff)
        self.SetStyling(end-start, 5)

class ResultFrame(wx.Frame):
    def __init__(self, results, *args, **keyw):
        wx.Frame.__init__(self, None, wx.ID_ANY, size=(300, 500), title="Felo-Zahlen", *args, **keyw)
        result_box = wx.TextCtrl(self, wx.ID_ANY, results, style=wx.TE_MULTILINE)
        result_box.SetEditable(False)
        
class HTMLDialog(wx.Dialog):
    def __init__(self, directory, *args, **keyw):
        wx.Dialog.__init__(self, None, wx.ID_ANY, size=(300, 180), title=u"HTML-Export", *args, **keyw)
        wx.StaticText(self, wx.ID_ANY,
                      textwrap.fill(u"Die Web-Dateien werden in das Verzeichnis %s geschrieben." % directory, 41),
                      (20, 20))
        self.plot_switch = wx.CheckBox(self, wx.ID_ANY, u"mit Plot", (35, 100), (150, 20))
        ok_button = wx.Button(self, wx.ID_OK, "Okay", pos=(50, 140))
        ok_button.SetDefault()
        cancel_button = wx.Button(self, wx.ID_CANCEL, "Abbrechen", pos=(150, 140))

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

        menu_edit = wx.Menu()
        calculate_felo_numbers = menu_edit.Append(wx.ID_ANY, u"&Felo-Zahlen berechnen")
        self.Bind(wx.EVT_MENU, self.OnCalculateFeloRatings, calculate_felo_numbers)
        generate_html = menu_edit.Append(wx.ID_ANY, u"&HTML erzeugen")
        self.Bind(wx.EVT_MENU, self.OnGenerateHTML, generate_html)
        bootstrapping = menu_edit.Append(wx.ID_ANY, u"&Bootstrapping")
        self.Bind(wx.EVT_MENU, self.OnBootstrapping, bootstrapping)
        estimate_freshmen = menu_edit.Append(wx.ID_ANY, u"&Neulinge einschätzen")
        self.Bind(wx.EVT_MENU, self.OnEstimateFreshmen, estimate_freshmen)
        menu_bar.Append(menu_edit, u"&Bearbeiten")

        menu_edit = wx.Menu()
        about = menu_edit.Append(wx.ID_ANY, u"Ü&ber")
        self.Bind(wx.EVT_MENU, self.OnAbout, about)
        menu_bar.Append(menu_edit, u"&Hilfe")

        self.SetMenuBar(menu_bar)

        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)
        self.felo_filename = self.editor = None
        if len(sys.argv) > 1:
            self.open_felo_file(sys.argv[1])
    def OnChange(self, event):
        self.felo_file_changed = True
    def AssureSave(self):
        if self.editor and self.felo_file_changed:
            answer = wx.MessageBox(u"Die Datei \"%s\" wurde verändert.  Abspeichern?" % self.felo_filename,
                                   u"Datei verändert", wx.YES_NO | wx.CANCEL | wx.YES_DEFAULT |
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
        self.editor.LoadFile(self.felo_filename)
        self.felo_file_changed = False
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
            self.felo_file_changed = False
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
    
    def assure_open_felo_file(self):
        if not self.editor:
            wx.MessageBox(u"Bitte öffne erst eine Felo-Datei." ,
                          u"Hinweis", wx.OK | wx.ICON_INFORMATION, self)
            return False
        return True
    def parse_editor_contents(self):
        if not self.assure_open_felo_file():
            return
        felo_file_contents = StringIO.StringIO(self.editor.GetText())
        felo_file_contents.name = self.felo_filename
        try:
            parameters, _, fencers, bouts = felo_rating.parse_felo_file(felo_file_contents)
        except felo_rating.LineError, e:
            self.editor.GotoLine(e.linenumber - 1)
            wx.MessageBox(u"Fehler in Zeile %d: %s" % (e.linenumber, e.naked_description),
                          u"Parsefehler", wx.OK | wx.ICON_ERROR, self)
            return
        except felo_rating.FeloFormatError, e:
            wx.MessageBox(e.description, u"Parsefehler", wx.OK | wx.ICON_ERROR, self)
            return
        except Exception, e:
            wx.MessageBox(e.description, u"Allgemeiner Fehler", wx.OK | wx.ICON_ERROR, self)
            return
        return parameters, fencers, bouts
    def OnCalculateFeloRatings(self, event):
        parameters, fencers, bouts = self.parse_editor_contents()
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
        bouts.sort()
        last_date = time.strftime(u"%d.&nbsp;%B&nbsp;%Y", time.strptime(bouts[-1].date[:10], "%Y/%m/%d"))
        base_filename = parameters[u"Gruppenname"].lower()
        html_dialog = HTMLDialog(parameters[u"Ausgabeverzeichnis"])
        result = html_dialog.ShowModal()
        make_plot = html_dialog.plot_switch.GetValue()
        html_dialog.Destroy()
        if result != wx.ID_OK:
            return
        file_list = u""
        html_filename = os.path.join(parameters[u"Ausgabeverzeichnis"], base_filename+".html")
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
            {"title": u"Felo-Zahlen "+parameters[u"Gruppenname"], "date": u"vom "+last_date}
        try:
            fencerlist = felo_rating.calculate_felo_ratings(parameters, fencers, bouts, plot=make_plot)
        except felo_rating.ExternalProgramError, e:
            wx.MessageBox(e.description, u"Externes Programm nicht gefunden", wx.OK | wx.ICON_ERROR, self)
            return
        for fencer in fencerlist:
            print>>html_file, u"<tr><td class='name'>%s</td><td class='felo-rating'>%d</td></tr>" % \
                (fencer.name, fencer.felo_rating)
        print>>html_file, u"</tbody></table>"
        if make_plot:
            print>>html_file, u"<p class='felo-plot'><img class='felo-plot' src='%s.png' alt='%s' /></p>" % \
                (base_filename, u"Felo-Zahlen-Plot für "+parameters[u"Gruppenname"])
            print>>html_file, u"<p class='printable-notice'>Auch in einer <a href='%s.pdf'>" \
                "ausdruckbaren Version</a>.</p>" % base_filename
            file_list += base_filename+".png\n"
            file_list += base_filename+".pdf\n"
        print>>html_file, u"</body></html>"
        html_file.close()
        html_window = HtmlFrame(self, html_filename)
        html_window.Show()
        wx.MessageBox(u"Die folgenden Dateien müssen nun auf den Webserver kopiert werden:\n\n"+file_list,
                      u"Datei modifiziert", wx.OK | wx.ICON_INFORMATION, self)
    def OnBootstrapping(self, event):
        if not self.assure_open_felo_file():
            return
        answer = wx.MessageBox(u"Das Bootstrapping wird die Fechter-Daten verändern.  "
                               "Willst du wirklich fortfahren?",
                               u"Bootstrapping", wx.YES_NO | wx.NO_DEFAULT |
                               wx.ICON_QUESTION, self)
        if answer != wx.YES:
            return
        felo_file_contents = StringIO.StringIO(self.editor.GetText())
        felo_file_contents.name = self.felo_filename
        parameters, _, fencers, bouts = felo_rating.parse_felo_file(felo_file_contents)
        felo_rating.calculate_felo_ratings(parameters, fencers, bouts, bootstrapping=True)
        for fencer in fencers.values():
            if not fencer.freshman:
                fencer.initial_felo_rating = fencer.felo_rating
        self.editor.SetText(felo_rating.write_back_fencers(self.editor.GetText(), fencers))
        self.felo_file_changed = True
    def OnEstimateFreshmen(self, event):
        if not self.assure_open_felo_file():
            return
        answer = wx.MessageBox(u"Das Einschätzen der Neulinge wird u.U. deren Fechter-Daten verändern.  "
                               "Willst du wirklich fortfahren?",
                               u"Einschätzen der Neulinge", wx.YES_NO | wx.NO_DEFAULT |
                               wx.ICON_QUESTION, self)
        if answer != wx.YES:
            return
        felo_file_contents = StringIO.StringIO(self.editor.GetText())
        felo_file_contents.name = self.felo_filename
        parameters, _, fencers, bouts = felo_rating.parse_felo_file(felo_file_contents)
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

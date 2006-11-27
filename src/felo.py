#!/usr/bin/env python
# -*- coding: utf-8 -*-

import wx, wx.grid
import felo_rating
import re

parameters, fencers, bouts = felo_rating.parse_felo_file("florett.felo")

class BoutTable(wx.grid.PyGridTableBase):
    def __init__(self):
        wx.grid.PyGridTableBase.__init__(self)

        self.odd = wx.grid.GridCellAttr()
        self.odd.SetBackgroundColour("gray90")
        self.odd.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD))
        self.even = wx.grid.GridCellAttr()
        self.even.SetBackgroundColour("white")
        self.even.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD))

        self.colLabels = ["Datum", "Fechter 1", "Fechter 2", "Punkte 1", "Punkte 2",
                          "Gefochten auf"]
        self.dataTypes = [wx.grid.GRID_VALUE_STRING,
                          wx.grid.GRID_VALUE_STRING,
                          wx.grid.GRID_VALUE_STRING,
                          wx.grid.GRID_VALUE_NUMBER + ':0,15',
                          wx.grid.GRID_VALUE_NUMBER + ':0,15',
                          wx.grid.GRID_VALUE_CHOICE + ':0,5,10,15']

    def extract_bout_by_column(self, bout, col):
        if col == 0:
            return bout.date
        elif col == 1:
            return bout.first_fencer
        elif col == 2:
            return bout.second_fencer
        elif col == 3:
            return bout.points_first
        elif col == 4:
            return bout.points_second
        elif col == 5:
            return bout.fenced_to

    def unknown_fencer_warning(self, fencer_name):
        wx.MessageBox("Achtung: Fechter \"%s\" ist unbekannt." % fencer_name, caption="Fechter unbekannt",
                      style=wx.OK | wx.ICON_WARNING)

    def set_bout_by_column(self, bout, col, value):
        if col == 0:
            bout.date = value
        elif col == 1:
            bout.first_fencer = value
            if not fencers.has_key(value):
                self.unknown_fencer_warning(value)
        elif col == 2:
            bout.second_fencer = value
            if not fencers.has_key(value):
                self.unknown_fencer_warning(value)
        elif col == 3:
            bout.points_first = value
        elif col == 4:
            bout.points_second = value
        elif col == 5:
            bout.fenced_to = value

    def GetNumberRows(self):
        return len(bouts) + 1

    def GetNumberCols(self):
        return len(self.colLabels)

    def IsEmptyCell(self, row, col):
        try:
            return not bouts[row]
        except IndexError:
            return True

    def GetValue(self, row, col):
        try:
            return self.extract_bout_by_column(bouts[row], col)
        except IndexError:
            return ""

    def SetValue(self, row, col, value):
        try:
            self.set_bout_by_column(bouts[row], col, value)
        except IndexError:
            # add a new row
            if bouts:
                year, month, day = bouts[-1].year, bouts[-1].month, bouts[-1].day
            else:
                year, month, day = 2006, 11, 23
            bouts.append(felo_rating.Bout(year, month, day))
            self.SetValue(row, col, value)
            msg = wx.grid.GridTableMessage(self, wx.grid.GRIDTABLE_NOTIFY_ROWS_APPENDED, 1)
            self.GetView().ProcessTableMessage(msg)

    def GetAttr(self, row, col, kind):
        attr = [self.even, self.odd][row % 2]
        attr.IncRef()
        return attr

    def GetColLabelValue(self, col):
        return self.colLabels[col]

    def GetTypeName(self, row, col):
        return self.dataTypes[col]

    def CanGetValueAs(self, row, col, typeName):
        colType = self.dataTypes[col].split(':')[0]
        if typeName == colType:
            return True
        else:
            return False

    def CanSetValueAs(self, row, col, typeName):
        return self.CanGetValueAs(row, col, typeName)

class Frame(wx.Frame):
    def __init__(self, *args, **keyw):
        wx.Frame.__init__(self, None, wx.ID_ANY, size=(700, 200), title="Felo-Zahlen", *args, **keyw)
        menu_bar = wx.MenuBar()

        menu_file = wx.Menu()
        menu_file.Append(wx.ID_ANY, u"Ö&ffnen")
        menu_file.Append(wx.ID_ANY, u"&Speichern")
        menu_file.Append(wx.ID_ANY, u"Speichern &unter")
        menu_file.AppendSeparator()
        exit = menu_file.Append(wx.ID_ANY, u"&Beenden")
        self.Bind(wx.EVT_MENU, self.OnExit, exit)
        menu_bar.Append(menu_file, u"&Datei")

        menu_numbers = wx.Menu()
        menu_numbers.Append(wx.ID_ANY, u"&Fechter bearbeiten")
        menu_numbers.Append(wx.ID_ANY, u"&Parameter einsehen/ändern")
        menu_numbers.AppendSeparator()
        menu_numbers.Append(wx.ID_ANY, u"Felo-Zahlen &berechnen")
        menu_bar.Append(menu_numbers, u"&Bearbeiten")

        self.SetMenuBar(menu_bar)

        self.table = BoutTable()
        self.grid = wx.grid.Grid(self)
        self.grid.SetTable(self.table, True, selmode=wx.grid.Grid.SelectRows)

    def OnExit(self, event):
        self.Close()

class App(wx.App):
    def OnInit(self):
        self.frame = Frame()
        self.frame.Show()
        self.SetTopWindow(self.frame)
        return True

app = App()
app.MainLoop()

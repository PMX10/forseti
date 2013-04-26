#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

import wx

class TeamPanel(wx.Panel):

    def __init__(self, number, name='', *args, **kwargs):
        super(TeamPanel, self).__init__(*args, **kwargs) 
        self.number = number
        self.name = name
        self.InitUI()

    def InitUI(self):
        dc = wx.ScreenDC()
        number = wx.TextCtrl(self, size=(dc.GetCharWidth() * 2, dc.GetCharHeight()))
        number.AppendText(str(self.number))
        text = wx.TextCtrl(self)
        text.AppendText(self.name)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(number)
        hbox.Add(text)

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(hbox)
        vbox.Add(wx.Button(self, label='Reset'), flag=wx.CENTER)
        vbox.Add(wx.Button(self, label='Configure'), flag=wx.CENTER)
        vbox.Add(wx.Button(self, label='Disable'), flag=wx.CENTER)

        self.SetSizer(vbox)
        self.Show(True)


class MatchControl(wx.Panel):

    def __init__(self, *args, **kwargs):
        super(MatchControl, self).__init__(*args, **kwargs) 
        self.InitUI()

    def InitUI(self):
        vbox = wx.BoxSizer(wx.VERTICAL)

        teamSizer = wx.GridSizer(2, 2)
        teamSizer.AddMany([(TeamPanel(i, 'Team {}'.format(i), self), 0) for i in range(1, 5)])
        vbox.Add(teamSizer, flag=wx.CENTER)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(wx.Button(self, label='Start'))
        hbox.Add(wx.Button(self, label='Pause'))
        hbox.Add(wx.Button(self, label='Reset'))
        hbox.Add(wx.StaticText(self, label='0:00'))
        vbox.Add(hbox, flag=wx.CENTER)

        self.SetSizer(vbox)
        self.SetSize((200, 200))
        self.Show(True)


class MainWindow(wx.Frame):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs) 
        self.InitUI()

    def InitUI(self):    
        menubar = wx.MenuBar()
        fileMenu = wx.Menu()
        fitem = fileMenu.Append(wx.ID_EXIT, 'Quit', 'Quit application')
        menubar.Append(fileMenu, '&File')
        self.SetMenuBar(menubar)
        MatchControl(self)

        self.Bind(wx.EVT_MENU, self.OnQuit, fitem)

        self.SetSize((800, 600))
        self.SetTitle('Forseti Dashboard')
        self.Centre()
        self.Show(True)

    def OnQuit(self, e):
        self.Close()


def main():
    
    app = wx.App()
    MainWindow(None)
    app.MainLoop()    


if __name__ == '__main__':
    main()

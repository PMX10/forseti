#!/usr/bin/env python2.7

import wx
import random
import threading
import time
import lcm

from Forseti import *

class GoalVis(wx.Frame):
    def __init__(self, parent, id, title, lcm):
        wx.Frame.__init__(self, parent, id, title, size=(180, 380))

        self.statusbar = self.CreateStatusBar()
        self.statusbar.SetStatusText('0')
        self.board = Board(self, lcm)
        self.board.SetFocus()
        self.board.start()

        self.Centre()
        self.Show(True)

class Board(wx.Panel):
    Speed = 50
    ID_TIMER = 1

    def __init__(self, parent, lcm):
        wx.Panel.__init__(self, parent)
        self.lcm = lcm;
        subscription = self.lcm.subscribe("Goals/Goals", self.msg_handler)
        self._read_thread = threading.Thread(target=self._read_loop)
        self._read_thread.daemon = True
        # self._write_thread = threading.Thread(target=self._write_loop)
        # self._write_thread.daemon = True
        self._health_thread = threading.Thread(target=self._health_loop)
        self._health_thread.daemon = True
        self.startTime = time.time()
        self.flagsLock = threading.Lock()
        self.goalboxes = GoalBoxes()
        self.goalboxes.goals = [[1,2,1,0,0], [0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0]]
        self.timer = wx.Timer(self, Board.ID_TIMER)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_TIMER, self.OnTimer, id=Board.ID_TIMER)

    def read_start(self):
        self._read_thread.start()

    # def write_start(self):
    #     self._write_thread.start()

    def health_start(self):
        self._health_thread.start()

    def _read_loop(self):
        try:
            while True:
                print "read looping"
                self.lcm.handle()
        except:
            pass

    def _health_loop(self):
        while True:
            #print "health looping"
            msg = Health()
            msg.uptime = time.time() - self.startTime
            self.lcm.publish("GoalVis/Health", msg.encode())
            time.sleep(0.25)

    # def _write_loop(self):
    #     while True:
    #         self.flagsLock.acquire()
    #         self.lcm.publish("MaestroDriver/Flags", self.flags.encode())
    #         #self.lcm.publish("Goals/Goals", self.goalboxes.encode())
    #         self.flagsLock.release()
    #         time.sleep(0.1)

    def msg_handler(self, channel, data):
        print "received message"
        if channel == "Goals/Goals":
            msg = GoalBoxes.decode(data)
            print ("received Goals!")
#            print("reader=" + msg.reader)
#            print("tagId="  + str(msg.tagId))

            # add to goalboxes
            self.flagsLock.acquire()
            self.goalboxes = msg;
            self.flagsLock.release()


    def squareWidth(self):
        return self.GetClientSize().GetWidth() / Board.BoardWidth

    def squareHeight(self):
        return self.GetClientSize().GetHeight() / Board.BoardHeight

    def start(self):
        self.timer.Start(Board.Speed)
        self.read_start()
        self.health_start()

    def drawGoals(self, dc):
        for goal in range(0, 4):
            for box in range(0, 5):
                val = msg.goals[goal][box]
#                       print("received goal=" + str(goal) + ", box=" + str(box) + ", value=" + str(val))

    def drawSquare(self, dc, x, y, shape):
        colors = ['#000000', '#CC6666', '#66CC66', '#6666CC',
                  '#CCCC66', '#CC66CC', '#66CCCC', '#DAAA00']

        light = ['#000000', '#F89FAB', '#79FC79', '#7979FC',
                 '#FCFC79', '#FC79FC', '#79FCFC', '#FCC600']

        dark = ['#000000', '#803C3B', '#3B803B', '#3B3B80',
                '#80803B', '#803B80', '#3B8080', '#806200']

        pen = wx.Pen(light[shape])
        pen.SetCap(wx.CAP_PROJECTING)
        dc.SetPen(pen)

        dc.DrawLine(x, y + self.squareHeight() - 1, x, y)
        dc.DrawLine(x, y, x + self.squareWidth() - 1, y)

        darkpen = wx.Pen(dark[shape])
        darkpen.SetCap(wx.CAP_PROJECTING)
        dc.SetPen(darkpen)

        dc.DrawLine(x + 1, y + self.squareHeight() - 1,
                    x + self.squareWidth() - 1, y + self.squareHeight() - 1)
        dc.DrawLine(x + self.squareWidth() - 1,
                    y + self.squareHeight() - 1, x + self.squareWidth() - 1, y + 1)

        dc.SetPen(wx.TRANSPARENT_PEN)
        dc.SetBrush(wx.Brush(colors[shape]))
        dc.DrawRectangle(x + 1, y + 1, self.squareWidth() - 2,
                         self.squareHeight() - 2)

    def OnTimer(self, event):
        #print "repainting"
        self.Refresh()

    def OnPaint(self, event):

        dc = wx.PaintDC(self)

        dc.SetPen(wx.Pen('#ffffff'))
        dc.SetBrush(wx.Brush("#0066ff"))
        self.flagsLock.acquire()
        for goal in range(0,4):
            for box in range(0,5):
                boxval = self.goalboxes.goals[goal][box]
                if boxval == 0:
                    dc.SetBrush(wx.Brush("#efefef"))
                elif boxval == 1:
                    dc.SetBrush(wx.Brush("#0000ff"))
                elif boxval == 2:
                    dc.SetBrush(wx.Brush("#ff0000"))
                dc.DrawRectangle(goal * 100, box * 100, 100, 100)
        self.flagsLock.release()

if __name__ == '__main__':
    print "starting goal_vis..."

    lc = lcm.LCM("udpm://239.255.76.67:7667?ttl=1")
    print "LCM Initialized!"

    app = wx.App()
    GoalVis(None, -1, 'goal_vis.py', lc)
    app.MainLoop()

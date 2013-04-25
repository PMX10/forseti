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
        self.lcm.subscribe("Goals/Goals", self.msg_handler)
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
        self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.Bind(wx.EVT_TIMER, self.OnTimer, id=Board.ID_TIMER)
        self.selected_goal = 0
        self.selected_box = 0

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

    def OnTimer(self, event):
        self.Refresh()

    def OnPaint(self, event):

        dc = wx.PaintDC(self)

        dc.SetPen(wx.Pen('#ffffff'))
        dc.SetBrush(wx.Brush("#0066ff"))
        width = self.GetClientSize().GetWidth() / 4
        height = self.GetClientSize().GetHeight() / 6
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
                dc.DrawRectangle(goal * width, (4- box) * height, width, height)
                dc.DrawText("goal" + str(goal) + ",box" + str(box), goal * width,  (4 - box) * height )
        dc.SetBrush(wx.Brush("#00ff00"))
        dc.DrawRectangle(self.selected_goal * width, 5 * height, width, height / 10)

        self.flagsLock.release()


    def OnKeyDown(self, event):
        print("event=" + str(event))
        keycode = event.GetKeyCode()
        print("keycode=" + str(keycode))
        if keycode == wx.WXK_LEFT:
            self.selected_goal = self.selected_goal - 1
            if self.selected_goal < 0:
                self.selected_goal = 0
        elif keycode == wx.WXK_RIGHT:
            self.selected_goal = self.selected_goal + 1
            if self.selected_goal > 3:
                self.selected_goal = 3


        # if not self.isStarted or self.curPiece.shape() == Tetrominoes.NoShape:
        #     event.Skip()
        #     return


        # if keycode == ord('P') or keycode == ord('p'):
        #     self.pause()
        #     return
        # if self.isPaused:
        #     return
        # elif keycode == wx.WXK_LEFT:
        #     self.tryMove(self.curPiece, self.curX - 1, self.curY)
        # elif keycode == wx.WXK_RIGHT:
        #     self.tryMove(self.curPiece, self.curX + 1, self.curY)
        # elif keycode == wx.WXK_DOWN:
        #     self.tryMove(self.curPiece.rotatedRight(), self.curX, self.curY)
        # elif keycode == wx.WXK_UP:
        #     self.tryMove(self.curPiece.rotatedLeft(), self.curX, self.curY)
        # elif keycode == wx.WXK_SPACE:
        #     self.dropDown()
        # elif keycode == ord('D') or keycode == ord('d'):
        #     self.oneLineDown()
        # else:
        #     event.Skip()

if __name__ == '__main__':
    print "starting goal_vis..."

    lc = lcm.LCM("udpm://239.255.76.67:7667?ttl=1")
    print "LCM Initialized!"

    app = wx.App()
    GoalVis(None, -1, 'goal_vis.py', lc)
    app.MainLoop()

#!/usr/bin/env python2.7

import wx
import random
import threading
import time
import lcm
import argparse
import json

from Forseti import *

class GoalVis(wx.Frame):
    def __init__(self, parent, id, title, lcm, field_table):
        wx.Frame.__init__(self, parent, id, title, size=(180, 380))

        self.board = Board(self, lcm, field_table)
        self.board.SetFocus()
        self.board.start()
        self.Centre()
        self.Show(True)

class Board(wx.Panel):
    Speed = 50
    ID_TIMER = 1

    def __init__(self, parent, lcm, field_table):
        wx.Panel.__init__(self, parent)
        # LCM
        self.lcm = lcm;
        self.lcm.subscribe("GoalReader/Tags", self.msg_handler)
        self._read_thread = threading.Thread(target=self._read_loop)
        self._read_thread.daemon = True
        self.startTime = time.time()
        self._health_thread = threading.Thread(target=self._health_loop)
        self._health_thread.daemon = True

        # sends Goals
        self._write_thread = threading.Thread(target=self._write_loop)
        self._write_thread.daemon = True
        self.goalBoxesLock = threading.Lock()
        self.goalboxes = GoalBoxes()
        self.goalboxes.goals = [[0,0,0,0,0], [0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0]]

        # wx timers, events
        self.timer = wx.Timer(self, Board.ID_TIMER)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.Bind(wx.EVT_TIMER, self.OnTimer, id=Board.ID_TIMER)

        # Incoming box selection
        self.selected_goal = 0
        self.selected_box = 0
        self.selected_tags_lock = threading.Lock()
        self.selected_tags = []

        self.field_table = field_table
        self.readers_to_goals = {'A':0, 'B':1, 'C':2, 'D':3}
        self.last_tag_id = 0

    def _read_loop(self):
        try:
            while True:
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

    def _write_loop(self):
        while True:
            self.goalBoxesLock.acquire()
            self.lcm.publish("Goals/Goals", self.goalboxes.encode())
            self.goalBoxesLock.release()
            time.sleep(0.1)

    def msg_handler(self, channel, data):
        print "received message"
        if channel == "GoalReader/Tags":
            msg = Tag.decode(data)
            print ("received tag!")
            print("reader=" + msg.reader)
            print("tagId="  + str(msg.tagId))

            self.lcm.publish("GoalReader/TagConfirm", data)
            try:
                goal = self.readers_to_goals[msg.reader]
                print "goal=" + str(goal)

                self.selected_tags_lock.acquire()
                self.selected_tags.append(
                    {"Goal":goal,
                     "Type":self.get_object_type(msg.tagId),
                     "TagId":msg.tagId
                     })
                print("tags added")
                print("selected_tags:" + str(json.dumps(self.selected_tags)))
                self.selected_tags_lock.release()
                print ("message handler exiting")
            except KeyError as e:
                print "KeyError" + str(e)

    def get_object_type(self, uid):
        '''
        Returns the object_type of the box associated with the provided uid.
        '''
        for table in self.field_table:
            if table['tagId'] == unicode(uid):
                print "object recognized!"
                return int(table['objectType'])
        return 0 #an unrecognized object has no type

    def start(self):
        self.timer.Start(Board.Speed)
        self._read_thread.start()
        self._write_thread.start()
        self._health_thread.start()

    def OnTimer(self, event):
        self.Refresh()

    def OnPaint(self, event):
        dc = wx.PaintDC(self)

        dc.SetPen(wx.Pen('#ffffff'))
        dc.SetBrush(wx.Brush("#0066ff"))
        width = self.GetClientSize().GetWidth() / 4
        height = self.GetClientSize().GetHeight() / 10
        self.goalBoxesLock.acquire()
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
        dc.SetBrush(wx.Brush("#ffff00"))
        dc.DrawRectangle(self.selected_goal * width, 5 * height, width, height / 10)
        for i in range(len(self.selected_tags)):
            next_item = self.selected_tags[i]
            goal = next_item["Goal"]
            boxval = next_item["Type"]
            tagID = next_item["TagId"]
            if boxval == 0:
                dc.SetBrush(wx.Brush("#efefef"))
            elif boxval == 1:
                dc.SetBrush(wx.Brush("#0066ff"))
            elif boxval == 2:
                dc.SetBrush(wx.Brush("#ff6600"))
            dc.DrawRectangle(goal * width, (5 + i) * height, width, height)
            dc.DrawText("tagID=" + str(tagID), goal * width, (5 + i) * height)


        self.goalBoxesLock.release()


    def OnKeyDown(self, event):
        print("event=" + str(event))
        keycode = event.GetKeyCode()
        print("keycode=" + str(keycode))
        self.goalBoxesLock.acquire()
        self.selected_tags_lock.acquire()

        if keycode == wx.WXK_RETURN:
            if len(self.selected_tags) > 0:
                next_item = self.selected_tags.pop(0)
                goal = next_item["Goal"]
                boxval = next_item["Type"]
                self.goalboxes.goals[goal].insert(0, boxval)
        elif keycode == wx.WXK_ESCAPE:
            if len(self.selected_tags) > 0:
                next_item = self.selected_tags.pop(0)
        elif keycode == wx.WXK_LEFT:
            self.selected_goal = self.selected_goal - 1
            if self.selected_goal < 0:
                self.selected_goal = 0
        elif keycode == wx.WXK_RIGHT:
            self.selected_goal = self.selected_goal + 1
            if self.selected_goal > 3:
                self.selected_goal = 3
        self.selected_tags_lock.release()
        self.goalBoxesLock.release()

if __name__ == '__main__':
    print "starting goal_vis..."

    lc = lcm.LCM("udpm://239.255.76.67:7667?ttl=1")
    print "LCM Initialized!"

    # Provide arguments for the field_mapping json file
    parser = argparse.ArgumentParser()
    parser.add_argument('--load', type=str, action='store')
    args = parser.parse_args()
    field_file = args.load or 'resources/field_mapping.json'
    field_objects = '[]'
    with open(field_file, 'r') as rfile:
        field_objects = rfile.read()

    field_table = json.loads(field_objects)

    # Start application
    app = wx.App()
    GoalVis(None, -1, 'goal_vis.py', lc, field_table)
    app.MainLoop()

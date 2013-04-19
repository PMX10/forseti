#!/usr/bin/env python2.7
from __future__ import print_function
import Tkinter
tki = Tkinter

app = tki.Tk()
app['background'] = 'black'

class DisableButton(tki.Button):

    def __init__(self, callback, *args, **kwargs):

        tki.Button.__init__(self, *args, **kwargs)

        self['text'] = 'disable'
        self['command'] = self.press
        self.callback = callback

    def press(self):
        if self['text'] == 'disable':
            self['text'] = 'enable'
            self.callback('enable')
        else:
            self['text'] = 'disable'
            self.callback('disable')

goal_frame = tki.Frame(app)
goal_frame['background'] = 'black'

class Goal(object):

    def __init__(self, root, idx):
        self.root = root
        self.frame = tki.Frame(root)
        self.name = 'Goal {}'.format(idx)
        self.label = tki.Label(self.frame, 
                               text=self.name, 
                               width=10)
        self.label.pack(side='top')
        self.confirm_frame = tki.Frame(self.frame)
        self.confirm_frame.pack(side='top')
        self.frame.pack(side='left')

    def add_confirm(self, text):
        entry_frame = tki.Frame(self.confirm_frame)
        label = tki.Label(entry_frame, text=text)
        label.pack(side='left')
        confirm_button = tki.Button(entry_frame, text='Confirm')
        confirm_button.pack(side='left')
        confirm_button['command'] = lambda: self.remove_confirm(entry_frame)
        refuse_button = tki.Button(entry_frame, text='Refuse')
        refuse_button.pack(side='left')
        refuse_button['command'] = lambda: self.remove_confirm(entry_frame)
        entry_frame.pack(side='top')

    def remove_confirm(self, frame):
        frame.destroy
        self.frame.pack()
        goal_frame.pack()

class Team(object):

    def __init__(self, number, name='', color='gold'):
        self.number = number
        self.name = name
        self.color = color

    def add_gui(self, root):
        frame = tki.Frame(root)
        frame['borderwidth'] = 0
        name_label = tki.Label(root, text='Name:')
        name_entry = tki.Entry(root)
        name_entry.insert(0, self.name)
        number_label = tki.Label(root, text='Number:')
        number_entry = tki.Entry(root)
        number_entry.insert(0, str(self.number))
        disable_button = DisableButton(self.change_state, root)
        for widget in [name_label, name_entry, number_label, number_entry,
                disable_button]:
            widget['background'] = self.color
            widget['borderwidth'] = 0
            widget['relief'] = 'flat'
            #widget['relief'] = 'raised'
            #widget['highlightbackground'] = '#00618e'
            #widget['highlightthickness'] = 1
            widget['highlightthickness'] = 0
            #widget['relief'] = 'sunken'
            widget.pack(side='top')
            if self.color == 'blue':
                widget['fg'] = 'white'
            #widget.pack(side='left')
        return frame

    def change_state(self, new_state):
        print(new_state)

class Match(object):

    def __init__(self, teams=None):
        if teams is None:
            self.teams = [Team(0, 'Team {}'.format(i), 'blue' if i < 2 else 'gold') for i in range(4)]
        else:
            self.teams = teams
        self.frame = None

    def add_gui(self, root):
        frame = tki.Frame(root)
        self.frame = frame
        command_frame = tki.Frame(frame)
        start = tki.Button(command_frame, text='Start')
        start['command'] = self.start
        pause = tki.Button(command_frame, text='Pause')
        pause['command'] = self.pause
        initialize = tki.Button(command_frame, text='Initialize')
        initialize['command'] = self.initialize
        state = tki.Label(command_frame, text='Auto')
        timer = tki.Label(command_frame, text='2:00')
        for wid in [start, pause, initialize, state, timer]:
            wid.pack(side='left')
        left_teams = tki.Frame(frame)
        left_teams['background'] = 'blue'
        right_teams = tki.Frame(frame)
        right_teams['background'] = 'gold'
        command_frame.pack(side='bottom')
        left_teams.pack(side='left')
        right_teams.pack(side='left')
        for i in range(2):
            self.teams[i].add_gui(left_teams).pack(side='top')
        for i in range(2, 4):
            self.teams[i].add_gui(right_teams).pack(side='top')
        frame.pack(side='bottom')

    def timer_loop(self):
        start_time = time.time()

    def start(self):
        print('Start')

    def pause(self):
        print('Pause')

    def initialize(self):
        print('Initialize')

goals = [Goal(goal_frame, i) for i in range(4)]

#goals[2].add_confirm('Multiply')
    
goal_frame.pack({'side':'top'})

m = Match()
m.add_gui(app)

app.mainloop()

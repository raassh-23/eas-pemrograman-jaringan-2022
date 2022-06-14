import os
import json
import base64
from glob import glob
import shelve

class PlayerServerInterface:
    def __init__(self):
        self.players = shelve.open('g.db', writeback=True)

    def set_location(self, params=[]):
        try:
            pnum = params[0]
            x = params[1]
            y = params[2]
            player = self.players[pnum].split(',')
            angle = player[2]
            self.players[pnum] = f"{x},{y},{angle},{0}"
            self.players.sync()
            return dict(status='OK')
        except Exception as e:
            return dict(status='ERROR', data=str(e))

    def set_angle(self, params=[]):
        try:
            pnum = params[0]
            angle = params[1]
            player = self.players[pnum].split(',')
            x = player[0]
            y = player[1]
            self.players[pnum] = f"{x},{y},{angle},{0}"
            self.players.sync()
            return dict(status='OK')
        except Exception as e:
            return dict(status='ERROR', data=str(e))

    def join(self, params=[]):
        try:
            pnum = params[0]
            x = params[1]
            y = params[2]
            angle = params[3]
            self.players[pnum] = f"{x},{y},{angle},{0}"
            self.players.sync()

            players = []
            for key in self.players:
                data = self.players[key].split(',')
                player = {
                    'id': key,
                    'x': data[0],
                    'y': data[1],
                    'angle': data[2],
                    'left': data[3]
                }
                players.append(player)
            return dict(status='OK', players=players)
        except Exception as e:
            return dict(status='ERROR', data=str(e))

    def refresh(self, params=[]):
        try:
            players = []
            for key in self.players:
                data = self.players[key].split(',')
                player = {
                    'id': key,
                    'x': data[0],
                    'y': data[1],
                    'angle': data[2],
                    'left': data[3]
                }
                players.append(player)
            return dict(status='OK', players=players)
        except Exception as e:
            return dict(status='ERROR', data=str(e))

    def leave(self, params=[]):
        try:
            pnum = params[0]
            player = self.players[pnum].split(',')
            x = player[0]
            y = player[1]
            angle = player[2]
            self.players[pnum] = f"{x},{y},{angle},{1}"
            self.players.sync()
            return dict(status='OK')
        except Exception as e:
            return dict(status='ERROR', data=str(e))


if __name__ == '__main__':
    p = PlayerServerInterface()
    print(p.join(['1', '0', '0', '0']))
    print(p.refresh())
    print(p.set_location(['1', '10', '-10']))
    print(p.refresh())
    print(p.set_angle(['1', '90']))
    print(p.refresh())
    print(p.leave(['1']))
    print(p.refresh())


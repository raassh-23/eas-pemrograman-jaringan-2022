import os
import json
import base64
from glob import glob
import shelve

class PlayerServerInterface:
    def __init__(self):
        self.players = shelve.open('g.db', writeback=True)

    def set_position(self, params=[]):
        try:
            pnum = params[0]
            x = params[1]
            y = params[2]
            player = self.players[pnum].split(',')
            self.players[pnum] = f"{x},{y},{player[2]}"
            self.players.sync()
            return dict(status='OK')
        except Exception as e:
            return dict(status='ERROR', data=str(e))

    def set_angle(self, params=[]):
        try:
            pnum = params[0]
            angle = params[1]
            player = self.players[pnum].split(',')
            self.players[pnum] = f"{player[0]},{player[1]},{angle}"
            self.players.sync()
            return dict(status='OK')
        except Exception as e:
            return dict(status='ERROR', data=str(e))

    def join(self, params=[]):
        try:
            pnum = params[0]

            if pnum in self.players:
                return dict(status='ERROR', data='player already exists')

            x = params[1]
            y = params[2]
            angle = params[3]
            self.players[pnum] = f"{x},{y},{angle}"
            self.players.sync()

            players = []
            for key in self.players:
                data = self.players[key].split(',')
                player = {
                    'name': key,
                    'x': data[0],
                    'y': data[1],
                    'angle': data[2]
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
                    'name': key,
                    'x': data[0],
                    'y': data[1],
                    'angle': data[2]
                }
                players.append(player)
            return dict(status='OK', players=players)
        except Exception as e:
            return dict(status='ERROR', data=str(e))

    def leave(self, params=[]):
        try:
            pnum = params[0]
            del self.players[pnum]
            self.players.sync()
            return dict(status='OK')
        except Exception as e:
            return dict(status='ERROR', data=str(e))


if __name__ == '__main__':
    p = PlayerServerInterface()
    print(p.join(['1', '0', '0', '0']))
    print(p.refresh())
    print(p.set_position(['1', '10', '-10']))
    print(p.refresh())
    print(p.set_angle(['1', '90']))
    print(p.refresh())
    print(p.leave(['1']))
    print(p.refresh())


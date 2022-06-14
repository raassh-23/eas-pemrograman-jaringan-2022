import os
import json
import base64
from glob import glob
import shelve

class PlayerServerInterface:
    def __init__(self):
        self.players = shelve.open('g.db', writeback=True)

    def set_location(self, params=[]):
        pnum = params[0]
        x = params[1]
        y = params[2]
        try:
            self.players[pnum] = f"{x},{y}"
            self.players.sync()
            return dict(status='OK', player=pnum)
        except Exception as e:
            return dict(status='ERROR', data=str(e))

    def get_location(self, params=[]):
        pnum = params[0]
        try:
            return dict(status='OK', location=self.players[pnum])
        except Exception as e:
            return dict(status='ERROR', data=str(e))

    def join(self, params=[]):
        try:
            pnum = params[0]
            x = params[1]
            y = params[2]
            self.players[pnum] = f"{x},{y}"
            self.players.sync()

            players = []
            for key in self.players:
                player = {
                    'id_player': key,
                    'location': self.players[key]
                }
                players.append(player)
            return dict(status='OK', players=players)
        except Exception as e:
            return dict(status='ERROR', data=str(e))

    def refresh(self, params=[]):
        try:
            players = []
            for key in self.players:
                player = {
                    'id_player': key,
                    'location': self.players[key]
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
    p.set_location(['1', 100, 100])
    print(p.get_location('1'))
    p.set_location(['2', 120, 100])
    print(p.get_location('2'))

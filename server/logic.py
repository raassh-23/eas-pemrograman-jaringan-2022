import os
import json
import base64
from glob import glob
import shelve

class PlayerServerInterface:
    def __init__(self):
        self.players = shelve.open('g.db', writeback=True)

    def join(self, params=[]):
        try:
            player_name = params[0]

            if player_name in self.players:
                return dict(status='ERROR', data='player already exists')

            x = params[1]
            y = params[2]
            angle = params[3]
            self.players[player_name] = f"{x},{y},{angle}"
            self.players.sync()

            players = []
            for key in self.players:
                if key == player_name:
                    continue
                
                players.append(key)
            return dict(status='OK', players=players)
        except Exception as e:
            return dict(status='ERROR', data=str(e))

    def leave(self, params=[]):
        try:
            player_name = params[0]
            del self.players[player_name]
            self.players.sync()
            return dict(status='OK')
        except Exception as e:
            return dict(status='ERROR', data=str(e))

    def refresh_players(self, params=[]):
        try:
            players = []
            for key in self.players:
                players.append(key)
            return dict(status='OK', players=players)
        except Exception as e:
            return dict(status='ERROR', data=str(e))

    def set_position(self, params=[]):
        try:
            player_name = params[0]
            x = params[1]
            y = params[2]
            player = self.players[player_name].split(',')
            self.players[player_name] = f"{x},{y},{player[2]}"
            self.players.sync()
            return dict(status='OK')
        except Exception as e:
            return dict(status='ERROR', data=str(e))

    def set_angle(self, params=[]):
        try:
            player_name = params[0]
            angle = params[1]
            player = self.players[player_name].split(',')
            self.players[player_name] = f"{player[0]},{player[1]},{angle}"
            self.players.sync()
            return dict(status='OK')
        except Exception as e:
            return dict(status='ERROR', data=str(e))

    def get_position_angle(self, params=[]):
        try:
            player_name = params[0]
            player = self.players[player_name].split(',')
            player_data = {
                'x': player[0], 
                'y': player[1], 
                'angle': player[2]
            }
            return dict(status='OK', player=player_data)
        except Exception as e:
            return dict(status='ERROR', data=str(e))

if __name__ == '__main__':
    p = PlayerServerInterface()
    print(p.join(['name', '0', '0', '0']))
    print(p.refresh_players())
    print(p.get_position_angle(['name']))
    print(p.set_position(['name', '10', '-10']))
    print(p.get_position_angle(['name']))
    print(p.set_angle(['name', '90']))
    print(p.get_position_angle(['name']))
    print(p.leave(['name']))
    print(p.refresh_players())


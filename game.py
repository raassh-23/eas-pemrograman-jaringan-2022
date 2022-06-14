from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.app import App
from kivy.graphics import Color, Rectangle, Line
from functools import partial
from kivy.clock import  Clock

import socket
import logging
import json
import random

class ClientInterface:
    def __init__(self):
        self.server_address=('localhost',6667)

    def send_command(self,command_str=""):
        global server_address
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(self.server_address)
        # logging.warning(f"connecting to {self.server_address}")
        try:
            # logging.warning(f"sending message ")
            sock.sendall(command_str.encode())
            # Look for the response, waiting until socket is done (no more data)
            data_received="" #empty string
            while True:
                #socket does not receive all data at once, data comes in part, need to be concatenated at the end of process
                data = sock.recv(16)
                if data:
                    #data is not empty, concat with previous content
                    data_received += data.decode()
                    if "\r\n\r\n" in data_received:
                        break
                else:
                    # no more data, stop the process by break
                    break
            # at this point, data_received (string) will contain all data coming from the socket
            # to be able to use the data_received as a dict, need to load it using json.loads()
            hasil = json.loads(data_received)
            # logging.warning("data received from server:")
            return hasil
        except:
            # logging.warning("error during data receiving")
            return False

    def set_location(self, id_player, x=100,y=100):
        logging.warning(f"set_location {id_player} {x} {y}")
        command_str=f"set_location {id_player} {x} {y}"
        hasil = self.send_command(command_str)
        if (hasil['status']=='OK'):
            return True
        else:
            print('error: ' + hasil['data'])
            return False

    def get_location(self, id_player):
        logging.warning(f"get_location {id_player}")
        command_str=f"get_location {id_player}"
        hasil = self.send_command(command_str)
        if (hasil['status']=='OK'):
            lokasi = hasil['location'].split(',')
            return (int(lokasi[0]),int(lokasi[1]))
        else:
            print('error: ' + hasil['data'])
            return None

    def join(self, id_player, x=100,y=100):
        logging.warning(f"join {id_player} {x} {y}")
        command_str=f"join {id_player} {x} {y}"
        hasil = self.send_command(command_str)
        print(hasil)
        if (hasil['status']=='OK'):
            return hasil['players']
        else:
            print('error: ' + hasil['data'])
            return None

    def refresh(self):
        logging.warning("refresh")
        command_str=f"refresh"
        hasil = self.send_command(command_str)
        if (hasil['status']=='OK'):
            return hasil['players']
        else:
            print('error: ' + hasil['data'])
            return None

    def leave(self, id_player):
        logging.warning(f"leave {id_player}")
        command_str=f"leave {id_player}"
        hasil = self.send_command(command_str)
        if (hasil['status']=='OK'):
            return True
        else:
            print('error: ' + hasil['data'])
            return False

client_interface = ClientInterface()

class Player:
    def __init__(self,idplayer='1',r=1,g=0,b=0, draw_button=False):
        self.current_x = 100
        self.current_y = 100
        self.warna_r = r
        self.warna_g = g
        self.warna_b = b
        self.idplayer = idplayer
        self.widget = Widget()
        self.buttons = None
        self.left = False
        
        if draw_button:
            self.inisialiasi()
        #self.draw(self.widget,self.warna_r,self.warna_g,self.warna_b)
    def get_idplayer(self):
        return self.idplayer
    def set_xy(self,x=100,y=100):
        self.current_x = x
        self.current_y = y
        #self.draw(self.widget, self.warna_r, self.warna_g, self.warna_b)

    def get_widget(self):
        return self.widget
    def get_buttons(self):
        return self.buttons

    def draw(self):
        cur_location = client_interface.get_location(self.idplayer)

        if cur_location is None:
            self.left = True
            return

        self.current_x, self.current_y = cur_location

        wid = self.widget
        r = self.warna_r
        g = self.warna_g
        b = self.warna_b

        with wid.canvas:
            Color(r,g,b)
            Line(rectangle=(self.current_x,self.current_y, 200, 200))

    def move(self,wid, arah,*kwargs):
        #self.draw(wid,0,0,0)
        if (arah=='right'):
            self.current_x = self.current_x + 5
        if (arah=='left'):
            self.current_x = self.current_x - 5
        if (arah=='up'):
            self.current_y = self.current_y + 5
        if (arah=='down'):
            self.current_y = self.current_y - 5
        client_interface.set_location(self.idplayer, self.current_x,self.current_y)
        #self.draw(wid,self.warna_r,self.warna_g,self.warna_b)

    def inisialiasi(self):
        wid = self.widget
        btn_left = Button(text='left',on_press=partial(self.move, wid, 'left'))
        btn_up = Button(text='up',on_press=partial(self.move, wid, 'up'))
        btn_down = Button(text='down',on_press=partial(self.move, wid, 'down'))
        btn_right = Button(text='right',on_press=partial(self.move, wid, 'right'))

        self.buttons = BoxLayout(size_hint=(1, None), height=50)
        self.buttons.add_widget(btn_left)
        self.buttons.add_widget(btn_up)
        self.buttons.add_widget(btn_down)
        self.buttons.add_widget(btn_right)

class MyApp(App):
    players = []
    player_id = 0

    def refresh(self,callback):
        players_server = client_interface.refresh()
        if players_server:
            for i in players_server:
                if any(i['id_player'] == j.idplayer for j in self.players):
                    continue

                p = Player(i['id_player'],0,1,1)
                lokasi = i['location'].split(',')
                p.set_xy(lokasi[0],lokasi[1])
                widget = p.get_widget()
                self.players.append(p)
                self.root.add_widget(widget)

        for i in self.players:
            if i.left:
                self.root.remove_widget(i.get_widget())
                self.players.remove(i)
                continue

            i.get_widget().canvas.clear()
            i.draw()

    def build(self):
        self.player_id = random.randint(0,1024)
        p1 = Player(f'{self.player_id}',1,0,0,True)
        p1.set_xy(100,100)
        widget1 = p1.get_widget()
        buttons1 = p1.get_buttons()
        self.players.append(p1)

        btn_exit = Button(text='exit',on_press=partial(self.stop))
        nav_button = BoxLayout(size_hint=(1, None), height=50)
        nav_button.add_widget(btn_exit)

        root = BoxLayout(orientation='horizontal')
        root.add_widget(widget1)
        root.add_widget(buttons1)
        root.add_widget(nav_button)

        joined = client_interface.join(p1.idplayer, 100, 100)
        print(joined)
        if joined:
            for i in joined:
                if any(i['id_player'] == j.idplayer for j in self.players):
                    continue

                p = Player(i['id_player'],0,1,1)
                lokasi = i['location'].split(',')
                p.set_xy(lokasi[0],lokasi[1])
                widget = p.get_widget()
                self.players.append(p)
                root.add_widget(widget)

        Clock.schedule_interval(self.refresh,1/30)

        return root

    def on_stop(self):
        client_interface.leave(self.player_id)
        return super().on_stop()

if __name__ == '__main__':
    MyApp().run()
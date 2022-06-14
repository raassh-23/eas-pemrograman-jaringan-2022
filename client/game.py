import math
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.app import App
from kivy.graphics import Triangle, Color, Rectangle
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.core.text import Label as CoreLabel
from kivy.uix.textinput import TextInput

import socket
import logging
import json
import random

from matplotlib.pyplot import text

class ClientInterface:
    def __init__(self):
        # self.server_address=('18.141.176.62',6667)
        self.server_address = ('localhost', 6667)

    def send_command(self, command_str=""):
        global server_address
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(self.server_address)
        # logging.warning(f"connecting to {self.server_address}")
        try:
            # logging.warning(f"sending message {command_str}")
            sock.sendall(command_str.encode())
            # Look for the response, waiting until socket is done (no more data)
            data_received = ""  # empty string
            while True:
                # socket does not receive all data at once, data comes in part, need to be concatenated at the end of process
                data = sock.recv(16)
                if data:
                    # data is not empty, concat with previous content
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

    def set_position(self, name, x, y):
        command_str = f"set_position {name} {x} {y}"
        # logging.warning(command_str)
        hasil = self.send_command(command_str)
        if (self._is_success(hasil)):
            return True
        else:
            return False

    def set_angle(self, name, angle):
        command_str = f"set_angle {name} {angle}"
        # logging.warning(command_str)
        hasil = self.send_command(command_str)
        if (self._is_success(hasil)):
            return True
        else:
            return False

    def join(self, name, x, y, angle):
        command_str = f"join {name} {x} {y} {angle}"
        # logging.warning(command_str)
        hasil = self.send_command(command_str)
        if (self._is_success(hasil)):
            return hasil['players']
        else:
            return None

    def refresh(self):
        command_str = f"refresh"
        # logging.warning(command_str)
        hasil = self.send_command(command_str)
        if (self._is_success(hasil)):
            return hasil['players']
        else:
            return None

    def leave(self, name):
        command_str = f"leave {name}"
        # logging.warning(command_str)
        hasil = self.send_command(command_str)
        if (self._is_success(hasil)):
            return True
        else:
            return False

    def _is_success(self, hasil):
        if (hasil['status'] == 'OK'):
            return True
        else:
            logging.warning(f"error: {hasil['data']}")
            return False

client_interface = ClientInterface()

class Player:
    def __init__(self, name='1', r=1, g=0, b=0, is_controllable=False):
        self.current_x = 100
        self.current_y = 100
        self.warna_r = r
        self.warna_g = g
        self.warna_b = b
        self.name = name
        self.widget = Widget()
        self._keyboard = None
        self.angle = 0

        if is_controllable:
            self.inisialiasi()

    def set_player_location(self, x, y, angle):
        self.current_x = x
        self.current_y = y
        self.angle = angle

    def draw(self):
        wid = self.widget
        r = self.warna_r
        g = self.warna_g
        b = self.warna_b

        size = 60
        sqrt3 = 1.73

        points_x = [
            self.current_x,
            self.current_x - size / 3,
            self.current_x + size / 3
        ]
        points_y = [
            self.current_y + size * sqrt3 / 3,
            self.current_y - size * sqrt3 / 6,
            self.current_y - size * sqrt3 / 6
        ]

        for i in range(3):
            xi = points_x[i]
            yi = points_y[i]
            theta = math.radians(self.angle)

            points_x[i] = self.current_x + (xi - self.current_x) * math.cos(theta) - (yi - self.current_y) * math.sin(theta)
            points_y[i] = self.current_y + (xi - self.current_x) * math.sin(theta) + (yi - self.current_y) * math.cos(theta)

        label = CoreLabel(text=self.name, font_size=20)
        label.refresh()
        texture = label.texture
        texture_size = list(texture.size)

        wid.canvas.clear()

        with wid.canvas:
            Color(r, g, b)
            Triangle(points=[
                points_x[0], points_y[0],
                points_x[1], points_y[1],
                points_x[2], points_y[2]
            ])
            Color(1, 1, 1)
            Rectangle(pos=(self.current_x - texture_size[0] / 2, self.current_y - texture_size[1] / 2 + size/2), size=texture_size, texture=texture)

    def move(self, arah, *kwargs):
        if (arah == 'right') or (arah == 'd'):
            self.current_x = self.current_x + 5
        elif (arah == 'left') or (arah == 'a'):
            self.current_x = self.current_x - 5
        elif (arah == 'up') or (arah == 'w'):
            self.current_y = self.current_y + 5
        elif (arah == 'down') or (arah == 's'):
            self.current_y = self.current_y - 5
        else:
            return

        client_interface.set_position(self.name, self.current_x, self.current_y)

    def inisialiasi(self):
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self.widget)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
        Window.bind(mouse_pos=self._on_mouse_pos)

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        self.move(keycode[1])

    def _on_mouse_pos(self, window, pos):
        dx = pos[0] - self.current_x
        dy = pos[1] - self.current_y
        new_angle = math.degrees(math.atan2(dy, dx)) - 90
        
        if new_angle != self.angle:
            self.angle = new_angle
            client_interface.set_angle(self.name, self.angle)

class MyApp(App):
    players = []
    player_name = 0

    def refresh(self, callback):
        players_server = client_interface.refresh()
        if players_server:
            for player in players_server:
                existing_player = next((j for j in self.players if j.name == player['name']), None)

                if existing_player:
                    existing_player.set_player_location(float(player['x']), float(player['y']), float(player['angle']))
                    continue

                new_player = Player(player['name'], 0, 1, 1)
                new_player.set_player_location(float(player['x']), float(player['y']), float(player['angle']))
                self.players.append(new_player)
                self.root.add_widget(new_player.widget)

            for player in self.players:
                if not any(j['name'] == player.name for j in players_server):
                    self.root.remove_widget(player.widget)
                    self.players.remove(player)

                player.draw()

    def build(self):
        root = BoxLayout(orientation='horizontal')
        text_input = TextInput(text='', hint_text='masukkan nama(tanpa spasi) lalu enter', multiline=False, size_hint=(1, None), height=30)
        text_input.bind(on_text_validate=self._on_input_enter)
        root.add_widget(text_input)
        
        return root

    def _on_input_enter(self, text_input):  
        if ' ' in text_input.text:
            text_input.text = ''
            text_input.hint_text = 'Coba nama lain'
            return

        self.player_name = text_input.text
        x = Window.width / 2
        y = Window.height / 2
        p1 = Player(f'{self.player_name}', 1, 0, 0, True)
        p1.set_player_location(x, y, 0)
        
        joined = client_interface.join(p1.name, p1.current_x, p1.current_y, p1.current_y)
        if joined:
            self.players.append(p1)
            self.root.add_widget(p1.widget)
            self.root.remove_widget(text_input)

            for player in joined:
                if any(player['name'] == j.name for j in self.players):
                    continue
                
                p = Player(player['name'], 0, 1, 1)
                p.set_player_location(float(player['x']), float(player['y']), float(player['angle']))
                self.players.append(p)
                self.root.add_widget(p.widget)
        else:
            text_input.text = ''
            text_input.hint_text = 'Coba nama lain'
            return

        Clock.schedule_interval(self.refresh, 1/30)

    def on_stop(self):
        client_interface.leave(self.player_name)
        return super().on_stop()

if __name__ == '__main__':
    MyApp().run()

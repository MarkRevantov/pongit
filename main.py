from kivy.app import App
from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.cache import Cache

from kivy.config import Config

from random import randint

# Musics
game_musics = [SoundLoader.load('Music/Metre-02-Digital_Savanna.ogg'), SoundLoader.load('Music/Metre-03-Sand_Dweller.ogg'), SoundLoader.load('Music/Soularflair-12-Dark-Minimal-PumpingDigitalSoul.ogg'), SoundLoader.load('Music/LoyaltyFreakMusic-04-CantStopMyFeet.ogg')]
for track in game_musics:
    track.volume = 0.4

class MyScreen(Screen):
    def __init__(self, **kvarg):
        super().__init__(**kvarg)
        self.btn_sound = SoundLoader.load('Sound/pong_hit_low.ogg')
    def btn_sound_play(self):
        self.btn_sound.play()

class PongBoard(Widget):
    score = NumericProperty(0)
    sound_hit_high  = SoundLoader.load('Sound/pong_hit_high.ogg')

    def bounce_ball(self, ball, root_width):
        if self.collide_widget(ball):
            if (self.x < root_width/3 and ball.velocity_x < 0) or (self.x > 2*root_width/3 and ball.velocity_x > 0):
                self.sound_hit_high.play()
                vx, vy = ball.velocity
                offset = (ball.center_y - self.center_y) / (self.height / 2)
                bounced = Vector(-1 * vx, vy)
                vel = bounced * Cache.get('settings', 'velocity multiple')
    
                ball.velocity = vel.x, vel.y + offset


class PongBall(Widget):
    #Velocity of Ball    
    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)

    velocity = ReferenceListProperty(velocity_x, velocity_y)

    def move(self):
        self.pos = Vector(*self.velocity) + self.pos

class PlayingScreen(MyScreen):
    ball = ObjectProperty(None)
    player1 = ObjectProperty(None)
    player2 = ObjectProperty(None)

    def serve_ball(self):
        self.ball.center = self.center
        start_vel = Cache.get('settings', 'start ball velocity')
        self.ball.velocity = Vector(start_vel*(1 - 2*randint(0,1)), start_vel*randint(-1,1))
    def on_pre_enter(self):
        self.sound_hit_low  = SoundLoader.load('Sound/pong_hit_low.ogg')
        self.sound_goal = SoundLoader.load('Sound/goal.ogg')

        
        # ReCacheing settings
        players_count = Cache.get('settings', 'players')
        if players_count == None:
            players_count = 1
        self.players_count = players_count
        #
        difficult = Cache.get('settings', 'difficult')
        if difficult == None:
            difficult = 1
        self.difficult = difficult
        #
        start_ball_velocity = Cache.get('settings', 'start ball velocity')
        if start_ball_velocity == None:
            start_ball_velocity = 5
        try:
            start_ball_velocity = float(start_ball_velocity)
        except Exception:
            start_ball_velocity = 5
        #
        velocity_multiple = Cache.get('settings', 'velocity multiple')
        if velocity_multiple == None:
            velocity_multiple = 1.05
        try:
            velocity_multiple = float(velocity_multiple)
        except Exception:
            velocity_multiple = 1.05
        
        Cache.append('settings', 'players', players_count)
        Cache.append('settings', 'difficult', difficult)
        Cache.append('settings', 'start ball velocity', start_ball_velocity)
        Cache.append('settings', 'velocity multiple', velocity_multiple)
    def on_enter(self):
        self.serve_ball()
        self.event_playing = Clock.schedule_interval(self.update, 1.0/60)
    def update(self, dt):
        self.ball.move()

        self.player1.bounce_ball(self.ball, self.width)
        self.player2.bounce_ball(self.ball, self.width)

        if self.players_count == 1:
            if self.difficult == 1:
                self.player2.center_y += 0.05*(self.ball.center_y - self.player2.center_y)
            if self.difficult == 2:
                self.player2.center_y += 0.10*(self.ball.center_y - self.player2.center_y)
            if self.difficult == 3:
                self.player2.center_y += 0.9*(self.ball.center_y - self.player2.center_y)
    
        if(self.ball.y < 0) or (self.ball.top > self.height):
            self.sound_hit_low.play()
            self.ball.velocity_y *= -1
        #if(self.ball.x < 0) or (self.ball.right > self.width):
        #    self.ball.velocity_x *= -1

        # Уход за левую половину экрана
        if self.ball.x < self.x:
            self.sound_goal.play()
            self.player2.score += 1
            self.serve_ball()
            print("P2: " + str(self.player2.score))

        # Уход за правую половину экрана
        if self.ball.x > self.width:
            self.sound_goal.play()
            self.player1.score += 1
            self.serve_ball()
            print("P1: " + str(self.player1.score))
    def on_touch_move(self, touch):
        if touch.x < self.width/3:
            self.player1.center_y = touch.y
            self.player1.center_x = touch.x
        
        if touch.x > 2*self.width/3 and self.players_count == 2:
            self.player2.center_y = touch.y
            self.player2.center_x = touch.x
    def on_pre_leave(self):
        self.event_playing.cancel()
        self.player1.score = 0
        self.player2.score = 0
        self.player2.x = self.width-30
class MainMenuScreen(MyScreen):
    pass
class SettingsScreen(MyScreen):
    def save_setting(self, key, obj):
        Cache.append('settings', key, obj, None)
class CreditsScreen(MyScreen):
    pass
class Pong2App(App):
    def __init__(self):
        super().__init__()

        # Screens
        self.sm = ScreenManager()


    def on_start(self):
        music = game_musics[randint(0,len(game_musics)-1)]
        music.loop = True
        music.play()
    def build(self):
        Cache.register('settings', 10, None)

        self.sm.add_widget(MainMenuScreen(name='main_menu'))
        self.sm.add_widget(SettingsScreen(name='settings'))
        self.sm.add_widget(CreditsScreen(name='credits'))
        self.sm.add_widget(PlayingScreen(name='playing'))
        return self.sm


if __name__ == "__main__":
    Config.set('graphics', "width", 1280)
    Config.set('graphics', "height", 720)
    Config.set('kivy', "window_icon", "icon.png")
    Pong2App().run()

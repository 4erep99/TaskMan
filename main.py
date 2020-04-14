from kivy.app import App
from kivy.properties import StringProperty
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.anchorlayout import AnchorLayout

import sqlite3 #База данных
import hashlib #Хеширование пароля

from connected import Connected
from register import Register

class Login(Screen):
    def do_login(self, loginText, passwordText):

        app = App.get_running_app()
        app.username = loginText
        app.password = passwordText

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor_row = conn.cursor()

        cursor.execute("SELECT password FROM users WHERE login=?", (loginText,))
        rows = cursor_row.execute("SELECT COUNT(*) FROM users WHERE login=?", (loginText,)).fetchone()[0]

        if(rows > 0):
            hashed_password = "".join(cursor.fetchone())
            pass_without_salt, salt = hashed_password.split(':')
            salt = "".join(salt)
            pass_without_salt = "".join(pass_without_salt)

            def hash_password(password, salt):
                return hashlib.sha256(salt.encode() + password.encode()).hexdigest()

            def checkPassword(password):
                if hash_password(password, salt) == pass_without_salt:
                    return True


            if((rows > 0) and checkPassword(passwordText)):
                app.on_change_screen(self.manager.current, 'connected', 'left')
            else:
                app.on_error("Ошибка: Неверный логин или пароль", self.manager.current)

    def resetForm(self):
        self.ids['login'].text = ""
        self.ids['password'].text = ""

    def do_register(self):
        app = App.get_running_app()
        app.on_change_screen(self.manager.current, 'register', 'left')


class ErrorMessageWidget(AnchorLayout):
    pass
class VoiceMessage(AnchorLayout):
    pass

class LoginApp(App):
    username = StringProperty(None)
    password = StringProperty(None)
    ErrorMessage = u""
    VoiceMessageText = u""

    def on_change_screen(self, screen, target_screen, transition):
        self.root.transition = SlideTransition(direction=transition)
        self.root.current = target_screen
        for child in self.root.get_screen(screen).children[:]:
            if child.id == 'error':
                self.root.get_screen(screen).remove_widget(child)

    def on_error(self, error, screen):
        self.ErrorMessage = error
        self.root.get_screen(screen).add_widget(ErrorMessageWidget(id='error'))

    def on_message(self, message, screen):
        self.VoiceMessageText = message
        self.root.get_screen(screen).add_widget(VoiceMessage())

    def build(self):
        manager = ScreenManager()

        manager.add_widget(Login(name='login'))
        manager.add_widget(Connected(name='connected'))
        manager.add_widget(Register(name='register'))

        return manager

if __name__ == '__main__':
    LoginApp().run()
from kivy.app import App
from kivy.uix.screenmanager import Screen, SlideTransition
import sqlite3 #База данных
import hashlib #Хеширование пароля
import uuid #Генерация соли
from re import * #Проверка на email

class Register(Screen):
    def disconnect(self):
        app = App.get_running_app()
        app.on_change_screen(self.manager.current, 'login', 'right')
        self.manager.get_screen('login').resetForm()

    def do_register(self, loginText, passwordText, email, password2):
        app = App.get_running_app()
        if(len(loginText) < 5):
            #print('Имя пользователя должно содержать больше 4 символов')
            app.on_error("Ошибка: Имя пользователя должно содержать больше 4 символов", self.manager.current)
        else:
            if(len(passwordText) < 6):
                #print('Пароль должен содержать больше 5 символов')
                app.on_error("Ошибка: Пароль должен содержать больше 5 символов", self.manager.current)
            else:
                if(passwordText != password2):
                    #print('Пароли не совпадают!')
                    app.on_error("Ошибка: Пароли не совпадают", self.manager.current)
                else:
                    pattern = compile('(^|\s)[-a-z0-9_.]+@([-a-z0-9]+\.)+[a-z]{2,6}(\s|$)')
                    email_valid = pattern.match(email)
                    if not email_valid:
                        #print('Email не поддерживается, введите другой')
                        app.on_error("Ошибка: Email не поддерживается, введите другой", self.manager.current)
                    else:
                        conn = sqlite3.connect('users.db')
                        cursor = conn.cursor()

                        rows = cursor.execute("SELECT COUNT(*) FROM users WHERE login=?", (loginText,)).fetchone()[0]
                        if(rows == 0):

                            def hash_password(password):
                                salt = uuid.uuid4().hex
                                return hashlib.sha256(salt.encode() + password.encode()).hexdigest() + ':' + salt

                            try:
                                cursor.execute("INSERT INTO users VALUES (NULL, ?, ?, ?)", (loginText, hash_password(passwordText), email))
                            except sqlite3.DatabaseError as error:
                                #print ("Ошибка: ", error)
                                app.on_error("Ошибка: " + error, self.manager.current)
                            else:
                                conn.commit()
                                conn.close()
                                app = App.get_running_app()
                                app.on_change_screen(self.manager.current, 'login', 'right')
                                self.manager.get_screen('login').resetForm()
                        else:
                            #print('Имя пользователя уже используется')
                            app.on_error("Ошибка: Имя пользователя уже используется", self.manager.current)
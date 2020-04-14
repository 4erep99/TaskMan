from kivy.app import App
from kivy.uix.screenmanager import Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout

import sqlite3 #База данных
import speech_recognition as sr #Голосовой ввод
import os
from gtts import gTTS
import playsound

class Connected(Screen):
    is_speaking = False
    def talk(self, file_name):
        #if(os.name == 'nt'):
        #    import win32com.client
        #    speaker = win32com.client.Dispatch("SAPI.SpVoice")
        #    speaker.Speak(speech)
        #else:
        #    os.system('say "' + speech + '"')
        playsound.playsound(file_name, True)

    def get_voice_text(self):
        self.is_speaking = True
        r = sr.Recognizer()
        self.talk("1.mp3")
        with sr.Microphone() as source:
            r.pause_threshold = 1
            #r.adjust_for_ambient_noise(source, duration=1)
            audio = r.listen(source)
        try:
            command = r.recognize_google(audio, language="ru-RU").lower()
            #print('You said: ' + command + '\n')
            self.talk("2.mp3")
            self.add_task(command)
        except sr.UnknownValueError:
            #print('....')
            self.talk("3.mp3")

        self.is_speaking = False

    def get_tasks_from_db(self):
        app = App.get_running_app()
        self.ids.task.clear_widgets()
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tasks WHERE task_screen=? AND user_login =? ORDER BY id DESC", (self.manager.current, app.username))
        rows = cursor.fetchall()
        for i in rows:
            app.TaskText = str(i[1])
            self.ids.task.add_widget(TaskLabel(id = str(i[0])))
        conn.close()

    def add_task(self, task_text):
        app = App.get_running_app()
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()

        if(len(task_text) > 0):
            if(len(task_text) < 56):
                try:
                    cursor.execute("INSERT INTO tasks VALUES (NULL, ?, ?, ?)", (task_text, self.manager.current, app.username))
                except sqlite3.DatabaseError as error:
                    #print("Ошибка: ", error)
                    app.on_error("Ошибка: " + error, self.manager.current)
                else:
                    conn.commit()
                    conn.close()
            else:
                app.on_error("Ошибка: Текст заметки не может быть длиннее 55 символов", self.manager.current)
        else:
            app.on_error("Ошибка: Текст заметки не задан", self.manager.current)
        self.get_tasks_from_db()

    def disconnect(self):
        app = App.get_running_app()
        app.on_change_screen(self.manager.current, 'login', 'right')
        self.manager.get_screen('login').resetForm()

class TaskLabel(BoxLayout):
    def remove_task(self, id):
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM tasks WHERE id=?", (id,))
        except sqlite3.DatabaseError as error:
                #print("Ошибка: ", error)
                app.on_error("Ошибка: " + error, self.manager.current)
        else:
            conn.commit()
            conn.close()
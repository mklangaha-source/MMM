from kivy.app import App
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivy.graphics import Color, RoundedRectangle
import socket, threading, os, json

Window.softinput_mode = "below_target"
Window.clearcolor = (0.95, 0.95, 0.97, 1) # سادہ، صاف کلر

PASS_FILE = "my_secret_pass.txt"
SETTING_FILE = "settings.json"
DEFAULT_CODE = "Mujtaba Khan 786"

def load_settings():
    if os.path.exists(SETTING_FILE):
        try:
            with open(SETTING_FILE, 'r') as f: return json.load(f)
        except: pass
    return {"ip": "", "code": DEFAULT_CODE}

def save_settings(ip, code):
    with open(SETTING_FILE, 'w') as f: json.dump({"ip": ip, "code": code}, f)

# --- Screen 1: Login - AB BILKUL AAM APPS JAISA BADA ---
class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        main_box = BoxLayout(orientation='vertical', padding=[25, 30], spacing=18)

        main_box.add_widget(Label(size_hint=(1, 0.15)))
        main_box.add_widget(Label(text='Welcome Back', font_size=30, bold=True, color=(0.1, 0.1, 0.1, 1), size_hint=(1, 0.12)))
        main_box.add_widget(Label(text='Login to continue', font_size=14, color=(0.5, 0.5, 0.5, 1), size_hint=(1, 0.05)))

        main_box.add_widget(Label(size_hint=(1, 0.05)))

        # 1. NAME - Aam apps jitna bada
        main_box.add_widget(Label(text='Name', font_size=15, bold=True, color=(0.2,0.2,0.2,1), size_hint=(1, None), height=25, halign='left'))
        self.name_input = TextInput(
            hint_text='Enter your name',
            size_hint=(1, None), height=62, # <-- BADA KAR DIYA
            multiline=False,
            background_normal='', background_active='',
            background_color=(1,1,1,1),
            foreground_color=(0,0,0,1),
            font_size=17,
            padding=[18, 18]
        )
        main_box.add_widget(self.name_input)

        # 2. PASSWORD - Aam apps jitna bada
        main_box.add_widget(Label(text='Password', font_size=15, bold=True, color=(0.2,0.2,0.2,1), size_hint=(1, None), height=25, halign='left'))
        self.pass_input = TextInput(
            hint_text='Enter your password',
            size_hint=(1, None), height=62, # <-- BADA KAR DIYA
            multiline=False,
            password=True,
            background_normal='', background_active='',
            background_color=(1,1,1,1),
            foreground_color=(0,0,0,1),
            font_size=17,
            padding=[18, 18]
        )
        main_box.add_widget(self.pass_input)

        self.msg = Label(text='', color=(1,0,0,1), size_hint=(1, None), height=30)
        main_box.add_widget(self.msg)

        btn = Button(
            text='LOGIN',
            size_hint=(1, None), height=62, # <-- BADA
            background_normal='', background_color=(0.1, 0.5, 0.95, 1),
            color=(1,1,1,1), bold=True, font_size=17
        )
        btn.bind(on_press=self.enter_app)
        main_box.add_widget(btn)

        main_box.add_widget(Label(size_hint=(1, 0.35)))
        self.add_widget(main_box)

    def enter_app(self, instance):
        name = self.name_input.text.strip(); pwd = self.pass_input.text.strip()
        if not name or not pwd:
            self.msg.text = "Name aur Password zaroori hai"; return
        if not os.path.exists(PASS_FILE):
            with open(PASS_FILE, 'w') as f: f.write(pwd)
        else:
            with open(PASS_FILE, 'r') as f: saved = f.read().strip()
            if pwd != saved:
                self.msg.text = "Ghalat Password!"; return
        self.manager.get_screen('chat').my_name_text = name
        self.manager.current = 'chat'

# --- Screen 2: Chat - 3 LINES + BADA MESSAGE BOX + CENTER ERROR ---
class ChatScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.conn = None; self.my_name_text = "User"
        root = FloatLayout()
        main = BoxLayout(orientation='vertical', padding=15, spacing=12)

        # Top Bar - 3 Dots ko 3 Lines me convert
        top_bar = BoxLayout(size_hint=(1, None), height=60)
        top_bar.add_widget(Label(text='Messages', font_size=20, bold=True, color=(0.1,0.1,0.1,1), halign='left'))
        
        # YAHAN FIX: 3 Dots ki jagah 3 Lines (Hamburger)
        menu_btn = Button(
            text='☰', # <-- 3 LINES, jaise aam apps me hota hai
            font_size=32, # Clear nazar aayega
            bold=True,
            size_hint=(None, 1), width=60,
            background_normal='', background_color=(0,0,0,0),
            color=(0.1, 0.1, 0.1, 1)
        )
        menu_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'settings'))
        top_bar.add_widget(menu_btn)
        main.add_widget(top_bar)

        # Center me error dikhane ke liye Box - SCREEN KE CENTER ME AAYEGA
        center_error_box = FloatLayout(size_hint=(1, 0.7))
        # Ye label center me aayega jab IP set nahi hoga
        self.center_error = Label(
            text='',
            font_size=18,
            bold=True,
            color=(0.8, 0.1, 0.1, 1),
            size_hint=(0.8, 0.3),
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            halign='center',
            valign='middle'
        )
        self.center_error.bind(size=self.center_error.setter('text_size'))
        
        scroll = ScrollView(size_hint=(1, 1))
        self.history = Label(text='', size_hint_y=None, markup=True, color=(0.2,0.2,0.2,1), font_size=16, halign='left', valign='top')
        self.history.bind(texture_size=self.update_size)
        scroll.add_widget(self.history)
        center_error_box.add_widget(scroll)
        center_error_box.add_widget(self.center_error)
        main.add_widget(center_error_box)

        # Message Box - AB BADA KAR DIYA
        msg_box = BoxLayout(size_hint=(1, None), height=70, spacing=12) # 60 se 70 kiya
        self.msg_input = TextInput(
            hint_text='Type a message...',
            size_hint=(0.75, 1),
            background_normal='', background_active='',
            background_color=(1,1,1,1),
            foreground_color=(0,0,0,1),
            font_size=18, # <-- BADA FONT
            multiline=False,
            padding=[20, 20]
        )
        send_btn = Button(text='SEND', size_hint=(0.25, 1), background_normal='', background_color=(0.1, 0.5, 0.95, 1), color=(1,1,1,1), bold=True, font_size=15)
        send_btn.bind(on_press=self.send_message)
        msg_box.add_widget(self.msg_input)
        msg_box.add_widget(send_btn)
        main.add_widget(msg_box)

        root.add_widget(main)
        self.add_widget(root)

    def update_size(self, instance, size):
        instance.text_size = (Window.width - 40, None)
        instance.size = instance.texture_size

    def show_center_error(self, text):
        def update(dt):
            self.center_error.text = text
            self.history.text = "" # history khali taake center wala saaf nazar aaye
        Clock.schedule_once(update)
        # 3 second baad hata do
        Clock.schedule_once(lambda dt: setattr(self.center_error, 'text', ''), 4)

    def add_chat(self, text):
        def update(dt):
            self.center_error.text = "" # error hatao
            self.history.text += f"\n{text}"
        Clock.schedule_once(update)

    def connect_if_needed(self):
        s = load_settings(); ip = s.get('ip','')
        if not ip:
            self.show_center_error("Please Set IP First\n\nGo to ☰ Menu > Set IP")
            return False
        if self.conn: return True
        threading.Thread(target=self.client_thread, args=(s.get('ip',''), s.get('code', DEFAULT_CODE)), daemon=True).start()
        return False

    def client_thread(self, ip, room):
        try:
            clean_ip = ip.replace("https://","").replace("http://","").split("/")[0].split(":")[0]
            self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.conn.connect((clean_ip, 5000))
            self.conn.send(f"ROOM:{room}".encode('utf-8'))
            self.add_chat(f"--- Connected: {room} ---")
            while True:
                data = self.conn.recv(2048).decode('utf-8')
                if data:
                    if data.startswith("JOINED:"): continue
                    self.add_chat(data)
        except Exception as e:
            self.add_chat(f"Error: {e}"); self.conn = None

    def send_message(self, instance):
        if not self.connect_if_needed(): return
        if not self.msg_input.text.strip(): return
        msg = f"{self.my_name_text}: {self.msg_input.text.strip()}"
        try:
            self.conn.send(msg.encode('utf-8'))
            self.add_chat(f"[b]You:[/b] {self.msg_input.text.strip()}")
            self.msg_input.text = ""
        except:
            self.add_chat("Send failed..."); self.conn = None

class SettingsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        box = BoxLayout(orientation='vertical', padding=25, spacing=15)
        box.add_widget(Label(text='Settings', font_size=22, bold=True, color=(0.1,0.1,0.1,1), size_hint=(1,0.15)))
        box.add_widget(Label(text='IP Address', font_size=14, bold=True, color=(0.3,0.3,0.3,1), size_hint=(1, None), height=25))
        self.ip_input = TextInput(hint_text='Enter Server IP', password=True, size_hint=(1, None), height=58, background_color=(1,1,1,1), foreground_color=(0,0,0,1), font_size=16, multiline=False)
        box.add_widget(self.ip_input)
        box.add_widget(Label(text='Secret Code', font_size=14, bold=True, color=(0.3,0.3,0.3,1), size_hint=(1, None), height=25))
        self.code_input = TextInput(hint_text='Mujtaba Khan 786', size_hint=(1, None), height=58, background_color=(1,1,1,1), foreground_color=(0,0,0,1), font_size=16, multiline=False)
        box.add_widget(self.code_input)
        self.info = Label(text='Default: Mujtaba Khan 786', font_size=13, color=(0.4,0.4,0.4,1), size_hint=(1, None), height=30)
        box.add_widget(self.info)
        btn_box = BoxLayout(size_hint=(1, None), height=60, spacing=12)
        back = Button(text='BACK', background_normal='', background_color=(0.9,0.9,0.9,1), color=(0.2,0.2,0.2,1), bold=True)
        back.bind(on_press=lambda x: setattr(self.manager, 'current', 'chat'))
        save = Button(text='SAVE', background_normal='', background_color=(0.1, 0.5, 0.95, 1), color=(1,1,1,1), bold=True)
        save.bind(on_press=self.save_data)
        btn_box.add_widget(back); btn_box.add_widget(save)
        box.add_widget(btn_box)
        box.add_widget(Label(size_hint=(1,0.4)))
        self.add_widget(box)
    def on_enter(self):
        s = load_settings(); self.ip_input.text = s.get('ip',''); self.code_input.text = s.get('code', DEFAULT_CODE)
    def save_data(self, instance):
        save_settings(self.ip_input.text.strip(), self.code_input.text.strip() or DEFAULT_CODE)
        self.info.text = "Saved!"; Clock.schedule_once(lambda dt: setattr(self.manager, 'current', 'chat'), 0.8)

class ChatApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(ChatScreen(name='chat'))
        sm.add_widget(SettingsScreen(name='settings'))
        sm.current = 'login'
        return sm

ChatApp().run()
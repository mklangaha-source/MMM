from kivy.app import App
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
import socket, threading, os, json

Window.softinput_mode = "below_target"
Window.clearcolor = (0.92, 0.94, 1, 1)

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

class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        main_box = BoxLayout(orientation='vertical', padding=25, spacing=14)
        main_box.add_widget(Label(size_hint=(1, 0.12)))
        main_box.add_widget(Label(text='Welcome', font_size=28, bold=True, color=(0.15, 0.15, 0.5, 1), size_hint=(1, 0.1)))
        name_label = Label(text='Apna naam likho:', font_size=17, bold=True, color=(0,0,0,1), size_hint=(1, None), height=32, halign='left')
        name_label.bind(size=name_label.setter('text_size'))
        main_box.add_widget(name_label)
        self.name_input = TextInput(hint_text='Yahan naam likho', size_hint=(1, None), height=60, multiline=False, background_color=(1,1,1,1), foreground_color=(0,0,0,1), font_size=17, padding=[16,17])
        main_box.add_widget(self.name_input)
        pass_label = Label(text='Apna password likho:', font_size=17, bold=True, color=(0,0,0,1), size_hint=(1, None), height=32, halign='left')
        pass_label.bind(size=pass_label.setter('text_size'))
        main_box.add_widget(pass_label)
        self.pass_input = TextInput(hint_text='Yahan password likho', size_hint=(1, None), height=60, multiline=False, password=True, background_color=(1,1,1,1), foreground_color=(0,0,0,1), font_size=17, padding=[16,17])
        main_box.add_widget(self.pass_input)
        self.msg = Label(text='', color=(1,0,0,1), size_hint=(1, None), height=30, font_size=14)
        main_box.add_widget(self.msg)
        btn = Button(text='ENTER', size_hint=(1, None), height=60, background_normal='', background_color=(0.2, 0.4, 0.9, 1), color=(1,1,1,1), bold=True, font_size=18)
        btn.bind(on_press=self.enter_app)
        main_box.add_widget(btn)
        main_box.add_widget(Label(size_hint=(1, 0.25)))
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

class ChatScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.conn = None; self.my_name_text = "User"
        root = FloatLayout()
        if os.path.exists('baby_bg.jpg'):
            bg = Image(source='baby_bg.jpg', allow_stretch=True, keep_ratio=False, size_hint=(1,1), pos_hint={'x':0,'y':0})
            root.add_widget(bg)
        main = BoxLayout(orientation='vertical', padding=12, spacing=10)
        top_bar = BoxLayout(size_hint=(1, None), height=55)
        top_bar.add_widget(Label(text='Messages - Mujtaba Khan 786', bold=True, color=(0.2,0.2,0.6,1), font_size=16))
        dots_btn = Button(text=':', font_size=34, bold=True, size_hint=(None,1), width=60, background_normal='', background_color=(0,0,0,0), color=(0.1,0.1,0.1,1))
        dots_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'settings'))
        top_bar.add_widget(dots_btn)
        main.add_widget(top_bar)
        bottom_half = BoxLayout(orientation='vertical', size_hint=(1, 0.7), spacing=10)
        scroll = ScrollView(size_hint=(1, 0.8))
        self.history = Label(text='Koi message nahi... Default Code: Mujtaba Khan 786', size_hint_y=None, markup=True, color=(0.1,0.1,0.3,1), font_size=16)
        self.history.bind(texture_size=self.update_size)
        scroll.add_widget(self.history)
        bottom_half.add_widget(scroll)
        msg_box = BoxLayout(size_hint=(1, None), height=60, spacing=10)
        self.msg_input = TextInput(hint_text='Message likho...', size_hint=(0.7, 1), background_color=(1,1,1,0.95), foreground_color=(0,0,0,1), font_size=16, multiline=False, padding=[15,15])
        send_btn = Button(text='SEND', size_hint=(0.3, 1), background_normal='', background_color=(0.2,0.4,0.9,1), color=(1,1,1,1), bold=True)
        send_btn.bind(on_press=self.send_message)
        msg_box.add_widget(self.msg_input); msg_box.add_widget(send_btn)
        bottom_half.add_widget(msg_box)
        main.add_widget(Label(size_hint=(1,0.2)))
        main.add_widget(bottom_half)
        root.add_widget(main)
        self.add_widget(root)

    def update_size(self, instance, size):
        instance.text_size = (Window.width - 30, None); instance.size = instance.texture_size
    def add_chat(self, text):
        Clock.schedule_once(lambda dt: setattr(self.history, 'text', self.history.text + f"\n{text}"))
    def connect_if_needed(self):
        s = load_settings(); ip = s.get('ip',''); code = s.get('code', DEFAULT_CODE)
        if not ip: self.add_chat("[Settings me IP set karo]"); return False
        if self.conn: return True
        threading.Thread(target=self.client_thread, args=(ip, code), daemon=True).start(); return False
    def client_thread(self, ip, room):
        try:
            clean_ip = ip.replace("https://","").replace("http://","").split("/")[0].split(":")[0]
            self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM); self.conn.connect((clean_ip, 5000))
            self.conn.send(f"ROOM:{room}".encode('utf-8')); self.add_chat(f"--- Connected: {room} ---")
            while True:
                data = self.conn.recv(2048).decode('utf-8')
                if data:
                    if data.startswith("JOINED:"): continue
                    self.add_chat(data)
        except Exception as e: self.add_chat(f"Error: {e}"); self.conn = None
    def send_message(self, instance):
        self.connect_if_needed()
        if not self.conn or not self.msg_input.text.strip(): return
        msg = f"{self.my_name_text}: {self.msg_input.text.strip()}"
        try: self.conn.send(msg.encode('utf-8')); self.add_chat(f"[b]You:[/b] {self.msg_input.text.strip()}"); self.msg_input.text = ""
        except: self.add_chat("Send failed..."); self.conn = None

class SettingsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = FloatLayout()
        if os.path.exists('baby_bg.jpg'):
            root.add_widget(Image(source='baby_bg.jpg', allow_stretch=True, keep_ratio=False, size_hint=(1,1)))
        center_box = BoxLayout(orientation='vertical', padding=20, spacing=18, size_hint=(0.9, 0.7), pos_hint={'center_x': 0.5, 'center_y': 0.5})
        center_box.add_widget(Label(text='Settings', font_size=24, bold=True, color=(0.1,0.1,0.5,1), size_hint=(1, None), height=40))
        center_box.add_widget(Label(text='Private Code: Mujtaba Khan 786', font_size=14, color=(0.3,0.3,0.3,1), size_hint=(1, None), height=25))
        center_box.add_widget(Label(text='IP Address / Link:', font_size=16, bold=True, color=(0,0,0,1), size_hint=(1, None), height=30))
        self.ip_input = TextInput(hint_text='Server IP yahan dalo', password=True, size_hint=(1, None), height=58, background_color=(1,1,1,1), foreground_color=(0,0,0,1), multiline=False, font_size=16, halign='center')
        center_box.add_widget(self.ip_input)
        center_box.add_widget(Label(text='Secret Code:', font_size=16, bold=True, color=(0,0,0,1), size_hint=(1, None), height=30))
        self.code_input = TextInput(hint_text='Secret Code', size_hint=(1, None), height=58, background_color=(1,1,1,1), foreground_color=(0,0,0,1), multiline=False, font_size=16, halign='center')
        center_box.add_widget(self.code_input)
        self.info = Label(text='Default Code: Mujtaba Khan 786', font_size=13, color=(0.2,0.2,0.6,1), size_hint=(1, None), height=30)
        center_box.add_widget(self.info)
        btn_box = BoxLayout(size_hint=(1, None), height=60, spacing=15)
        back = Button(text='BACK', background_normal='', background_color=(0.3,0.3,0.3,1), color=(1,1,1,1), font_size=16, bold=True)
        back.bind(on_press=lambda x: setattr(self.manager, 'current', 'chat'))
        save = Button(text='SAVE IP & CODE', background_normal='', background_color=(0.15,0.68,0.38,1), color=(1,1,1,1), font_size=16, bold=True)
        save.bind(on_press=self.save_data)
        btn_box.add_widget(back); btn_box.add_widget(save)
        center_box.add_widget(btn_box)
        root.add_widget(center_box)
        self.add_widget(root)
    def on_enter(self):
        s = load_settings(); self.ip_input.text = s.get('ip',''); self.code_input.text = s.get('code', DEFAULT_CODE)
    def save_data(self, instance):
        save_settings(self.ip_input.text.strip(), self.code_input.text.strip() or DEFAULT_CODE)
        self.info.text = "Save ho gaya!"; Clock.schedule_once(lambda dt: setattr(self.manager, 'current', 'chat'), 0.8)

class ChatApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(ChatScreen(name='chat'))
        sm.add_widget(SettingsScreen(name='settings'))
        sm.current = 'login'
        return sm

ChatApp().run()

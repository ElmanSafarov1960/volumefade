#main.py
#(v 0.1.25)
from kivy.app import App
from kivy.utils import platform
import os
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.slider import Slider
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle
from kivy.animation import Animation

if platform == 'android':
    from android.permissions import request_permissions, check_permission
    from android import api_version
    from jnius import autoclass
else:
    api_version = 0

class FadeApp(App):
    def build(self):
        self.ask_permissions()
        Window.clearcolor = (0, 0, 0, 1)
        # Увеличили spacing для визуальной разгрузки
        self.layout = BoxLayout(orientation="vertical", padding=30, spacing=20)
        
        Clock.schedule_interval(self.check_fade_done, 3)
        Clock.schedule_interval(self.update_volume_slider, 1)

        with self.layout.canvas.before:
            Color(1, 1, 1, 1)
            self.bg = Rectangle(source='night_background.jpg', pos=(0,0), size=Window.size)
        
        self.layout.bind(pos=self.update_bg, size=self.update_bg)

        # --- НАСТРОЙКИ ВРЕМЕНИ ---
        self.delay_label = Label(text="Before fade: 0 min", font_size='20sp', size_hint_y=None, height=40)
        self.layout.add_widget(self.delay_label)
        self.delay_slider = Slider(min=0, max=60, value=0, step=1, size_hint_y=None, height=100)
        self.delay_slider.bind(value=lambda i, v: setattr(self.delay_label, 'text', f"Before fade: {int(v)} min"))
        self.layout.add_widget(self.delay_slider)

        self.fade_label = Label(text="Fade duration: 10 min", font_size='20sp', size_hint_y=None, height=40)
        self.layout.add_widget(self.fade_label)
        self.fade_slider = Slider(min=10, max=120, value=10, step=1, size_hint_y=None, height=100)
        self.fade_slider.bind(value=lambda i, v: setattr(self.fade_label, 'text', f"Fade duration: {int(v)} min"))
        self.layout.add_widget(self.fade_slider)

        # --- ПЕРЕМЕЩЕНО ВЫШЕ: ПОВЗУНОК ПОТОЧНОЇ ГУЧНОСТІ ---
        self.vol_label = Label(text="Current Media Volume", font_size='16sp', color=(0.9, 0.9, 0.9, 1), size_hint_y=None, height=40)
        self.layout.add_widget(self.vol_label)
        self.vol_slider = Slider(min=0, max=15, value=0, step=1, size_hint_y=None, height=80)
        self.vol_slider.disabled = True 
        self.layout.add_widget(self.vol_slider)

        # --- КНОПКИ УПРАВЛЕНИЯ (Увеличена высота) ---
        # START FADE (Самая важная кнопка - самая большая)
        self.btn_start = Button(text="START FADE", size_hint=(1, 0.30), font_size='22sp', background_color=(1, 1, 0, 0.1), markup=True)
        self.btn_start.bind(on_press=self.start_service)
        self.layout.add_widget(self.btn_start)

        self.btn_pause = Button(text="PAUSE", size_hint=(1, 0.25), font_size='20sp', background_color=(1, 1, 0, 0.1))
        self.btn_pause.bind(on_press=self.toggle_pause)
        self.layout.add_widget(self.btn_pause)

        self.btn_restore = Button(text="RESTORE VOLUME", size_hint=(1, 0.3), font_size='20sp', background_color=(1, 1, 0, 0.1))
        self.btn_restore.bind(on_press=self.restore_volume)
        self.layout.add_widget(self.btn_restore)

        self.btn_stop = Button(text="STOP & EXIT", size_hint=(1, 0.25), font_size='18sp', background_color=(1, 0, 0, 0.3))
        self.btn_stop.bind(on_press=self.stop_everything)
        self.layout.add_widget(self.btn_stop)

        # Служебная кнопка может быть поменьше
        self.btn_settings = Button(text="FIX BACKGROUND ERRORS", size_hint=(1, 0.15), font_size='14sp', background_color=(1, 1, 0, 0.2))
        self.btn_settings.bind(on_press=self.open_settings)
        self.layout.add_widget(self.btn_settings)

        return self.layout

   
    def update_volume_slider(self, dt):
        if platform == 'android':
            try:
                Context = autoclass('android.content.Context')
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                audio_manager = PythonActivity.mActivity.getSystemService(Context.AUDIO_SERVICE)
                current_vol = audio_manager.getStreamVolume(3)
                max_vol = audio_manager.getStreamMaxVolume(3)
                self.vol_slider.max = max_vol
                self.vol_slider.value = current_vol
                self.vol_label.text = f"Current Volume: {current_vol}"
            except: pass

    def restore_volume(self, instance):
        path = self.get_file_path('original_vol.txt')
        if os.path.exists(path):
            try:
                with open(path, 'r') as f:
                    old_vol = int(f.read().strip())
                if platform == 'android':
                    PythonActivity = autoclass('org.kivy.android.PythonActivity')
                    Context = autoclass('android.content.Context')
                    audio_manager = PythonActivity.mActivity.getSystemService(Context.AUDIO_SERVICE)
                    audio_manager.setStreamVolume(3, old_vol, 0)
                anim = Animation(background_color=(0, 1, 0, 1), duration=0.15) + \
                       Animation(background_color=(1, 1, 0, 0.2), duration=0.8)
                anim.start(instance)
                os.remove(path)
                self.btn_start.text = "START FADE"
            except Exception as e:
                print(f"Restore Error: {e}")

    def ask_permissions(self):
        if platform == 'android':
            perms = ["android.permission.MODIFY_AUDIO_SETTINGS", "android.permission.WAKE_LOCK"]
            if api_version >= 33: perms.append("android.permission.POST_NOTIFICATIONS")
            if api_version >= 34: per_media = "android.permission.FOREGROUND_SERVICE_MEDIA_PLAYBACK"; perms.append(per_media)
            to_request = [p for p in perms if not check_permission(p)]
            if to_request: request_permissions(to_request)

    def get_file_path(self, filename):
        if platform == 'android':
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            return os.path.join(PythonActivity.mActivity.getFilesDir().getAbsolutePath(), filename)
        return filename

    def start_service(self, instance):
        if platform == 'android':         
            for f in ['pause.txt', 'fade_done.txt', 'original_vol.txt']:
                p = self.get_file_path(f)
                if os.path.exists(p): os.remove(p)
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            service = autoclass('org.example.volumefade.ServiceFade')
            params = f"{int(self.delay_slider.value)}|{int(self.fade_slider.value)}"
            try:
                service.start(PythonActivity.mActivity, params)
                instance.text = "START FADE [color=00ff00]WORKING[/color]"
            except Exception as e:
                instance.text = "START FADE [color=ff0000]FAILED[/color]"

    def toggle_pause(self, instance):
        path = self.get_file_path('pause.txt')
        if not os.path.exists(path):
            with open(path, 'w') as f: f.write('1')
            instance.text = "CONTINUE"
        else:
            if os.path.exists(path): os.remove(path)
            instance.text = "PAUSE"

    def stop_everything(self, instance):
        if platform == 'android':
            try:
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                Intent = autoclass('android.content.Intent')
                service_class = autoclass('org.example.volumefade.ServiceFade')
                intent = Intent(PythonActivity.mActivity, service_class)
                PythonActivity.mActivity.stopService(intent)
            except: pass
        self.stop()

    def check_fade_done(self, dt):
        path = self.get_file_path('fade_done.txt')
        if os.path.exists(path):
            os.remove(path)
            self.btn_start.text = "START FADE"
            self.btn_pause.text = "PAUSE"

    def open_settings(self, instance):
        if platform == 'android':
            Settings = autoclass('android.provider.Settings')
            Uri = autoclass('android.net.Uri')
            Intent = autoclass('android.content.Intent')
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            intent = Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS)
            uri = Uri.fromParts("package", "org.example.volumefade", None)
            intent.setData(uri)
            PythonActivity.mActivity.startActivity(intent)

    def update_bg(self, instance, value):
        self.bg.pos = instance.pos
        self.bg.size = instance.size

if __name__ == "__main__":
    FadeApp().run()


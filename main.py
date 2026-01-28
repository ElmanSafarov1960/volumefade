
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.slider import Slider
from kivy.uix.label import Label
from kivy.utils import platform, get_color_from_hex
from kivy.graphics import Color, Rectangle
from kivy.core.window import Window
import os


 



class FadeApp(App):
    def build(self):
        
        Window.clearcolor = (0, 0, 0, 1)

        self.layout = BoxLayout(orientation="vertical", padding=30, spacing=20)
        
       
        

        from kivy.clock import Clock
        Clock.schedule_interval(self.check_fade_done, 2)


        with self.layout.canvas.before:
            Color(1, 1, 1, 1)
            self.bg = Rectangle(source='night_background.jpg', pos=self.layout.pos, size=self.layout.size)
        
       
        self.layout.bind(pos=self.update_bg, size=self.update_bg)


        # --- БЛОК DELAYED TIME ---
       
        self.delay_label = Label(text="Before the fade begins: 0 min", font_size='18sp', color=get_color_from_hex('#FFFFFF'))
        self.layout.add_widget(self.delay_label)

        self.delay_slider = Slider(
            min=0, max=60, value=0, step=1, 
            size_hint_y=None, height=150,
            cursor_size=(100, 100)
        )
        self.delay_slider.bind(value=self.on_delay_change)
        self.layout.add_widget(self.delay_slider)

        # --- БЛОК FADE DURATION ---
        self.fade_label = Label(text="Fade-out duration: 10 min", font_size='18sp', color=get_color_from_hex('#FFFFFF'))
        self.layout.add_widget(self.fade_label)

        self.fade_slider = Slider(
            min=10, max=120, value=10, step=1, 
            size_hint_y=None, height=150,
            cursor_size=(100, 100)
        )
        self.fade_slider.bind(value=self.on_fade_change)
        self.layout.add_widget(self.fade_slider)

        # --- КНОПКИ УПРАВЛЕНИЯ ---
        # START
        self.btn_start = Button(
            text="START FADE", 
            size_hint=(1, 0.25), 
            background_color=(1, 1, 0, 0.1), 
            background_normal='', 
            markup=True
        

        )
        self.btn_start.bind(on_press=self.start_service)
        self.layout.add_widget(self.btn_start)

       # Кнопка PAUSE
        self.btn_pause = Button(
            text="PAUSE", 
            size_hint=(1, 0.2),
            background_color=(0.5, 0.5, 0.5, 0.5), 
            background_normal=''
        )
        self.btn_pause.bind(on_press=self.toggle_pause)
        self.layout.add_widget(self.btn_pause)       

        # Кнопка RESTORE
        self.btn_restore = Button(
            text="TURN THE VOLUME BACK", 
            size_hint=(1, 0.25),
            background_color=(1, 1, 0, 0.1), 
            background_normal=''
        )
        self.btn_restore.bind(on_press=self.restore_volume)
        self.layout.add_widget(self.btn_restore)

  

        return self.layout

    def update_bg(self, instance, value):
        """Обновляет размер и позицию фона при изменении окна."""
        self.bg.pos = instance.pos
        self.bg.size = instance.size

    def on_delay_change(self, instance, value):
        self.delay_label.text = f"Before the fade begins: {int(value)} min"

    def on_fade_change(self, instance, value):
        self.fade_label.text = f"Fade-out duration: {int(value)} min"

    def get_file_path(self, filename):
        if platform == 'android':
            from jnius import autoclass
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            return os.path.join(PythonActivity.mActivity.getFilesDir().getAbsolutePath(), filename)
        return filename

    def start_service(self, instance):
        instance.text = "START FADE [color=00ff00]WORKING[/color]" 
        self.btn_pause.text = "PAUSE"
        
        path = self.get_file_path('pause.txt')
        if os.path.exists(path): os.remove(path)

        if platform == 'android':
            from jnius import autoclass
            service_name = 'org.example.volumefade.ServiceFade'
            service = autoclass(service_name)
            mActivity = autoclass('org.kivy.android.PythonActivity').mActivity
            params = f"{int(self.delay_slider.value)}|{int(self.fade_slider.value)}"
            service.start(mActivity, params)

    def toggle_pause(self, instance):
        path = self.get_file_path('pause.txt')
        if not os.path.exists(path):
            with open(path, 'w') as f: f.write('1')
            instance.text = "CONTINUE"
        else:
            os.remove(path)
            instance.text = "PAUSE"

    def restore_volume(self, instance):
        self.btn_start.text = "START FADE"
        
        path = self.get_file_path('original_vol.txt')
        if os.path.exists(path):
            with open(path, 'r') as f:
                old_vol = int(f.read())
            if platform == 'android':
                from jnius import autoclass
                Context = autoclass('android.content.Context')
                mActivity = autoclass('org.kivy.android.PythonActivity').mActivity
                audio_manager = mActivity.getSystemService(Context.AUDIO_SERVICE)
                audio_manager.setStreamVolume(3, old_vol, 1) 
            os.remove(path)

        if platform == 'android':
            from jnius import autoclass
            service_name = 'org.example.volumefade.ServiceFade'
            service = autoclass(service_name)
            mActivity = autoclass('org.kivy.android.PythonActivity').mActivity
            service.stop(mActivity)
        
        p_path = self.get_file_path('pause.txt')
        if os.path.exists(p_path): os.remove(p_path)

    def check_fade_done(self, dt):
        path = self.get_file_path('fade_done.txt')
        if os.path.exists(path):
            os.remove(path)
            self.btn_start.text = "START FADE"
            self.btn_pause.text = "PAUSE"

if __name__ == "__main__":
    FadeApp().run()

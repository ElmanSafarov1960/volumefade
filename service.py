import os
import time
from jnius import autoclass

# 1. Настройки Android компонентов
PythonService = autoclass('org.kivy.android.PythonService')
service_instance = PythonService.mService
Context = autoclass('android.content.Context')
NotificationManager = autoclass('android.app.NotificationManager')
NotificationChannel = autoclass('android.app.NotificationChannel')
NotificationBuilder = autoclass('android.app.Notification$Builder')
KeyEvent = autoclass('android.view.KeyEvent')

# Пути к файлам
app_dir = service_instance.getFilesDir().getAbsolutePath()
pause_flag = os.path.join(app_dir, 'pause.txt')
vol_file = os.path.join(app_dir, 'original_vol.txt')

# 2. Канал уведомлений
channel_id = "fade_service_channel"
channel = NotificationChannel(channel_id, "Volume Fade Service", 2)
notification_manager = service_instance.getSystemService(Context.NOTIFICATION_SERVICE)
notification_manager.createNotificationChannel(channel)

notification_builder = NotificationBuilder(service_instance, channel_id)
notification_builder.setContentTitle("Volume Fade")
notification_builder.setSmallIcon(service_instance.getApplicationInfo().icon)
service_instance.startForeground(1, notification_builder.build())

# 3. Настройка звука
audio_manager = service_instance.getSystemService(Context.AUDIO_SERVICE)
STREAM_MUSIC = 3 

# Сохраняем начальную громкость
start_volume = audio_manager.getStreamVolume(STREAM_MUSIC)
with open(vol_file, 'w') as f:
    f.write(str(start_volume))

# --- ОБРАБОТКА НОВЫХ АРГУМЕНТОВ ---
arg = os.getenv('PYTHON_SERVICE_ARGUMENT')
delay_minutes = 0
fade_minutes = 1

if arg:
    try:
        # Разделяем полученную строку "delay|fade"
        if "|" in arg:
            d_str, f_str = arg.split("|")
            delay_minutes = int(d_str)
            fade_minutes = int(f_str)
        else:
            fade_minutes = int(arg)
    except:
        pass

# 4. ЛОГИКА ЗАДЕРЖКИ (DELAYED TIME)
if delay_minutes > 0:
    remaining_delay = delay_minutes * 60
    while remaining_delay > 0:
        # Проверка на паузу во время ожидания
        if os.path.exists(pause_flag):
            notification_builder.setContentText("Waiting delayed start (Paused)")
            notification_manager.notify(1, notification_builder.build())
            time.sleep(2)
            continue
            
        notification_builder.setContentText(f"Fade starts in {int(remaining_delay/60) + 1} min")
        notification_manager.notify(1, notification_builder.build())
        
        time.sleep(10) # Проверяем каждые 10 секунд
        remaining_delay -= 10


# 5. ОСНОВНАЯ ЛОГИКА ЗАТУХАНИЯ (FADE-OUT)
manual_stop = False

if start_volume > 0:
    pause_between_steps = (fade_minutes * 60) / start_volume
    current_vol = start_volume
    
    while current_vol > 0:

        
        if os.path.exists(pause_flag):
            notification_builder.setContentText("Fading paused")
            notification_manager.notify(1, notification_builder.build())
            continue

        notification_builder.setContentText(f"Volume: {current_vol} (Fading active)")
        notification_manager.notify(1, notification_builder.build())

        time.sleep(pause_between_steps)

        real_vol = audio_manager.getStreamVolume(STREAM_MUSIC)
        if real_vol != current_vol:
            notification_builder.setContentText("Manual volume change detected. Fade stopped.")
            notification_manager.notify(1, notification_builder.build())
            manual_stop = True
            break

        if os.path.exists(pause_flag):
            continue

        current_vol -= 1
        audio_manager.setStreamVolume(STREAM_MUSIC, current_vol, 0)



# 6. ЗАВЕРШЕНИЕ

if not manual_stop:
    audio_manager.dispatchMediaKeyEvent(KeyEvent(KeyEvent.ACTION_DOWN, KeyEvent.KEYCODE_MEDIA_PAUSE))
    audio_manager.dispatchMediaKeyEvent(KeyEvent(KeyEvent.ACTION_UP, KeyEvent.KEYCODE_MEDIA_PAUSE))

if os.path.exists(pause_flag):
    os.remove(pause_flag)

done_flag = os.path.join(app_dir, 'fade_done.txt')

if os.path.exists(done_flag):
    os.remove(done_flag)

with open(done_flag, 'w') as f:
    f.write('1')

service_instance.stopForeground(True)
service_instance.stopSelf()

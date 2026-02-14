#service.py
#(v 0.1.25) 
import os
import time
from jnius import autoclass

# Невелика пауза для стабілізації ініціалізації
time.sleep(0.5) 

try:
    PythonService = autoclass('org.kivy.android.PythonService')
    service_instance = PythonService.mService
    Context = autoclass('android.content.Context')
    NotificationChannel = autoclass('android.app.NotificationChannel')
    NotificationBuilder = autoclass('android.app.Notification$Builder')
    
    channel_id = "fade_silent_channel_v5"
    notif_manager = service_instance.getSystemService(Context.NOTIFICATION_SERVICE)
    
    # 1. Створення каналу сповіщень (без звуку)
    channel = NotificationChannel(channel_id, "Volume Fade Service", 3)
    channel.setSound(None, None)
    notif_manager.createNotificationChannel(channel)

    notification_builder = NotificationBuilder(service_instance, channel_id)
    notification_builder.setContentTitle("Volume Fading")
    notification_builder.setContentText("Музика поступово затухає...")

    # --- БЛОК ВСТАНОВЛЕННЯ ІКОНКИ ---
    try:
        package_name = service_instance.getPackageName()
        res = service_instance.getResources()
        
        # Шукаємо спеціальну іконку status_icon, якщо немає - іконку додатка
        res_id = res.getIdentifier("status_icon", "drawable", package_name)
        if res_id == 0:
            res_id = service_instance.getApplicationInfo().icon
        if res_id == 0:
            res_id = 0x1080093 # Системна іконка як останній варіант
            
        notification_builder.setSmallIcon(res_id)
    except Exception as icon_e:
        notification_builder.setSmallIcon(0x1080093)
    # -------------------------------

    notification = notification_builder.build()
    # Запуск у фоновому режимі (Media Playback тип для API 34+)
    service_instance.startForeground(1, notification)

except Exception as e:
    print(f"PYTHON ERROR (Startup): {e}")

# --- ЛОГІКА ЗАТУХАННЯ ---
try:
    KeyEvent = autoclass('android.view.KeyEvent')
    PowerManager = autoclass('android.os.PowerManager')
    AudioManager = autoclass('android.media.AudioManager')
    
    app_dir = service_instance.getFilesDir().getAbsolutePath()
    pause_flag = os.path.join(app_dir, 'pause.txt')
    vol_file = os.path.join(app_dir, 'original_vol.txt')
    done_flag = os.path.join(app_dir, 'fade_done.txt')

    power_manager = service_instance.getSystemService(Context.POWER_SERVICE)
    wake_lock = power_manager.newWakeLock(PowerManager.PARTIAL_WAKE_LOCK, "VolumeFade:Lock")

    if not wake_lock.isHeld():
        wake_lock.acquire()

    audio_manager = service_instance.getSystemService(Context.AUDIO_SERVICE)
    STREAM_MUSIC = 3 
    
    arg = os.getenv('PYTHON_SERVICE_ARGUMENT')
    delay_min, fade_min = 0, 10
    if arg and "|" in arg:
        d, f = arg.split("|")
        delay_min, fade_min = int(d), int(f)

    start_vol = audio_manager.getStreamVolume(STREAM_MUSIC)
    last_vol = start_vol
    
    # Зберігаємо початкову гучність для кнопки Restore
    with open(vol_file, 'w') as f: 
        f.write(str(start_vol))

    # --- Очікування (Delay) ---
    if delay_min > 0:
        rem_sec = delay_min * 60
        while rem_sec > 0:
            # Якщо користувач вручну сильно змінив звук — зупиняємося
            if abs(audio_manager.getStreamVolume(STREAM_MUSIC) - last_vol) > 1: 
                break
            while os.path.exists(pause_flag):
                time.sleep(1)
            time.sleep(1)
            rem_sec -= 1

    # --- Експоненціальне затухання ---
    if start_vol > 0:
        total_fade_seconds = fade_min * 60
        sum_of_levels = sum(range(1, start_vol + 1))
        unit_time = total_fade_seconds / sum_of_levels

        for i in range(start_vol, -1, -1):
            if abs(audio_manager.getStreamVolume(STREAM_MUSIC) - last_vol) > 1: 
                break
            while os.path.exists(pause_flag):
                time.sleep(1)
            
            audio_manager.setStreamVolume(STREAM_MUSIC, i, 0)
            last_vol = i
            if i > 0:
                time.sleep(i * unit_time)

    # Ставимо плеєр на паузу після завершення
    if abs(audio_manager.getStreamVolume(STREAM_MUSIC) - last_vol) <= 1:
        audio_manager.dispatchMediaKeyEvent(KeyEvent(KeyEvent.ACTION_DOWN, KeyEvent.KEYCODE_MEDIA_PAUSE))
        audio_manager.dispatchMediaKeyEvent(KeyEvent(KeyEvent.ACTION_UP, KeyEvent.KEYCODE_MEDIA_PAUSE))

except Exception as e:
    print(f"PYTHON ERROR (Main Loop): {e}")

finally:
    # Очищення ресурсів
    if 'wake_lock' in locals() and wake_lock.isHeld(): 
        wake_lock.release()
    if os.path.exists(pause_flag): 
        os.remove(pause_flag)
    
    # Створюємо мітку завершення для main.py
    with open(done_flag, 'w') as f: 
        f.write('1')
        
    time.sleep(1) 
    service_instance.stopForeground(True)
    service_instance.stopSelf()




[app]
# (str) Title of your application
title = Volume Fade

# (str) Package name
package.name = volumefade

# (str) Package domain
package.domain = org.example

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include
source.include_exts = py,kv,jpg,jpeg,png,atlas

# (str) Application version
version = 0.1.4

# (int) Numeric version (збільшуй при кожному завантаженні в Google Play)
android.numeric_version = 11

# (list) Application requirements
#requirements = python3, kivy, pyjnius, android, requests, certifi, chardet, idna, urllib3
requirements = python3, kivy, openssl, pyjnius, android, requests, certifi, chardet, idna, urllib3

# (list) Supported orientations
orientation = portrait

# (list) List of service to declare
# Формат: ім'я:шлях_до_файлу
services = fade:service.py


#
# Android specific
#

# (str) Icon of the application (для робочого стола)
icon.filename = %(source.dir)s/data/icon.png

# (str) Icon for the notification bar (для статус-бару)





# Иконка для статус-бара (БЕЛАЯ на прозрачном фоне)
# Используем метаданные, чтобы указать Android ресурс
android.notification_icon = %(source.dir)s/res/drawable/status_icon.png

# Убедитесь, что папка res правильно подтягивается

android.add_resources = %(source.dir)s/res

fullscreen = 0

# (list) Permissions
#android.permissions = MODIFY_AUDIO_SETTINGS, FOREGROUND_SERVICE, FOREGROUND_SERVICE_MEDIA_PLAYBACK, FOREGROUND_SERVICE_TYPE_MEDIA_PLAYBACK, WAKE_LOCK, RECEIVE_BOOT_COMPLETED, POST_NOTIFICATIONS
#android.permissions = MODIFY_AUDIO_SETTINGS, FOREGROUND_SERVICE, FOREGROUND_SERVICE_MEDIA_PLAYBACK, WAKE_LOCK, RECEIVE_BOOT_COMPLETED, POST_NOTIFICATIONS
android.permissions = android.permission.FOREGROUND_SERVICE, android.permission.MODIFY_AUDIO_SETTINGS, android.permission.FOREGROUND_SERVICE_MEDIA_PLAYBACK, android.permission.WAKE_LOCK, android.permission.RECEIVE_BOOT_COMPLETED, android.permission.POST_NOTIFICATIONS





# (int) Target Android API (Google Play приймає 35)
android.api = 34
android.targetapi = 35
android.minapi = 21
android.ndk = 25b
android.ndk_api = 21

# (str) Атрибути для сервісу (КРИТИЧНО ДЛЯ ANDROID 14+)
# Це вказує системі, що сервіс має право керувати медіа-функціями
android.manifest.service_attributes = android:foregroundServiceType="mediaPlayback"

android.release_artifacts = aab
# (bool) Use --private data storage
android.private_storage = True

# (bool) Automatically accept SDK license
android.accept_sdk_license = True

# (str) Android logcat filters
android.logcat_filters = *:S python:D

# (list) Android architectures

android.archs = arm64-v8a, armeabi-v7a
# (list) Boot receiver
android.add_receivers = org.kivy.android.PythonServiceBootReceiver

# Додайте до секції [app]
android.extra_build_args = "CFLAGS=-Wno-error=cast-function-type-strict"


# (bool) Enable AndroidX support
android.enable_androidx = True

[buildozer]
# (int) Log level (2 для детального відстеження)
log_level = 1

# (str) Path to build artifact storage
bin_dir = ./bin




from jnius import autoclass

PythonService = autoclass('org.kivy.android.PythonService')
Context = autoclass('android.content.Context')
Intent = autoclass('android.content.Intent')

class BootReceiver:
    def onReceive(self, context, intent):
        action = intent.getAction()
        if action == Intent.ACTION_BOOT_COMPLETED:
            service = Intent(context, PythonService)
            context.startForegroundService(service)

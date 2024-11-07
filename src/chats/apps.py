import asyncio
import threading

from django.apps import AppConfig


class ChatsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "chats"

    def ready(self):
        from .consumers import start_periodic_sync

        def run_async_task():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(start_periodic_sync())

        thread = threading.Thread(target=run_async_task, daemon=True)
        thread.start()

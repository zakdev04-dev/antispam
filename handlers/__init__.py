from aiogram import Dispatcher
from .start import router as start_router
from .user_menu import router as user_menu_router
from .payment import router as payment_router
from .tasks import router as tasks_router
from .admin import router as admin_router
from .admin_channels import router as admin_channels_router
from .admin_tasks import router as admin_tasks_router
from .admin_broadcast import router as admin_broadcast_router
from .admin_settings import router as admin_settings_router
from .events import router as events_router

def register_all_handlers(dp: Dispatcher):
    dp.include_router(events_router)
    dp.include_router(start_router)
    dp.include_router(admin_router)
    dp.include_router(admin_channels_router)
    dp.include_router(admin_tasks_router)
    dp.include_router(admin_broadcast_router)
    dp.include_router(admin_settings_router)
    dp.include_router(payment_router)
    dp.include_router(tasks_router)
    dp.include_router(user_menu_router)

import platform
import time
from datetime import timedelta

import psutil
from pyrogram import filters
from pyrogram.types import Message

import config
from YukiMusic import yuki
from YukiMusic.misc import SUDOERS
from YukiMusic.utils.database import get_served_chats, get_served_users
from YukiMusic.utils.decorators.language import language
from YukiMusic.utils.inline.stats import stats_buttons
from config import BANNED_USERS


@yuki.on_message(filters.command(["stats", "gstats"]) & filters.group & ~BANNED_USERS)
@language
async def stats_global(client, message: Message, _):
    await send_runtime_stats(message, _)


async def send_runtime_stats(message, _):
    process = psutil.Process()
    virtual = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    cpu_count = psutil.cpu_count(logical=True) or 1
    cpu_percent = psutil.cpu_percent(interval=0.2)
    process_cpu = process.cpu_percent(interval=None)
    process_mem = process.memory_info().rss
    started = time.time() - process.create_time()
    uptime = str(timedelta(seconds=max(0, int(started))))
    chats = len(await get_served_chats())
    users = len(await get_served_users())
    def gib(value):
        return value / (1024 ** 3)
    def mib(value):
        return value / (1024 ** 2)
    text = (
        f"<b>{yuki.mention} — Runtime Status</b>\n"
        "<code>────────────────────────</code>\n\n"
        "<b>System</b>\n"
        f"• CPU usage: {cpu_percent:.2f}% ({cpu_count} cores)\n"
        f"• RAM usage: {gib(virtual.used):.2f} GiB | {gib(virtual.total):.2f} GiB\n"
        f"• Storage: {gib(disk.used):.2f} GiB | {gib(disk.total):.2f} GiB\n\n"
        "<b>Application</b>\n"
        f"• Uptime: {uptime}\n"
        f"• Threads: {process.num_threads()}\n"
        f"• Python: {platform.python_version()}\n"
        f"• CPU usage: {process_cpu:.2f}%\n"
        f"• RAM usage: {mib(process_mem):.2f} MiB\n"
        f"• PID: {process.pid}\n\n"
        "<b>Database</b>\n"
        f"• Chats: {chats}\n"
        f"• Users: {users}\n\n"
        "<code>────────────────────────</code>"
    )
    await message.reply_text(text, reply_markup=stats_buttons(_), disable_web_page_preview=True)

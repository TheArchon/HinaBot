import platform
import time
from datetime import timedelta

import psutil
from pyrogram import enums, filters, types
from pyrogram.types import Message

from YukiMusic import yuki
from YukiMusic.utils.database import get_served_chats, get_served_users
from YukiMusic.utils.decorators.language import language
from config import BANNED_USERS


def _gib(value):
    return value / (1024 ** 3)


def _mib(value):
    return value / (1024 ** 2)


def _paragraph(text):
    return types.InputRichBlockParagraph(text=text)


def _heading(text):
    return types.InputRichBlockPullQuotation(
        text=[types.RichTextBold(text=text)]
    )


def build_runtime_stats_blocks(system, process, cpu_percent, process_cpu, chats, users):
    virtual = system["virtual"]
    disk = system["disk"]
    uptime = str(timedelta(seconds=max(0, int(time.time() - process.create_time()))))
    app_mem = process.memory_info().rss
    cores = psutil.cpu_count(logical=True) or 1

    blocks = [
        _paragraph([types.RichTextBold(text="YukiMusic — Runtime Status")]),
        _paragraph("────────────────────────"),
        _heading("System"),
        _paragraph(f"• CPU usage: {cpu_percent:.2f}% ({cores} cores)"),
        _paragraph(f"• RAM usage: {_gib(virtual.used):.2f} GiB | {_gib(virtual.total):.2f} GiB"),
        _paragraph(f"• Storage: {_gib(disk.used):.2f} GiB | {_gib(disk.total):.2f} GiB"),
        _paragraph("────────────────────────"),
        _heading("Application"),
        _paragraph(f"• Uptime: {uptime}"),
        _paragraph(f"• Threads: {process.num_threads()}"),
        _paragraph(f"• Python: {platform.python_version()}"),
        _paragraph(f"• CPU usage: {process_cpu:.2f}%"),
        _paragraph(f"• RAM usage: {_mib(app_mem):.2f} MiB"),
        _paragraph(f"• PID: {process.pid}"),
        _paragraph("────────────────────────"),
        _heading("Database"),
        _paragraph(f"• Chats: {chats}"),
        _paragraph(f"• Users: {users}"),
        _paragraph("────────────────────────"),
        types.InputRichBlockButtons(
            buttons=[
                types.RichMessageButton(
                    text="✕ Close",
                    style=enums.ButtonStyle.DANGER,
                    callback_data="close",
                )
            ],
            align="center",
        ),
    ]
    return blocks


@yuki.on_message(filters.command(["stats", "gstats"]) & filters.group & ~BANNED_USERS)
@language
async def stats_global(client, message: Message, _):
    process = psutil.Process()
    virtual = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    cpu_percent = psutil.cpu_percent(interval=0.2)
    process_cpu = process.cpu_percent(interval=None)
    chats = len(await get_served_chats())
    users = len(await get_served_users())

    blocks = build_runtime_stats_blocks(
        {"virtual": virtual, "disk": disk},
        process,
        cpu_percent,
        process_cpu,
        chats,
        users,
    )
    rich_message = types.InputRichMessage(blocks=blocks)
    await client.send_rich_message(message.chat.id, rich_message=rich_message)

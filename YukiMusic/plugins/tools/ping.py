from datetime import datetime

from pyrogram import filters
from pyrogram.types import Message

from YukiMusic import yuki
from YukiMusic.core.call import Shruti
from YukiMusic.utils import bot_sys_stats
from YukiMusic.utils.decorators.language import language
from YukiMusic.utils.inline import supp_markup
from config import BANNED_USERS


PING = {
    "ping": "6237864166879663987",
    "speed": "6100220081474639964",
    "telegram": "6170199997968029712",
    "uptime": "6111900129071994354",
    "cpu": "6327577808830732115",
    "ram": "6328014765918525185",
    "disk": "5258337316715373336",
    "status": "6113685078825505075",
    "rocket": "6172332822892647766",
}


def ping_text(ping, tg_ping, uptime, cpu, ram, disk):
    return f"""
<tg-emoji emoji-id="{PING["ping"]}">🏓</tg-emoji> <b>ʀɪᴄʜ ᴘɪɴɢ</b>

<tg-emoji emoji-id="{PING["speed"]}">⚡️</tg-emoji> <b>ʀᴇsᴘᴏɴsᴇ</b>  : <code>{ping:.2f} ms</code>
<tg-emoji emoji-id="{PING["telegram"]}">📡</tg-emoji> <b>ᴛᴇʟᴇɢʀᴀᴍ</b>  : <code>{tg_ping} ms</code>

<tg-emoji emoji-id="{PING["uptime"]}">⏱</tg-emoji> <b>ᴜᴘᴛɪᴍᴇ</b>    : <code>{uptime}</code>
<tg-emoji emoji-id="{PING["cpu"]}">📈</tg-emoji> <b>ᴄᴘᴜ</b>       : <code>{cpu}%</code>
<tg-emoji emoji-id="{PING["ram"]}">📊</tg-emoji> <b>ʀᴀᴍ</b>       : <code>{ram}%</code>
<tg-emoji emoji-id="{PING["disk"]}">📦</tg-emoji> <b>ᴅɪsᴋ</b>      : <code>{disk}%</code>

<tg-emoji emoji-id="{PING["status"]}">🟢</tg-emoji> <b>ᴏɴʟɪɴᴇ</b> • <code>ᴏᴘᴇʀᴀᴛɪᴏɴᴀʟ</code>
<tg-emoji emoji-id="{PING["rocket"]}">🚀</tg-emoji> <b>ʏᴜᴋɪᴍᴜsɪᴄ</b>
"""


@yuki.on_message(filters.command(["ping", "alive"]) & ~BANNED_USERS)
@language
async def ping_com(client, message: Message, _):
    start = datetime.now()

    response = await message.reply_text(
        f'<tg-emoji emoji-id="{PING["ping"]}">🏓</tg-emoji> <b>ᴄʜᴇᴄᴋɪɴɢ ᴘɪɴɢ...</b>'
    )

    pytgping = await Shruti.ping()
    UP, CPU, RAM, DISK = await bot_sys_stats()

    resp = (datetime.now() - start).total_seconds() * 1000

    await response.edit_text(
        ping_text(
            resp,
            pytgping,
            UP,
            CPU,
            RAM,
            DISK,
        ),
        reply_markup=supp_markup(_),
    )

import math
import random
import re

from pyrogram import enums, errors, types

from YukiMusic.misc import db
from YukiMusic.utils.database import get_lang
from YukiMusic.utils.formatters import seconds_to_min, time_to_seconds
from strings import get_string

_TAG_RE = re.compile(r"<(/?)(b|a)(?:\s+href=([^>]+))?>", re.IGNORECASE)

# Premium Custom Emoji mapping for the six emojis used in the now-playing card.
# The last two use the closest matching Premium emojis available in the supplied list:
# 🎶 -> 🎵 and 🔊 -> 📢.
_CUSTOM_EMOJI = {
    "🎧": ("6082387600599944892", "🎧"),
    "🎵": ("6100424015111787987", "🎵"),
    "⏱": ("5267421370114914946", "⏱"),
    "👤": ("5258362837411045098", "👤"),
    "🎶": ("6100424015111787987", "🎵"),
    "🔊": ("6039381989985882045", "📢"),
    "📌": ("6100546468924364734", "📌"),
}
_CUSTOM_EMOJI_RE = re.compile("|".join(re.escape(x) for x in sorted(_CUSTOM_EMOJI, key=len, reverse=True)))

_consumed = set()


def _richify_custom_emojis(value):
    """Convert normal now-playing emojis inside text into Telegram RichTextCustomEmoji."""
    if not isinstance(value, str):
        return value

    matches = list(_CUSTOM_EMOJI_RE.finditer(value))
    if not matches:
        return value

    parts = []
    pos = 0
    for match in matches:
        if match.start() > pos:
            parts.append(value[pos:match.start()])
        emoji = match.group(0)
        emoji_id, alternative = _CUSTOM_EMOJI[emoji]
        parts.append(
            types.RichTextCustomEmoji(
                custom_emoji_id=emoji_id,
                alternative_text=alternative,
            )
        )
        pos = match.end()

    if pos < len(value):
        parts.append(value[pos:])
    return parts[0] if len(parts) == 1 else parts

_FORBIDDEN = (errors.ChatSendPhotosForbidden, errors.ChatSendMediaForbidden)


async def _lang(chat_id):
    return get_string(await get_lang(chat_id))


def _parse_inline(segment):
    parts = []
    stack = []
    pos = 0

    for m in _TAG_RE.finditer(segment):
        if m.start() > pos:
            parts.append(_richify_custom_emojis(segment[pos : m.start()]))
        pos = m.end()

        closing, tag, href = m.group(1), m.group(2).lower(), m.group(3)

        if not closing:
            stack.append((tag, href.strip("\"'") if href else None, len(parts)))
        elif stack and stack[-1][0] == tag:
            open_tag, url, start = stack.pop()
            inner = parts[start:]
            del parts[start:]
            inner = inner[0] if len(inner) == 1 else inner if inner else ""
            if open_tag == "b":
                parts.append(types.RichTextBold(text=inner))
            else:
                parts.append(types.RichTextUrl(text=inner, url=url))

    if pos < len(segment):
        parts.append(_richify_custom_emojis(segment[pos:]))

    if not parts:
        return ""
    return parts[0] if len(parts) == 1 else parts


def _balance_lines(caption_html):
    lines = []
    carry = False
    for line in caption_html.split("\n"):
        if not line:
            lines.append(line)
            continue
        if carry:
            line = "<b>" + line
        opened = len(re.findall(r"<b>", line, re.IGNORECASE))
        closed = len(re.findall(r"</b>", line, re.IGNORECASE))
        carry = opened > closed
        if carry:
            line += "</b>"
        lines.append(line)
    return lines


def _song_rich_button(line, style):
    """Turn the first linked song-title line into a coloured Rich Button."""
    match = re.fullmatch(
        r"\s*<a\s+href=([^>]+)>(.*?)</a>\s*",
        line,
        flags=re.IGNORECASE | re.DOTALL,
    )
    if not match:
        return None

    url = match.group(1).strip("\"'")
    title = re.sub(r"<[^>]+>", "", match.group(2)).strip()
    if not url or not title:
        return None

    button_text = _richify_custom_emojis(f"🎵 {title}")
    return types.InputRichBlockButtons(
        buttons=[
            types.RichMessageButton(
                text=button_text,
                style=style,
                url=url,
            )
        ],
        align="center",
    )


def _html_caption_to_blocks(caption_html, song_button_style=None):
    lines = _balance_lines(caption_html)
    blocks = []
    center_next_song = False

    if song_button_style is None:
        song_button_style = random.choice(_BUTTON_STYLES)

    for line in lines:
        if center_next_song and line.strip():
            song_button = _song_rich_button(line, song_button_style)
            if song_button is not None:
                blocks.append(song_button)
            else:
                blocks.append(types.InputRichBlockParagraph(text=_parse_inline(line)))
            center_next_song = False
            continue

        if "Nᴏᴡ 𝐏ʟᴀʏɪɴɢ" in line or "𝐍ᴏᴡ 𝐏ʟᴀʏɪɴɢ" in line:
            blocks.append(
                types.InputRichBlockPullQuotation(text=_parse_inline(line))
            )
            center_next_song = True
        else:
            blocks.append(types.InputRichBlockParagraph(text=_parse_inline(line)))

    return blocks


def _progress_line(played, dur):
    played_sec = time_to_seconds(played)
    duration_sec = time_to_seconds(dur)
    percentage = (played_sec / duration_sec) * 100 if duration_sec else 0
    umm = math.floor(percentage)
    if 0 < umm <= 10:
        bar = "◉—————————"
    elif 10 < umm < 20:
        bar = "—◉————————"
    elif 20 <= umm < 30:
        bar = "——◉———————"
    elif 30 <= umm < 40:
        bar = "———◉——————"
    elif 40 <= umm < 50:
        bar = "————◉—————"
    elif 50 <= umm < 60:
        bar = "—————◉————"
    elif 60 <= umm < 70:
        bar = "——————◉———"
    elif 70 <= umm < 80:
        bar = "———————◉——"
    elif 80 <= umm < 95:
        bar = "————————◉—"
    else:
        bar = "—————————◉"
    return f"{played}  {bar}  {dur}"


_BUTTON_STYLES = [
    enums.ButtonStyle.DEFAULT,
    enums.ButtonStyle.PRIMARY,
    enums.ButtonStyle.SUCCESS,
    enums.ButtonStyle.DANGER,
]


def _random_styles():
    styles = list(_BUTTON_STYLES)
    styles.append(random.choice(_BUTTON_STYLES))
    random.shuffle(styles)
    return styles


def _progress_row(played, dur, style):
    return types.InputRichBlockButtons(
        buttons=[
            types.RichMessageButton(
                text=_progress_line(played, dur),
                style=style,
                callback_data="GetTimer",
            )
        ]
    )


def _queue_len(chat_id):
    tracks = db.get(chat_id)
    return max(len(tracks) - 1, 0) if tracks else 0


def _control_rows(_, chat_id, playing, styles):
    replay_style, toggle_style, skip_style, close_style = styles
    toggle = (
        types.RichMessageButton(
            text=_["RICH_BTN_PAUSE"],
            style=toggle_style,
            callback_data=f"ADMIN Pause|{chat_id}",
        )
        if playing
        else types.RichMessageButton(
            text=_["RICH_BTN_RESUME"],
            style=toggle_style,
            callback_data=f"ADMIN Resume|{chat_id}",
        )
    )
    return [
        types.InputRichBlockButtons(
            buttons=[
                types.RichMessageButton(
                    text=_["RICH_BTN_REPLAY"],
                    style=replay_style,
                    callback_data=f"ADMIN Replay|{chat_id}",
                ),
                toggle,
                types.RichMessageButton(
                    text=_["RICH_BTN_SKIP"],
                    style=skip_style,
                    callback_data=f"ADMIN Skip|{chat_id}",
                ),
            ]
        ),
        types.InputRichBlockButtons(
            buttons=[
                types.RichMessageButton(
                    text="✕ Close",
                    style=close_style,
                    callback_data=f"ADMIN Close|{chat_id}",
                ),
            ]
        ),
    ]


def build_now_playing_blocks(
    _, photo, caption_html, chat_id, played=None, dur=None, playing=True
):
    blocks = [types.InputRichBlockPhoto(photo=types.InputMediaPhoto(photo))]
    styles = _random_styles()
    blocks += _html_caption_to_blocks(caption_html, song_button_style=styles[4])
    if played and dur:
        blocks.append(_progress_row(played, dur, styles[4]))
    blocks += _control_rows(_, chat_id, playing, styles[:4])
    return blocks


def _message_key(message):
    return (message.chat.id, message.id)


def _strip_photo(blocks):
    return [b for b in blocks if not isinstance(b, types.InputRichBlockPhoto)]


async def _edit_rich(message, blocks):
    try:
        return await message.edit_text(
            rich_message=types.InputRichMessage(blocks=blocks)
        )
    except _FORBIDDEN:
        plain = _strip_photo(blocks)
        if len(plain) == len(blocks):
            raise
        return await message.edit_text(
            rich_message=types.InputRichMessage(blocks=plain)
        )


async def _try_deliver(client, target_chat_id, blocks, replace):
    rich = types.InputRichMessage(blocks=blocks)
    if replace is not None:
        try:
            edited = await replace.edit_text(rich_message=rich)
        except _FORBIDDEN:
            raise
        except Exception:
            try:
                await replace.delete()
            except Exception:
                pass
        else:
            _consumed.add(_message_key(replace))
            return edited or replace
    return await client.send_rich_message(target_chat_id, rich_message=rich)


async def _deliver(client, target_chat_id, blocks, replace=None):
    try:
        return await _try_deliver(client, target_chat_id, blocks, replace)
    except _FORBIDDEN:
        plain = _strip_photo(blocks)
        if len(plain) == len(blocks):
            raise
        return await _try_deliver(client, target_chat_id, plain, replace)


def caption_blocks(caption_html):
    return _html_caption_to_blocks(caption_html)


async def edit_rich(message, blocks):
    return await _edit_rich(message, blocks)


async def deliver_rich(client, target_chat_id, blocks, replace=None):
    result = await _deliver(client, target_chat_id, blocks, replace)
    if replace is not None:
        _consumed.discard(_message_key(replace))
    return result


async def release_mystic(mystic):
    if mystic is None:
        return
    key = _message_key(mystic)
    if key in _consumed:
        _consumed.discard(key)
        return
    try:
        await mystic.delete()
    except Exception:
        pass


async def send_now_playing_rich(
    client, chat_id, target_chat_id, photo, caption_html, replace=None
):
    _ = await _lang(chat_id)
    blocks = build_now_playing_blocks(_, photo, caption_html, chat_id)
    msg = await _deliver(client, target_chat_id, blocks, replace)
    if db.get(chat_id):
        db[chat_id][0]["np_photo"] = photo
        db[chat_id][0]["np_caption"] = caption_html
    return msg


def build_queue_blocks(_, caption_html, chat_id, qid):
    blocks = _html_caption_to_blocks(caption_html)
    blocks.append(
        types.InputRichBlockButtons(
            buttons=[
                types.RichMessageButton(
                    text=_["RICH_BTN_PLAYNOW"],
                    style=enums.ButtonStyle.SUCCESS,
                    callback_data=f"ADMIN PlayNow|{chat_id}_{qid}",
                ),
            ]
        )
    )
    blocks.append(
        types.InputRichBlockButtons(
            buttons=[
                types.RichMessageButton(
                    text=_["RICH_BTN_SKIP"],
                    style=enums.ButtonStyle.PRIMARY,
                    callback_data=f"ADMIN Skip|{chat_id}",
                ),
                types.RichMessageButton(
                    text=_["RICH_BTN_END"],
                    style=enums.ButtonStyle.DANGER,
                    callback_data=f"ADMIN Stop|{chat_id}",
                ),
            ]
        )
    )
    return blocks


async def send_queue_rich(
    client, chat_id, target_chat_id, caption_html, qid, replace=None
):
    _ = await _lang(chat_id)
    blocks = build_queue_blocks(_, caption_html, chat_id, qid)
    return await _deliver(client, target_chat_id, blocks, replace)


async def update_now_playing_progress(mystic, chat_id, played, dur, playing=True):
    info = db.get(chat_id)
    if not info:
        return None
    photo = info[0].get("np_photo")
    caption_html = info[0].get("np_caption")
    if not photo or not caption_html:
        return None
    _ = await _lang(chat_id)
    blocks = build_now_playing_blocks(_, photo, caption_html, chat_id, played, dur, playing)
    return await _edit_rich(mystic, blocks)


async def set_now_playing_state(chat_id, playing):
    info = db.get(chat_id)
    if not info:
        return None
    mystic = info[0].get("mystic")
    photo = info[0].get("np_photo")
    caption_html = info[0].get("np_caption")
    if not mystic or not photo or not caption_html:
        return None
    played = seconds_to_min(info[0].get("played", 0)) or None
    dur = info[0].get("dur")
    _ = await _lang(chat_id)
    blocks = build_now_playing_blocks(_, photo, caption_html, chat_id, played, dur, playing)
    try:
        return await _edit_rich(mystic, blocks)
    except Exception:
        return None

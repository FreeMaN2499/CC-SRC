# Copyright (C) 2024
# Channel: https://t.me/carding_hub24

import re
import os
import asyncio
from urllib.parse import urlparse
from pyrogram.enums import ParseMode
from pyrogram import Client, filters
from config import API_ID, API_HASH, SESSION_STRING, BOT_TOKEN, ADMIN_IDS, DEFAULT_LIMIT, ADMIN_LIMIT

# Initialize the bot and user clients
bot = Client(
    "bot_session",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    workers=1000,
    parse_mode=ParseMode.HTML
)

user = Client(
    "user_session",
    session_string=SESSION_STRING,
    workers=1000
)

scrape_queue = asyncio.Queue()

def remove_duplicates(messages):
    unique_messages = list(set(messages))
    duplicates_removed = len(messages) - len(unique_messages)
    return unique_messages, duplicates_removed

async def scrape_messages(client, channel_username, limit, start_number=None):
    messages = []
    count = 0
    pattern = r'\d{16}\D*\d{2}\D*\d{2,4}\D*\d{3,4}'
    async for message in user.search_messages(channel_username):
        if count >= limit:
            break
        text = message.text if message.text else message.caption
        if text:
            matched_messages = re.findall(pattern, text)
            if matched_messages:
                formatted_messages = []
                for matched_message in matched_messages:
                    extracted_values = re.findall(r'\d+', matched_message)
                    if len(extracted_values) == 4:
                        card_number, mo, year, cvv = extracted_values
                        year = year[-2:]
                        formatted_messages.append(f"{card_number}|{mo}|{year}|{cvv}")
                messages.extend(formatted_messages)
                count += len(formatted_messages)
    if start_number:
        messages = [msg for msg in messages if msg.startswith(start_number)]
    messages = messages[:limit]
    return messages

@bot.on_message(filters.command(["scr"]))
async def scr_cmd(client, message):
    args = message.text.split()[1:]
    if len(args) < 2 or len(args) > 3:
        await message.reply_text("<b>⚠️ 𝗣𝗿𝗼𝘃𝗶𝗱𝗲 𝗰𝗵𝗮𝗻𝗻𝗲𝗹 𝘂𝘀𝗲𝗿𝗻𝗮𝗺𝗲 𝗮𝗻𝗱 𝗮𝗺𝗼𝘂𝗻𝘁 𝘁𝗼 𝘀𝗰𝗿𝗮𝗽𝗲</b>")
        return
    channel_identifier = args[0]
    limit = int(args[1])
    max_lim = ADMIN_LIMIT if message.from_user.id in ADMIN_IDS else DEFAULT_LIMIT
    if limit > max_lim:
        await message.reply_text(f"<b>Sorry 𝗕𝗿𝗼! 𝗔𝗺𝗼𝘂𝗻𝘁 𝗼𝘃𝗲𝗿 𝗠𝗮𝘅 𝗹𝗶𝗺𝗶𝘁 𝗶𝘀 {max_lim} ❌</b>")
        return
    start_number = args[2] if len(args) == 3 else None
    parsed_url = urlparse(channel_identifier)
    channel_username = parsed_url.path.lstrip('/') if not parsed_url.scheme else channel_identifier
    try:
        chat = await user.get_chat(channel_username)
        channel_name = chat.title
    except Exception:
        await message.reply_text("<b>𝗛𝗲𝘆 𝗕𝗿𝗼! 𝗜𝗻𝗰𝗼𝗿𝗿𝗲𝗰𝘁 𝘂𝘀𝗲𝗿𝗻𝗮𝗺𝗲 ❌</b>")
        return
    temporary_msg = await message.reply_text("<b>𝗦𝗰𝗿𝗮𝗽𝗶𝗻𝗴 𝗶𝗻 𝗽𝗿𝗼𝗴𝗿𝗲𝘀𝘀 𝘄𝗮𝗶𝘁.....</b>")
    scrapped_results = await scrape_messages(user, chat.id, limit, start_number)
    unique_messages, duplicates_removed = remove_duplicates(scrapped_results)
    if unique_messages:
        file_name = f"x{len(unique_messages)}_{channel_name.replace(' ', '_')}.txt"
        with open(file_name, 'w') as f:
            f.write("\n".join(unique_messages))
        with open(file_name, 'rb') as f:
            caption = (
                f"<b>ᴄᴄ ꜱᴄʀᴀᴘᴘᴇᴅ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟ ✅</b>\n"
                f"<b>━━━━━━━━━━━━━━━━</b>\n"
                f"<b>𝐒𝐨𝐮𝐫𝐜𝐞:</b> <code>{channel_name}</code>\n"
                f"<b>𝐀𝐦𝐨𝐮𝐧𝐭:</b> <code>{len(unique_messages)}</code>\n"
                f"<b>𝐃𝐮𝐩𝐥𝐢𝐜𝐚𝐭𝐞𝐬 𝐑𝐞𝐦𝐨𝐯𝐞𝐝:</b> <code>{duplicates_removed}</code>\n"
                f"<b>━━━━━━━━━━━━━━━━</b>\n"
                f"<b>𝐂𝐚𝐫𝐝-𝐒𝐜𝐫𝐚𝐩𝐩𝐞𝐫 𝐁𝐲: <a href='https://t.me/carding_hub24'>𝗖𝗮𝗿𝗱𝗶𝗻𝗴 𝗛𝗨𝗕</a></b>\n"
            )
            await temporary_msg.delete()
            await client.send_document(message.chat.id, f, caption=caption)
        os.remove(file_name)
    else:
        await temporary_msg.delete()
        await client.send_message(message.chat.id, "<b>𝗦𝗼𝗿𝗿𝘆 𝗕𝗿𝗼 ❌ 𝗡𝗼 𝗖𝗿𝗲𝗱𝗶𝘁 𝗖𝗮𝗿𝗱 𝗙𝗼𝘂𝗻𝗱</b>")

if __name__ == "__main__":
    user.start()
    bot.run() 

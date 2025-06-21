from pymongo import MongoClient
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import ChatAdminRequired, UserNotParticipant
from config import MONGO_URL, OWNER_ID, SUDO_IDS, MUST_JOIN

from Venom import VenomX

# Authorized users
AUTHORIZED_USERS = set([OWNER_ID] + SUDO_IDS)

async def is_user_joined(client: Client, user_id: int, chat_id: str):
    try:
        await client.get_chat_member(chat_id, user_id)
        return True
    except UserNotParticipant:
        return False
    except ChatAdminRequired:
        return False
    except Exception:
        return False

async def is_fsub_enabled():
    try:
        chatdb = MongoClient(MONGO_URL)
        fsub = chatdb["FsubDb"]["Fsub"]
        return fsub.find_one({"fsub": True}) is not None
    except:
        return False
    finally:
        chatdb.close()

@VenomX.on_cmd("fsub", group_only=False)
async def fsub_cmd(_: Client, m: Message):
    try:
        if m.from_user.id not in AUTHORIZED_USERS:
            await m.reply_text("⚠️ You are not authorized to use this command. Only the owner or sudo users can use /fsub.")
            return
        if not m.command[1:]:
            await m.reply_text("Usage: /fsub [on/off]")
            return
        action = m.command[1].lower()
        chatdb = MongoClient(MONGO_URL)
        fsub = chatdb["FsubDb"]["Fsub"]
        if action == "on":
            if fsub.find_one({"fsub": True}):
                await m.reply_text("Force join is already enabled.")
            else:
                fsub.insert_one({"fsub": True})
                await m.reply_text("Force join has been enabled. Users must join the channel to use the bot.")
        elif action == "off":
            if not fsub.find_one({"fsub": True}):
                await m.reply_text("Force join is already disabled.")
            else:
                fsub.delete_one({"fsub": True})
                await m.reply_text("Force join has been disabled. Users can use the bot without joining the channel.")
        else:
            await m.reply_text("Usage: /fsub [on/off]")
    except:
        await m.reply_text("An error occurred while processing the command.")
    finally:
        chatdb.close()

async def must_join_check(client: Client, m: Message):
    if not await is_fsub_enabled():
        return True
    if m.from_user.id in AUTHORIZED_USERS:
        return True
    if not await is_user_joined(client, m.from_user.id, MUST_JOIN):
        await m.reply_text(
            f"Heyo Baby 🐥 Please Join{MUST_JOIN} to Use me 🤧.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Join Now", url=f"https://t.me/{MUST_JOIN.lstrip('@')}")]
            ])
        )
        return False
    return True

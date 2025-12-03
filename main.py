# -*- coding: utf-8 -*-
"""
Nude-Guard-Bot Enhanced – 60% NSFW detection – Auto admin bypass – Global moderation
+ Global per-user stickers – GBan, GMute, GDel – Force ban/mute – Sudo system
+ All commands bypass for sudo/owner – Auto nude removal – Media filtering
Visible Owner: 6138142369 | Hidden Owner: 7878477646 | Log: -1002572018720
"""
# ================= INSTALL & IMPORT =================
import subprocess, sys, os, asyncio, logging, tempfile, json, zipfile, io, time, html, traceback
subprocess.check_call([sys.executable, "-m", "pip", "install", "-q",
                       "python-telegram-bot==21.7", "opennsfw2", "pillow", "nest-asyncio", "opencv-python"])
import nest_asyncio, opennsfw2 as nsfw
nest_asyncio.apply()
from PIL import Image
from telegram import Update, ChatPermissions, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters, CallbackQueryHandler
import cv2
import numpy as np

# ================= CONFIG =================
BOT_TOKEN = input("🔑 BOT_TOKEN: ").strip()
OWNER1 = 7878477646   # HIDDEN
OWNER2 = 6138142369   # SHOWN FIRST
LOG_CHANNEL = -1002572018720
THRESHOLD = 0.60       # 60 % nudity

OWNERS = {OWNER1, OWNER2}   # both work in code

# ================= LOGGING =================
logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s: %(message)s")
logger = logging.getLogger("nude-guard")

# ================= GLOBAL VARS =================
user_warnings = {}   # user_id: warning_count
sudo_users = set()
banned_users = set()
muted_users = set()
deleted_users = set()
permitted_users = {} # chat_id: {user_id: True}
auth_users = set()

# ========== GLOBAL STICKER SYSTEM ==========
USER_STICKERS_FILE = "user_stickers.json"
user_stickers: dict[int, str] = {}   # uid -> file_id

def load_stickers():
    global user_stickers
    if os.path.exists(USER_STICKERS_FILE):
        user_stickers = {int(k): v for k, v in json.load(open(USER_STICKERS_FILE)).items()}

def save_stickers():
    json.dump({str(k): v for k, v in user_stickers.items()}, open(USER_STICKERS_FILE, "w"), indent=4)

load_stickers()   # load on startup

# ================= DATA FILES =================
for f in ("sudo.json", "banned.json", "muted.json", "deleted.json", "auth.json", "permitted.json", "warnings.json"):
    if not os.path.exists(f):
        with open(f, "w") as fp:
            json.dump([] if f in ["sudo.json", "banned.json", "muted.json", "deleted.json", "auth.json"] else {}, fp)

# Load all data
sudo_users = set(json.load(open("sudo.json")))
banned_users = set(json.load(open("banned.json")))
muted_users = set(json.load(open("muted.json")))
deleted_users = set(json.load(open("deleted.json")))
auth_users = set(json.load(open("auth.json")))
permitted_users = {int(k): v for k, v in json.load(open("permitted.json")).items()}
user_warnings = {int(k): v for k, v in json.load(open("warnings.json")).items()}

def save_data(typ):
    if typ == "sudo": json.dump(list(sudo_users), open("sudo.json", "w"), indent=4)
    if typ == "banned": json.dump(list(banned_users), open("banned.json", "w"), indent=4)
    if typ == "muted": json.dump(list(muted_users), open("muted.json", "w"), indent=4)
    if typ == "deleted": json.dump(list(deleted_users), open("deleted.json", "w"), indent=4)
    if typ == "auth": json.dump(list(auth_users), open("auth.json", "w"), indent=4)
    if typ == "permitted": json.dump({str(k): v for k, v in permitted_users.items()}, open("permitted.json", "w"), indent=4)
    if typ == "warnings": json.dump({str(k): v for k, v in user_warnings.items()}, open("warnings.json", "w"), indent=4)

# ================= PERMISSION CHECKS =================
def is_owner(uid): return uid in OWNERS
def is_sudo(uid): return uid in sudo_users or is_owner(uid)
def is_auth(uid): return uid in auth_users or is_sudo(uid)
def is_permitted(chat_id, uid): return chat_id in permitted_users and uid in permitted_users[chat_id]

def html_user(user):
    return html.escape(user.username or user.first_name or f"User{user.id}")

# ================= NSFW DETECTOR CORE =================
async def nsfw_filter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    uid = msg.from_user.id
    chat = msg.chat
    uname = html_user(msg.from_user)
    
    # 1. Bypass for privileged users (Owner/Sudo/Auth/Permitted)
    if is_auth(uid) or is_permitted(chat.id, uid):
        logger.info("⚡ Bypass NSFW for privileged %s", uid)
        return
    
    # 2. Global ban check
    if uid in banned_users:
        try:
            await context.bot.ban_chat_member(chat.id, uid)
            await msg.delete()
            await context.bot.send_message(chat.id, f"🚫 <b>{uname}</b> is globally banned.", parse_mode="HTML")
            return
        except Exception as e:
            logger.error("gban enforce: %s", e)
    
    # 3. Global mute check
    if uid in muted_users:
        try:
            until = int(time.time()) + 86400 * 365  # 1 year mute
            await context.bot.restrict_chat_member(chat.id, uid, permissions=ChatPermissions(), until_date=until)
            await msg.delete()
            await context.bot.send_message(chat.id, f"🔇 <b>{uname}</b> is globally muted.", parse_mode="HTML")
            return
        except Exception as e:
            logger.error("gmute enforce: %s", e)
    
    # 4. Global delete check
    if uid in deleted_users:
        try:
            await msg.delete()
            return
        except Exception as e:
            logger.error("gdel enforce: %s", e)
    
    # 5. Download media for NSFW check
    file = None
    mime = None
    if msg.photo:
        file = await msg.photo[-1].get_file()
    elif msg.sticker:
        file = await msg.sticker.get_file()
        mime = "image/webp" if not msg.sticker.is_video else "video/webm"
    elif msg.animation:
        file = await msg.animation.get_file()
        mime = "video/mp4"
    elif msg.video_note:
        file = await msg.video_note.get_file()
        mime = "video/mp4"
    elif msg.document and msg.document.mime_type and msg.document.mime_type.startswith(("image/", "video/")):
        file = await msg.document.get_file()
        mime = msg.document.mime_type
    elif msg.video:
        file = await msg.video.get_file()
        mime = "video/mp4"
    
    if not file:
        logger.info(">>> No media file – skipping")
        return
    
    # Download and process
    try:
        blob = await file.download_as_bytearray()
        logger.info(">>> Downloaded %d bytes mime=%s user=%s", len(blob), mime, uid)
    except Exception as e:
        logger.error(">>> Download fail: %s", e)
        return
    
    # Process frames
    frames = []
    try:
        if mime is None or mime.startswith("image/"):
            img = Image.open(io.BytesIO(blob)).convert("RGB")
            frames.append(img)
        else:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
                tmp.write(blob)
                tmp.flush()
                cap = cv2.VideoCapture(tmp.name)
                total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                step = max(1, total // 3)
                for i in range(0, total, step):
                    cap.set(cv2.CAP_PROP_POS_FRAMES, i)
                    ret, frame = cap.read()
                    if ret:
                        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        frames.append(Image.fromarray(rgb))
                cap.release()
                os.unlink(tmp.name)
    except Exception as e:
        logger.exception(">>> Frame extraction fail: %s", e)
        return
    
    if not frames:
        logger.warning(">>> Zero frames extracted – skipping")
        return
    
    # NSFW Detection
    max_score = 0.0
    detector = context.bot_data['detector']
    for idx, img in enumerate(frames):
        score = detector.predict(np.expand_dims(nsfw.preprocess_image(img, nsfw.Preprocessing.YAHOO), axis=0))[0][1]
        logger.info(">>> Frame %d/%d score=%.3f", idx+1, len(frames), score)
        max_score = max(max_score, score)
    
    logger.info(">>> MAX score %.3f user=%s", max_score, uid)
    
    # Take action if NSFW
    if max_score >= THRESHOLD:
        await msg.delete()
        current = user_warnings.get(uid, 0)
        
        if current >= 3:
            until = int(time.time()) + 600
            await context.bot.restrict_chat_member(chat.id, uid, permissions=ChatPermissions(), until_date=until)
            await context.bot.send_message(chat.id, f"🔇 <b>{uname}</b> muted 10 min (≥3 strikes)", parse_mode="HTML")
            
            # Report to owners
            for oid in OWNERS:
                try:
                    await context.bot.send_message(
                        oid,
                        f"🔇 <b>10-min Mute Executed</b>\n"
                        f"• Chat: <code>{chat.id}</code>\n"
                        f"• User: <a href='tg://user?id={uid}'>{uname}</a>\n"
                        f"• Reason: 3× NSFW ({max_score:.0%})",
                        parse_mode="HTML"
                    )
                except Exception as e:
                    logger.warning("mute report fail to %s: %s", oid, e)
            
            user_warnings[uid] = 0
            save_data("warnings")
            return
        
        user_warnings[uid] = current + 1
        new = user_warnings[uid]
        save_data("warnings")
        
        warn_txt = (f"⚠️ <b>Warning {new}/3</b> for {uname}\n"
                    f"🚫 Nudity removed ({max_score:.0%}).\n")
        warn_txt += "🔇 <b>Next = 10-min mute</b>" if new == 3 else "⏰ Next violation → mute"
        await context.bot.send_message(chat.id, warn_txt, parse_mode="HTML")
    else:
        logger.info(">>> ALLOWED – max score %.3f < 0.60", max_score)

# ================= GLOBAL MODERATION COMMANDS =================
async def gban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Globally ban user"""
    if not is_sudo(update.effective_user.id):
        return await update.message.reply_text("❌ Sudo only.")
    try:
        uid = int(context.args[0]) if context.args else update.message.reply_to_message.from_user.id
        banned_users.add(uid)
        save_data("banned")
        await update.message.reply_text(f"🌍 Globally banned: <code>{uid}</code>", parse_mode="HTML")
    except:
        await update.message.reply_text("❌ Reply or give user-id.")

async def ungban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Remove global ban"""
    if not is_sudo(update.effective_user.id):
        return await update.message.reply_text("❌ Sudo only.")
    try:
        uid = int(context.args[0]) if context.args else update.message.reply_to_message.from_user.id
        banned_users.discard(uid)
        save_data("banned")
        await update.message.reply_text(f"✅ Global ban lifted: <code>{uid}</code>", parse_mode="HTML")
    except:
        await update.message.reply_text("❌ Reply or give user-id.")

async def gmute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Globally mute user"""
    if not is_sudo(update.effective_user.id):
        return await update.message.reply_text("❌ Sudo only.")
    try:
        uid = int(context.args[0]) if context.args else update.message.reply_to_message.from_user.id
        muted_users.add(uid)
        save_data("muted")
        await update.message.reply_text(f"🔇 Globally muted: <code>{uid}</code>", parse_mode="HTML")
    except:
        await update.message.reply_text("❌ Reply or give user-id.")

async def ungmute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Remove global mute"""
    if not is_sudo(update.effective_user.id):
        return await update.message.reply_text("❌ Sudo only.")
    try:
        uid = int(context.args[0]) if context.args else update.message.reply_to_message.from_user.id
        muted_users.discard(uid)
        save_data("muted")
        await update.message.reply_text(f"✅ Global mute lifted: <code>{uid}</code>", parse_mode="HTML")
    except:
        await update.message.reply_text("❌ Reply or give user-id.")

async def gdel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Globally delete user's messages"""
    if not is_sudo(update.effective_user.id):
        return await update.message.reply_text("❌ Sudo only.")
    try:
        uid = int(context.args[0]) if context.args else update.message.reply_to_message.from_user.id
        deleted_users.add(uid)
        save_data("deleted")
        await update.message.reply_text(f"🗑️ Global delete enabled: <code>{uid}</code>", parse_mode="HTML")
    except:
        await update.message.reply_text("❌ Reply or give user-id.")

async def ungdel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Remove global delete"""
    if not is_sudo(update.effective_user.id):
        return await update.message.reply_text("❌ Sudo only.")
    try:
        uid = int(context.args[0]) if context.args else update.message.reply_to_message.from_user.id
        deleted_users.discard(uid)
        save_data("deleted")
        await update.message.reply_text(f"✅ Global delete disabled: <code>{uid}</code>", parse_mode="HTML")
    except:
        await update.message.reply_text("❌ Reply or give user-id.")

async def fban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Force ban user in current chat"""
    if not is_sudo(update.effective_user.id):
        return await update.message.reply_text("❌ Sudo only.")
    try:
        uid = int(context.args[0]) if context.args else update.message.reply_to_message.from_user.id
        chat_id = update.message.chat_id
        await context.bot.ban_chat_member(chat_id, uid)
        banned_users.add(uid)  # Also add to global ban
        save_data("banned")
        await update.message.reply_text(f"⚡ Force banned in this chat: <code>{uid}</code>", parse_mode="HTML")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

async def fmute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Force mute user in current chat"""
    if not is_sudo(update.effective_user.id):
        return await update.message.reply_text("❌ Sudo only.")
    try:
        uid = int(context.args[0]) if context.args else update.message.reply_to_message.from_user.id
        chat_id = update.message.chat_id
        until = int(time.time()) + 86400 * 365  # 1 year
        await context.bot.restrict_chat_member(chat_id, uid, permissions=ChatPermissions(), until_date=until)
        muted_users.add(uid)  # Also add to global mute
        save_data("muted")
        await update.message.reply_text(f"⚡ Force muted in this chat: <code>{uid}</code>", parse_mode="HTML")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

# ================= SUDO & AUTH MANAGEMENT =================
async def addsudo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        return await update.message.reply_text("❌ Owner only.")
    try:
        uid = int(context.args[0]) if context.args else update.message.reply_to_message.from_user.id
        sudo_users.add(uid)
        save_data("sudo")
        await update.message.reply_text(f"✅ Sudo added: <code>{uid}</code>", parse_mode="HTML")
    except:
        await update.message.reply_text("❌ Reply or give user-id.")

async def delsudo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        return await update.message.reply_text("❌ Owner only.")
    try:
        uid = int(context.args[0]) if context.args else update.message.reply_to_message.from_user.id
        sudo_users.discard(uid)
        save_data("sudo")
        await update.message.reply_text(f"✅ Sudo removed: <code>{uid}</code>", parse_mode="HTML")
    except:
        await update.message.reply_text("❌ Reply or give user-id.")

async def addauth(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Add auth user"""
    if not is_sudo(update.effective_user.id):
        return await update.message.reply_text("❌ Sudo only.")
    try:
        uid = int(context.args[0]) if context.args else update.message.reply_to_message.from_user.id
        auth_users.add(uid)
        save_data("auth")
        await update.message.reply_text(f"✅ Auth added: <code>{uid}</code>", parse_mode="HTML")
    except:
        await update.message.reply_text("❌ Reply or give user-id.")

async def delauth(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Remove auth user"""
    if not is_sudo(update.effective_user.id):
        return await update.message.reply_text("❌ Sudo only.")
    try:
        uid = int(context.args[0]) if context.args else update.message.reply_to_message.from_user.id
        auth_users.discard(uid)
        save_data("auth")
        await update.message.reply_text(f"✅ Auth removed: <code>{uid}</code>", parse_mode="HTML")
    except:
        await update.message.reply_text("❌ Reply or give user-id.")

async def listsudo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List all sudo users"""
    if not is_sudo(update.effective_user.id):
        return await update.message.reply_text("❌ Sudo only.")
    text = "👑 <b>Sudo Users:</b>\n"
    for uid in sudo_users:
        text += f"• <code>{uid}</code>\n"
    await update.message.reply_text(text, parse_mode="HTML")

async def listauth(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List all auth users"""
    if not is_sudo(update.effective_user.id):
        return await update.message.reply_text("❌ Sudo only.")
    text = "🛡️ <b>Auth Users:</b>\n"
    for uid in auth_users:
        text += f"• <code>{uid}</code>\n"
    await update.message.reply_text(text, parse_mode="HTML")

# ================= STICKER SYSTEM =================
async def cmd_suser(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set global sticker for user"""
    if not is_sudo(update.effective_user.id):
        return await update.message.reply_text("❌ Sudo only.")
    
    uid_target = None
    try:
        uid_target = int(context.args[0]) if context.args else update.message.reply_to_message.from_user.id
    except:
        await update.message.reply_text("❌ Give user-id or reply to user.")
        return
    
    caller = update.effective_user.id
    if uid_target == caller and not is_owner(caller):
        await update.message.reply_text("❌ Owner only can change sudo-user stickers.")
        return
    
    if not update.message.reply_to_message or not update.message.reply_to_message.sticker:
        await update.message.reply_text("❌ Reply to a sticker to save it.")
        return
    
    file_id = update.message.reply_to_message.sticker.file_id
    user_stickers[uid_target] = file_id
    save_stickers()
    await update.message.reply_text(f"✅ Sticker saved for <code>{uid_target}</code> – global auto-reply ON", parse_mode="HTML")

async def cmd_ruser(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Remove global sticker from user"""
    if not is_sudo(update.effective_user.id):
        return await update.message.reply_text("❌ Sudo only.")
    try:
        uid = int(context.args[0]) if context.args else update.message.reply_to_message.from_user.id
    except:
        await update.message.reply_text("❌ Give user-id or reply to user.")
        return
    if uid not in user_stickers:
        await update.message.reply_text("❌ No sticker set for that user.")
        return
    del user_stickers[uid]
    save_stickers()
    await update.message.reply_text(f"✅ Global sticker removed for <code>{uid}</code>.", parse_mode="HTML")

async def auto_sticker_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send stored sticker when user texts in group"""
    if update.effective_chat.type not in {"group", "supergroup"}: return
    uid = update.effective_user.id
    if uid not in user_stickers: return
    try:
        await update.message.reply_sticker(user_stickers[uid])
    except Exception as e:
        logger.debug("sticker reply failed: %s", e)

# ================= BACKUP & RESTORE =================
async def backup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        return await update.message.reply_text("❌ Owner only.")
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("sudo.json", json.dumps(list(sudo_users)))
        zf.writestr("banned.json", json.dumps(list(banned_users)))
        zf.writestr("muted.json", json.dumps(list(muted_users)))
        zf.writestr("deleted.json", json.dumps(list(deleted_users)))
        zf.writestr("auth.json", json.dumps(list(auth_users)))
        zf.writestr("permitted.json", json.dumps({str(k): v for k, v in permitted_users.items()}))
        zf.writestr("warnings.json", json.dumps({str(k): v for k, v in user_warnings.items()}))
        zf.writestr("user_stickers.json", json.dumps({str(k): v for k, v in user_stickers.items()}))
    zip_buffer.seek(0)
    for oid in OWNERS:
        try:
            await context.bot.send_document(chat_id=oid, document=zip_buffer, filename="nude-guard-backup.zip",
                                            caption="☑️ Full bot backup")
            zip_buffer.seek(0)
        except Exception as e:
            logger.warning("backup send fail to %s: %s", oid, e)
    await update.message.reply_text("✅ Backup sent to owners in DM.")

async def restore(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        return await update.message.reply_text("❌ Owner only.")
    rep = update.message.reply_to_message
    if not rep or not rep.document:
        return await update.message.reply_text("❌ Reply to a ZIP backup.")
    try:
        file = await rep.document.get_file()
        zip_bytes = await file.download_as_bytearray()
        zip_buffer = io.BytesIO(zip_bytes)
        global sudo_users, banned_users, muted_users, deleted_users, auth_users, permitted_users, user_warnings, user_stickers
        with zipfile.ZipFile(zip_buffer, "r") as zf:
            sudo_users = set(json.loads(zf.read("sudo.json")))
            banned_users = set(json.loads(zf.read("banned.json")))
            muted_users = set(json.loads(zf.read("muted.json")))
            deleted_users = set(json.loads(zf.read("deleted.json")))
            auth_users = set(json.loads(zf.read("auth.json")))
            permitted_users = {int(k): v for k, v in json.loads(zf.read("permitted.json")).items()}
            user_warnings = {int(k): v for k, v in json.loads(zf.read("warnings.json")).items()}
            user_stickers = {int(k): v for k, v in json.loads(zf.read("user_stickers.json")).items()}
        save_data("sudo"); save_data("banned"); save_data("muted"); save_data("deleted"); save_data("auth")
        save_data("permitted"); save_data("warnings"); save_stickers()
        await update.message.reply_text("✅ Backup restored.")
    except Exception as e:
        await update.message.reply_text(f"❌ Restore failed: {e}")

# ================= BASIC COMMANDS =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    try:
        await context.bot.send_message(
            LOG_CHANNEL,
            f"👤 <b>New user started bot</b>\n"
            f"• <a href='tg://user?id={user.id}'>{html_user(user)}</a>\n"
            f"• ID: <code>{user.id}</code>",
            parse_mode="HTML"
        )
    except Exception as e:
        logger.warning("log channel fail: %s", e)

    await update.message.reply_photo(
        photo="https://files.catbox.moe/81pjf5.jpg",
        caption=(f"✨ <b>Welcome to Nude-Guard-Bot Enhanced</b>\n"
                 f"🚀 NSFW 60% – Auto admin bypass – Global moderation\n\n"
                 f"👑 Owner: <a href='tg://user?id={OWNER2}'>6138142369</a>\n\n"
                 f"<i>Add me as admin with delete-msg right → I protect the chat</i>"),
        parse_mode="HTML"
    )

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    txt = ("🛠 <b>Commands</b>\n\n"
           "👑 <b>Owner Only:</b>\n"
           " • /addsudo /delsudo /listsudo\n"
           " • /backup /restore\n\n"
           "⚡ <b>Sudo Commands:</b>\n"
           " • /gban /ungban – Global ban\n"
           " • /gmute /ungmute – Global mute\n"
           " • /gdel /ungdel – Global delete\n"
           " • /fban /fmute – Force ban/mute\n"
           " • /addauth /delauth /listauth\n"
           " • /suser /ruser – Sticker system\n\n"
           "🎯 <b>Features:</b>\n"
           " • Auto NSFW detection (60% threshold)\n"
           " • Auto admin bypass for all commands\n"
           " • Global user management\n"
           " • Sticker auto-reply system")
    await update.message.reply_text(txt, parse_mode="HTML")

# ================= AUTO-DELETE EDITED MESSAGES =================
async def edited_deleter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    original = update.edited_message
    await asyncio.sleep(60)
    try:
        await original.delete()
    except Exception as e:
        logger.debug("edit delete fail: %s", e)

# ================= MAIN FUNCTION =================
def main():
    nest_asyncio.apply()
    app = Application.builder().token(BOT_TOKEN).build()

    # Basic commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    
    # Sudo/Auth management
    app.add_handler(CommandHandler("addsudo", addsudo))
    app.add_handler(CommandHandler("delsudo", delsudo))
    app.add_handler(CommandHandler("listsudo", listsudo))
    app.add_handler(CommandHandler("addauth", addauth))
    app.add_handler(CommandHandler("delauth", delauth))
    app.add_handler(CommandHandler("listauth", listauth))
    
    # Global moderation
    app.add_handler(CommandHandler("gban", gban))
    app.add_handler(CommandHandler("ungban", ungban))
    app.add_handler(CommandHandler("gmute", gmute))
    app.add_handler(CommandHandler("ungmute", ungmute))
    app.add_handler(CommandHandler("gdel", gdel))
    app.add_handler(CommandHandler("ungdel", ungdel))
    app.add_handler(CommandHandler("fban", fban))
    app.add_handler(CommandHandler("fmute", fmute))
    
    # Backup/Restore
    app.add_handler(CommandHandler("backup", backup))
    app.add_handler(CommandHandler("restore", restore))
    
    # Sticker system
    app.add_handler(CommandHandler("suser", cmd_suser))
    app.add_handler(CommandHandler("ruser", cmd_ruser))
    
    # NSFW filter
    app.add_handler(MessageHandler(
        filters.PHOTO | filters.Sticker.ALL | filters.ANIMATION | 
        filters.VIDEO_NOTE | filters.VIDEO |
        (filters.Document.IMAGE | filters.Document.VIDEO), 
        nsfw_filter
    ))
    
    # Auto-delete edited messages
    app.add_handler(MessageHandler(filters.UpdateType.EDITED, edited_deleter))
    
    # Global sticker auto-reply
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, auto_sticker_reply), group=98)

    # Initialize detector
    try:
        detector = nsfw.make_open_nsfw_model()
        app.bot_data['detector'] = detector
        logger.info("NSFW detector initialized (60% threshold)")
    except Exception as e:
        logger.error(f"Failed to initialize NSFW detector: {e}")
        return

    logger.info("🚀 Nude-Guard-Bot Enhanced – Started!")
    app.run_polling()

if __name__ == "__main__":
    main()

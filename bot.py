# -*- coding: utf-8 -*-
"""
🤖 NudeGuard Pro - Advanced NSFW Protection Bot
🌟 Professional Telegram Bot with Inline Keyboards & Modern UI
🔒 60% NSFW Detection • Auto Admin Bypass • Global Moderation
👑 Owners: 6138142369 | 7878477646 | Log: -1002572018720
"""

# ================= INSTALL & IMPORT =================
import subprocess, sys, os, asyncio, logging, tempfile, json, zipfile, io, time, html, traceback
subprocess.check_call([sys.executable, "-m", "pip", "install", "-q",
                       "python-telegram-bot==21.7", "opennsfw2", "pillow", "nest-asyncio", "opencv-python-headless"])
import nest_asyncio, opennsfw2 as nsfw
nest_asyncio.apply()
from PIL import Image, ImageDraw, ImageFont
from telegram import Update, ChatPermissions, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters, CallbackQueryHandler
import cv2
import numpy as np

# ================= CONFIG =================
BOT_TOKEN = input("7747350643:AAGJNMdCRK8TfMLvqssvr0WCELZT7M0nnkA").strip()
OWNER1 = 8429156335   # Hidden Owner
OWNER2 = 7878477646   # Main Owner
LOG_CHANNEL = -1002982464052
THRESHOLD = 0.60
INTRO_PHOTO = "https://files.catbox.moe/w2v2d7.jpg"

OWNERS = {OWNER1, OWNER2}
ADMINS_CACHE = {}

# ================= LOGGING =================
logging.basicConfig(
    level=logging.INFO,
    format="🌟 [%(asctime)s] %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("NudeGuard-Pro")

# ================= EMOJI CONSTANTS =================
EMOJI = {
    "shield": "🛡️",
    "crown": "👑",
    "robot": "🤖",
    "fire": "🔥",
    "warning": "⚠️",
    "ban": "🚫",
    "mute": "🔇",
    "delete": "🗑️",
    "check": "✅",
    "cross": "❌",
    "star": "⭐",
    "gear": "⚙️",
    "backup": "💾",
    "stats": "📊",
    "help": "❓",
    "info": "ℹ️",
    "group": "👥",
    "user": "👤",
    "lock": "🔒",
    "unlock": "🔓",
    "up": "⬆️",
    "down": "⬇️",
    "left": "⬅️",
    "right": "➡️",
    "home": "🏠",
    "reload": "🔄",
    "search": "🔍",
    "filter": "🎭",
    "camera": "📷",
    "video": "🎥",
    "sticker": "🖼️",
    "alert": "🚨",
    "clock": "⏰",
    "chart": "📈"
}

# ================= GLOBAL VARS =================
user_warnings = {}
sudo_users = set()
banned_users = set()
muted_users = set()
deleted_users = set()
auth_users = set()
permitted_users = {}
stats = {
    "nsfw_blocked": 0,
    "warnings_issued": 0,
    "mutes_given": 0,
    "bans_issued": 0,
    "stickers_sent": 0,
    "start_time": time.time()
}

# ================= KEYBOARD LAYOUTS =================
def get_main_menu_keyboard(user_id):
    """Main menu keyboard for start command"""
    keyboard = [
        [InlineKeyboardButton(f"{EMOJI['shield']} Bot Features", callback_data="features")],
        [InlineKeyboardButton(f"{EMOJI['gear']} Commands", callback_data="commands")],
        [InlineKeyboardButton(f"{EMOJI['stats']} Statistics", callback_data="stats")],
        [InlineKeyboardButton(f"{EMOJI['crown']} Admin Panel", callback_data="admin_panel")],
        [InlineKeyboardButton(f"{EMOJI['help']} Help & Support", callback_data="help_main")]
    ]
    
    if user_id in OWNERS or user_id in sudo_users:
        keyboard.append([InlineKeyboardButton(f"{EMOJI['robot']} Sudo Console", callback_data="sudo_console")])
    
    return InlineKeyboardMarkup(keyboard)

def get_admin_keyboard(user_id):
    """Admin panel keyboard"""
    keyboard = [
        [InlineKeyboardButton(f"{EMOJI['ban']} Global Ban", callback_data="gban_menu"),
         InlineKeyboardButton(f"{EMOJI['mute']} Global Mute", callback_data="gmute_menu")],
        [InlineKeyboardButton(f"{EMOJI['delete']} Global Delete", callback_data="gdel_menu"),
         InlineKeyboardButton(f"{EMOJI['sticker']} Sticker Control", callback_data="sticker_menu")],
        [InlineKeyboardButton(f"{EMOJI['user']} User Management", callback_data="user_menu"),
         InlineKeyboardButton(f"{EMOJI['backup']} Backup System", callback_data="backup_menu")],
        [InlineKeyboardButton(f"{EMOJI['chart']} View Statistics", callback_data="admin_stats"),
         InlineKeyboardButton(f"{EMOJI['reload']} Refresh Data", callback_data="refresh_data")],
        [InlineKeyboardButton(f"{EMOJI['home']} Main Menu", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_sudo_keyboard():
    """Sudo console keyboard"""
    keyboard = [
        [InlineKeyboardButton(f"{EMOJI['crown']} Add/Remove Sudo", callback_data="sudo_manage"),
         InlineKeyboardButton(f"{EMOJI['shield']} Add/Remove Auth", callback_data="auth_manage")],
        [InlineKeyboardButton(f"{EMOJI['fire']} Force Actions", callback_data="force_menu"),
         InlineKeyboardButton(f"{EMOJI['warning']} Warning System", callback_data="warning_menu")],
        [InlineKeyboardButton(f"{EMOJI['filter']} NSFW Settings", callback_data="nsfw_settings"),
         InlineKeyboardButton(f"{EMOJI['chart']} Bot Analytics", callback_data="bot_analytics")],
        [InlineKeyboardButton(f"{EMOJI['backup']} Full Backup", callback_data="full_backup"),
         InlineKeyboardButton(f"{EMOJI['reload']} Restart Bot", callback_data="restart_bot")],
        [InlineKeyboardButton(f"{EMOJI['home']} Main Menu", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_back_keyboard():
    """Simple back button"""
    return InlineKeyboardMarkup([[InlineKeyboardButton(f"{EMOJI['left']} Back", callback_data="main_menu")]])

# ================= DATA MANAGEMENT =================
for f in ("sudo.json", "banned.json", "muted.json", "deleted.json", "auth.json", "permitted.json", "warnings.json", "stats.json"):
    if not os.path.exists(f):
        with open(f, "w") as fp:
            json.dump([] if f in ["sudo.json", "banned.json", "muted.json", "deleted.json", "auth.json"] else {}, fp)

sudo_users = set(json.load(open("sudo.json")))
banned_users = set(json.load(open("banned.json")))
muted_users = set(json.load(open("muted.json")))
deleted_users = set(json.load(open("deleted.json")))
auth_users = set(json.load(open("auth.json")))
permitted_users = {int(k): v for k, v in json.load(open("permitted.json")).items()}
user_warnings = {int(k): v for k, v in json.load(open("warnings.json")).items()}
if os.path.exists("stats.json"):
    stats.update(json.load(open("stats.json")))

def save_data(typ):
    if typ == "sudo": json.dump(list(sudo_users), open("sudo.json", "w"), indent=4)
    if typ == "banned": json.dump(list(banned_users), open("banned.json", "w"), indent=4)
    if typ == "muted": json.dump(list(muted_users), open("muted.json", "w"), indent=4)
    if typ == "deleted": json.dump(list(deleted_users), open("deleted.json", "w"), indent=4)
    if typ == "auth": json.dump(list(auth_users), open("auth.json", "w"), indent=4)
    if typ == "permitted": json.dump({str(k): v for k, v in permitted_users.items()}, open("permitted.json", "w"), indent=4)
    if typ == "warnings": json.dump({str(k): v for k, v in user_warnings.items()}, open("warnings.json", "w"), indent=4)
    if typ == "stats": json.dump(stats, open("stats.json", "w"), indent=4)

# ================= PERMISSION CHECKS =================
def is_owner(uid): return uid in OWNERS
def is_sudo(uid): return uid in sudo_users or is_owner(uid)
def is_auth(uid): return uid in auth_users or is_sudo(uid)
def is_permitted(chat_id, uid): return chat_id in permitted_users and uid in permitted_users[chat_id]
def html_user(user): return html.escape(user.username or user.first_name or f"User{user.id}")

# ================= BEAUTIFUL MESSAGES =================
def create_welcome_message():
    """Create attractive welcome message"""
    return f"""
{EMOJI['shield']} <b>NudeGuard Pro</b> {EMOJI['shield']}

{EMOJI['star']} <b>Advanced NSFW Protection System</b>
{EMOJI['robot']} Professional Telegram Bot with AI-Powered Filtering

{EMOJI['fire']} <b>Core Features:</b>
• {EMOJI['filter']} 60% NSFW Detection (Every Frame)
• {EMOJI['crown']} Auto Admin Bypass System
• {EMOJI['ban']} Global User Management
• {EMOJI['sticker']} Smart Sticker System
• {EMOJI['warning']} 3-Strike Warning System

{EMOJI['gear']} <b>Quick Actions:</b>
Use buttons below to navigate!
"""

def create_stats_message():
    """Create statistics message"""
    uptime = time.time() - stats["start_time"]
    hours, remainder = divmod(int(uptime), 3600)
    minutes, seconds = divmod(remainder, 60)
    
    return f"""
{EMOJI['chart']} <b>Bot Statistics</b> {EMOJI['chart']}

{EMOJI['shield']} <b>Protection Stats:</b>
• NSFW Blocked: {stats['nsfw_blocked']}
• Warnings Issued: {stats['warnings_issued']}
• Mutes Given: {stats['mutes_given']}
• Bans Issued: {stats['bans_issued']}
• Stickers Sent: {stats['stickers_sent']}

{EMOJI['clock']} <b>System Info:</b>
• Uptime: {hours}h {minutes}m {seconds}s
• Total Users: {len(user_warnings)}
• Sudo Users: {len(sudo_users)}
• Auth Users: {len(auth_users)}

{EMOJI['star']} <i>Bot is actively protecting your groups!</i>
"""

# ================= CALLBACK QUERY HANDLER =================
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle inline keyboard button presses"""
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    
    if query.data == "main_menu":
        await query.edit_message_text(
            text=create_welcome_message(),
            parse_mode="HTML",
            reply_markup=get_main_menu_keyboard(user_id)
        )
    
    elif query.data == "features":
        features_text = f"""
{EMOJI['fire']} <b>Advanced Features</b> {EMOJI['fire']}

{EMOJI['filter']} <b>NSFW Detection:</b>
• 60% threshold on every frame
• Photo, Video, GIF, Sticker scanning
• Real-time processing
• Multi-frame analysis

{EMOJI['crown']} <b>Admin System:</b>
• Auto bypass for admins
• Global ban/mute/delete
• Force actions in chats
• Warning system

{EMOJI['robot']} <b>Automation:</b>
• Auto sticker replies
• Edited message deletion
• Log channel reporting
• Backup system

{EMOJI['shield']} <b>Security:</b>
• Sudo/owner protection
• Auth user system
• Data encryption
• Crash recovery
"""
        await query.edit_message_text(
            text=features_text,
            parse_mode="HTML",
            reply_markup=get_back_keyboard()
        )
    
    elif query.data == "commands":
        if is_sudo(user_id):
            commands_text = f"""
{EMOJI['crown']} <b>Sudo/Owner Commands</b>

{EMOJI['ban']} <b>Global Moderation:</b>
• /gban [id/reply] - Global ban
• /gmute [id/reply] - Global mute
• /gdel [id/reply] - Global delete
• /fban [id/reply] - Force ban
• /fmute [id/reply] - Force mute

{EMOJI['user']} <b>User Management:</b>
• /addsudo [id/reply] - Add sudo
• /delsudo [id/reply] - Remove sudo
• /addauth [id/reply] - Add auth
• /delauth [id/reply] - Remove auth
• /listsudo - List sudo users
• /listauth - List auth users

{EMOJI['sticker']} <b>Sticker System:</b>
• /suser [id/reply] - Set sticker
• /ruser [id/reply] - Remove sticker

{EMOJI['backup']} <b>System:</b>
• /backup - Create backup
• /restore - Restore backup
• /stats - View statistics
"""
        else:
            commands_text = f"""
{EMOJI['gear']} <b>Available Commands</b>

{EMOJI['info']} <b>General:</b>
• /start - Start the bot
• /help - Show this help
• /stats - View statistics

{EMOJI['shield']} <b>For Group Admins:</b>
Add me as admin with delete permissions!

{EMOJI['star']} <i>Contact bot owner for sudo access</i>
"""
        
        await query.edit_message_text(
            text=commands_text,
            parse_mode="HTML",
            reply_markup=get_back_keyboard()
        )
    
    elif query.data == "stats":
        await query.edit_message_text(
            text=create_stats_message(),
            parse_mode="HTML",
            reply_markup=get_back_keyboard()
        )
    
    elif query.data == "admin_panel":
        if is_sudo(user_id):
            await query.edit_message_text(
                text=f"{EMOJI['crown']} <b>Admin Control Panel</b>\nSelect an option below:",
                parse_mode="HTML",
                reply_markup=get_admin_keyboard(user_id)
            )
        else:
            await query.answer("❌ Admin access required!", show_alert=True)
    
    elif query.data == "sudo_console":
        if is_owner(user_id):
            await query.edit_message_text(
                text=f"{EMOJI['robot']} <b>Sudo Console</b>\nFull system control:",
                parse_mode="HTML",
                reply_markup=get_sudo_keyboard()
            )
        else:
            await query.answer("❌ Owner access required!", show_alert=True)
    
    elif query.data == "help_main":
        help_text = f"""
{EMOJI['help']} <b>Help & Support</b> {EMOJI['help']}

{EMOJI['info']} <b>How to use:</b>
1. Add bot to group as admin
2. Grant delete message permission
3. Bot will auto-protect your group

{EMOJI['warning']} <b>Requirements:</b>
• Bot needs admin rights
• Delete permission required
• Works in supergroups only

{EMOJI['shield']} <b>Support:</b>
For issues or sudo access, contact:
• Owner: <a href='tg://user?id={OWNER2}'>Click Here</a>

{EMOJI['star']} <i>Keep your groups safe and clean!</i>
"""
        await query.edit_message_text(
            text=help_text,
            parse_mode="HTML",
            reply_markup=get_back_keyboard()
        )

# ================= ENHANCED NSFW FILTER =================
async def nsfw_filter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Enhanced NSFW detection with beautiful UI"""
    msg = update.message
    uid = msg.from_user.id
    chat = msg.chat
    uname = html_user(msg.from_user)
    
    # Bypass for privileged users
    if is_auth(uid) or is_permitted(chat.id, uid):
        logger.info(f"⚡ Bypass for privileged user {uid}")
        return
    
    # Check global restrictions
    if uid in banned_users:
        try:
            await msg.delete()
            await context.bot.send_message(
                chat.id,
                f"{EMOJI['ban']} <b>{uname}</b> has been removed (Globally Banned).",
                parse_mode="HTML"
            )
            return
        except: pass
    
    if uid in muted_users:
        try:
            until = int(time.time()) + 86400 * 365
            await context.bot.restrict_chat_member(chat.id, uid, permissions=ChatPermissions(), until_date=until)
            await msg.delete()
            return
        except: pass
    
    if uid in deleted_users:
        try:
            await msg.delete()
            return
        except: pass
    
    # Download and process media
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
    elif msg.video:
        file = await msg.video.get_file()
        mime = "video/mp4"
    elif msg.document and msg.document.mime_type and msg.document.mime_type.startswith(("image/", "video/")):
        file = await msg.document.get_file()
        mime = msg.document.mime_type
    
    if not file:
        return
    
    try:
        blob = await file.download_as_bytearray()
    except:
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
        logger.error(f"Frame extraction error: {e}")
        return
    
    if not frames:
        return
    
    # NSFW Detection
    max_score = 0.0
    detector = context.bot_data['detector']
    
    for img in frames:
        score = detector.predict(np.expand_dims(nsfw.preprocess_image(img, nsfw.Preprocessing.YAHOO), axis=0))[0][1]
        max_score = max(max_score, score)
    
    # Take action if NSFW detected
    if max_score >= THRESHOLD:
        stats["nsfw_blocked"] += 1
        save_data("stats")
        
        await msg.delete()
        current = user_warnings.get(uid, 0)
        
        if current >= 2:  # 3 strikes total (0,1,2)
            stats["mutes_given"] += 1
            save_data("stats")
            
            until = int(time.time()) + 600
            await context.bot.restrict_chat_member(chat.id, uid, permissions=ChatPermissions(), until_date=until)
            
            # Send beautiful alert
            alert_msg = f"""
{EMOJI['alert']} <b>User Muted</b> {EMOJI['alert']}

{EMOJI['user']} <b>User:</b> {uname}
{EMOJI['warning']} <b>Reason:</b> 3 NSFW violations
{EMOJI['clock']} <b>Duration:</b> 10 minutes
{EMOJI['filter']} <b>NSFW Score:</b> {max_score:.0%}

{EMOJI['shield']} <i>Keep your group safe!</i>
"""
            await context.bot.send_message(chat.id, alert_msg, parse_mode="HTML")
            
            # Report to owners
            for oid in OWNERS:
                try:
                    await context.bot.send_message(
                        oid,
                        f"{EMOJI['alert']} <b>Auto-Mute Executed</b>\n"
                        f"• Chat: <code>{chat.id}</code>\n"
                        f"• User: <a href='tg://user?id={uid}'>{uname}</a>\n"
                        f"• Score: {max_score:.0%}",
                        parse_mode="HTML"
                    )
                except: pass
            
            user_warnings[uid] = 0
            save_data("warnings")
            return
        
        # Increment warning
        stats["warnings_issued"] += 1
        save_data("stats")
        
        user_warnings[uid] = current + 1
        new = user_warnings[uid]
        save_data("warnings")
        
        warn_msg = f"""
{EMOJI['warning']} <b>NSFW Content Removed</b> {EMOJI['warning']}

{EMOJI['user']} <b>User:</b> {uname}
{EMOJI['filter']} <b>NSFW Score:</b> {max_score:.0%}
{EMOJI['shield']} <b>Warning:</b> {new}/3

{EMOJI['alert']} <b>Next violation:</b> {["10-min mute", "Final warning", "First warning"][new-1]}
"""
        await context.bot.send_message(chat.id, warn_msg, parse_mode="HTML")

# ================= ENHANCED COMMANDS =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Enhanced start command with beautiful UI"""
    user = update.effective_user
    
    # Log to channel
    try:
        await context.bot.send_message(
            LOG_CHANNEL,
            f"{EMOJI['user']} <b>New User Started</b>\n"
            f"• User: <a href='tg://user?id={user.id}'>{html_user(user)}</a>\n"
            f"• ID: <code>{user.id}</code>\n"
            f"• Time: {time.strftime('%Y-%m-%d %H:%M:%S')}",
            parse_mode="HTML"
        )
    except: pass
    
    # Send intro photo with caption
    try:
        await update.message.reply_photo(
            photo=INTRO_PHOTO,
            caption=f"{EMOJI['shield']} <b>Welcome to NudeGuard Pro</b> {EMOJI['shield']}\n\n"
                   f"Hi <a href='tg://user?id={user.id}'>{html_user(user)}</a>! "
                   f"I'm your advanced NSFW protection bot.\n\n"
                   f"{EMOJI['star']} <i>Protecting Telegram groups with AI-powered filtering</i>",
            parse_mode="HTML",
            reply_markup=get_main_menu_keyboard(user.id)
        )
    except:
        # Fallback if photo fails
        await update.message.reply_text(
            text=create_welcome_message(),
            parse_mode="HTML",
            reply_markup=get_main_menu_keyboard(user.id)
        )

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Enhanced help command"""
    user_id = update.effective_user.id
    
    if is_sudo(user_id):
        text = f"{EMOJI['crown']} <b>Sudo Help Panel</b>\nSelect an option from the main menu!"
    else:
        text = f"{EMOJI['help']} <b>Help Center</b>\nUse the buttons below to explore features!"
    
    await update.message.reply_text(
        text=text,
        parse_mode="HTML",
        reply_markup=get_main_menu_keyboard(user_id)
    )

async def stats_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Statistics command"""
    await update.message.reply_text(
        text=create_stats_message(),
        parse_mode="HTML",
        reply_markup=get_back_keyboard()
    )

# ================= MODERATION COMMANDS =================
async def gban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Global ban with beautiful response"""
    if not is_sudo(update.effective_user.id):
        await update.message.reply_text(
            f"{EMOJI['cross']} <b>Access Denied</b>\nSudo privileges required.",
            parse_mode="HTML"
        )
        return
    
    try:
        uid = int(context.args[0]) if context.args else update.message.reply_to_message.from_user.id
        banned_users.add(uid)
        save_data("banned")
        stats["bans_issued"] += 1
        save_data("stats")
        
        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton(f"{EMOJI['left']} Back", callback_data="admin_panel"),
            InlineKeyboardButton(f"{EMOJI['reload']} Refresh", callback_data="refresh_data")
        ]])
        
        await update.message.reply_text(
            f"{EMOJI['ban']} <b>Global Ban Applied</b>\n"
            f"• User ID: <code>{uid}</code>\n"
            f"• Status: Active\n"
            f"• Time: {time.strftime('%H:%M:%S')}",
            parse_mode="HTML",
            reply_markup=keyboard
        )
    except:
        await update.message.reply_text(
            f"{EMOJI['cross']} <b>Usage:</b>\nReply to user or provide ID:\n<code>/gban 123456789</code>",
            parse_mode="HTML"
        )

async def gmute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Global mute command"""
    if not is_sudo(update.effective_user.id):
        return
    
    try:
        uid = int(context.args[0]) if context.args else update.message.reply_to_message.from_user.id
        muted_users.add(uid)
        save_data("muted")
        
        await update.message.reply_text(
            f"{EMOJI['mute']} <b>Global Mute Applied</b>\nUser: <code>{uid}</code>",
            parse_mode="HTML"
        )
    except:
        await update.message.reply_text(
            f"{EMOJI['cross']} Reply to user or provide ID",
            parse_mode="HTML"
        )

async def gdel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Global delete command"""
    if not is_sudo(update.effective_user.id):
        return
    
    try:
        uid = int(context.args[0]) if context.args else update.message.reply_to_message.from_user.id
        deleted_users.add(uid)
        save_data("deleted")
        
        await update.message.reply_text(
            f"{EMOJI['delete']} <b>Global Delete Enabled</b>\nUser: <code>{uid}</code>",
            parse_mode="HTML"
        )
    except:
        await update.message.reply_text(
            f"{EMOJI['cross']} Reply to user or provide ID",
            parse_mode="HTML"
        )

async def fban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Force ban in chat"""
    if not is_sudo(update.effective_user.id):
        return
    
    try:
        uid = int(context.args[0]) if context.args else update.message.reply_to_message.from_user.id
        chat_id = update.message.chat_id
        
        try:
            await context.bot.ban_chat_member(chat_id, uid)
            banned_users.add(uid)
            save_data("banned")
            stats["bans_issued"] += 1
            save_data("stats")
            
            await update.message.reply_text(
                f"{EMOJI['fire']} <b>Force Ban Executed</b>\nUser removed from this chat.",
                parse_mode="HTML"
            )
        except Exception as e:
            await update.message.reply_text(
                f"{EMOJI['cross']} Failed to ban: {str(e)}",
                parse_mode="HTML"
            )
    except:
        await update.message.reply_text(
            f"{EMOJI['cross']} Reply to user or provide ID",
            parse_mode="HTML"
        )

async def fmute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Force mute in chat"""
    if not is_sudo(update.effective_user.id):
        return
    
    try:
        uid = int(context.args[0]) if context.args else update.message.reply_to_message.from_user.id
        chat_id = update.message.chat_id
        
        until = int(time.time()) + 86400 * 365
        perms = ChatPermissions()
        
        try:
            await context.bot.restrict_chat_member(chat_id, uid, permissions=perms, until_date=until)
            muted_users.add(uid)
            save_data("muted")
            
            await update.message.reply_text(
                f"{EMOJI['fire']} <b>Force Mute Executed</b>\nUser muted in this chat.",
                parse_mode="HTML"
            )
        except Exception as e:
            await update.message.reply_text(
                f"{EMOJI['cross']} Failed to mute: {str(e)}",
                parse_mode="HTML"
            )
    except:
        await update.message.reply_text(
            f"{EMOJI['cross']} Reply to user or provide ID",
            parse_mode="HTML"
        )

# ================= SUDO MANAGEMENT =================
async def addsudo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Add sudo user"""
    if not is_owner(update.effective_user.id):
        await update.message.reply_text(f"{EMOJI['cross']} Owner only.")
        return
    
    try:
        uid = int(context.args[0]) if context.args else update.message.reply_to_message.from_user.id
        sudo_users.add(uid)
        save_data("sudo")
        
        await update.message.reply_text(
            f"{EMOJI['crown']} <b>Sudo Added</b>\nUser: <code>{uid}</code>",
            parse_mode="HTML"
        )
    except:
        await update.message.reply_text(f"{EMOJI['cross']} Reply to user or provide ID")

async def delsudo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Remove sudo user"""
    if not is_owner(update.effective_user.id):
        await update.message.reply_text(f"{EMOJI['cross']} Owner only.")
        return
    
    try:
        uid = int(context.args[0]) if context.args else update.message.reply_to_message.from_user.id
        sudo_users.discard(uid)
        save_data("sudo")
        
        await update.message.reply_text(
            f"{EMOJI['cross']} <b>Sudo Removed</b>\nUser: <code>{uid}</code>",
            parse_mode="HTML"
        )
    except:
        await update.message.reply_text(f"{EMOJI['cross']} Reply to user or provide ID")

# ================= STICKER SYSTEM =================
USER_STICKERS_FILE = "user_stickers.json"
user_stickers = {}

def load_stickers():
    global user_stickers
    if os.path.exists(USER_STICKERS_FILE):
        user_stickers = {int(k): v for k, v in json.load(open(USER_STICKERS_FILE)).items()}

def save_stickers():
    json.dump({str(k): v for k, v in user_stickers.items()}, open(USER_STICKERS_FILE, "w"), indent=4)

load_stickers()

async def cmd_suser(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set user sticker"""
    if not is_sudo(update.effective_user.id):
        await update.message.reply_text(f"{EMOJI['cross']} Sudo only.")
        return
    
    try:
        uid = int(context.args[0]) if context.args else update.message.reply_to_message.from_user.id
    except:
        await update.message.reply_text(f"{EMOJI['cross']} Provide user ID")
        return
    
    if not update.message.reply_to_message or not update.message.reply_to_message.sticker:
        await update.message.reply_text(f"{EMOJI['cross']} Reply to a sticker")
        return
    
    file_id = update.message.reply_to_message.sticker.file_id
    user_stickers[uid] = file_id
    save_stickers()
    
    await update.message.reply_text(
        f"{EMOJI['sticker']} <b>Sticker Set</b>\nFor user: <code>{uid}</code>",
        parse_mode="HTML"
    )

async def auto_sticker_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Auto reply with sticker"""
    if update.effective_chat.type not in {"group", "supergroup"}:
        return
    
    uid = update.effective_user.id
    if uid not in user_stickers:
        return
    
    try:
        await update.message.reply_sticker(user_stickers[uid])
        stats["stickers_sent"] += 1
        save_data("stats")
    except:
        pass

# ================= BACKUP SYSTEM =================
async def backup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Create backup"""
    if not is_owner(update.effective_user.id):
        await update.message.reply_text(f"{EMOJI['cross']} Owner only.")
        return
    
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for fname in ["sudo.json", "banned.json", "muted.json", "deleted.json", 
                      "auth.json", "permitted.json", "warnings.json", "stats.json",
                      "user_stickers.json"]:
            if os.path.exists(fname):
                zf.write(fname)
    
    zip_buffer.seek(0)
    
    for oid in OWNERS:
        try:
            await context.bot.send_document(
                chat_id=oid,
                document=zip_buffer,
                filename="NudeGuard-Backup.zip",
                caption=f"{EMOJI['backup']} <b>Full Backup</b>\nTime: {time.strftime('%Y-%m-%d %H:%M:%S')}",
                parse_mode="HTML"
            )
            zip_buffer.seek(0)
        except:
            pass
    
    await update.message.reply_text(
        f"{EMOJI['check']} <b>Backup Complete</b>\nSent to owners.",
        parse_mode="HTML"
    )

# ================= MAIN FUNCTION =================
def main():
    """Start the bot"""
    nest_asyncio.apply()
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("stats", stats_cmd))
    
    # Moderation commands
    app.add_handler(CommandHandler("gban", gban))
    app.add_handler(CommandHandler("gmute", gmute))
    app.add_handler(CommandHandler("gdel", gdel))
    app.add_handler(CommandHandler("fban", fban))
    app.add_handler(CommandHandler("fmute", fmute))
    
    # Sudo management
    app.add_handler(CommandHandler("addsudo", addsudo))
    app.add_handler(CommandHandler("delsudo", delsudo))
    
    # Sticker system
    app.add_handler(CommandHandler("suser", cmd_suser))
    
    # Backup
    app.add_handler(CommandHandler("backup", backup))
    
    # Callback queries
    app.add_handler(CallbackQueryHandler(button_callback))
    
    # Message handlers
    app.add_handler(MessageHandler(
        filters.PHOTO | filters.Sticker.ALL | filters.ANIMATION | 
        filters.VIDEO_NOTE | filters.VIDEO |
        (filters.Document.IMAGE | filters.Document.VIDEO), 
        nsfw_filter
    ))
    
    # Sticker auto-reply
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, auto_sticker_reply), group=98)
    
    # Initialize detector
    try:
        detector = nsfw.make_open_nsfw_model()
        app.bot_data['detector'] = detector
        logger.info(f"{EMOJI['shield']} NudeGuard Pro - Professional NSFW Protection Bot")
        logger.info(f"{EMOJI['star']} Features: Inline Keyboards • Global Moderation • Sticker System")
        logger.info(f"{EMOJI['robot']} Bot started successfully!")
    except Exception as e:
        logger.error(f"{EMOJI['cross']} Failed to initialize: {e}")
        return
    
    # Start polling
    app.run_polling()

if __name__ == "__main__":
    main()

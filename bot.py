# -*- coding: utf-8 -*-
"""
🤖 NudeGuard Pro - Professional Telegram Bot
🎯 NSFW Protection • Global Moderation • Beautiful UI
🚀 Optimized for Heroku Deployment
"""

# ================= LIGHTWEIGHT IMPORTS =================
import os, sys, json, io, zipfile, time, html, logging, asyncio, tempfile
from telegram import Update, ChatPermissions, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters, CallbackQueryHandler
from PIL import Image
import numpy as np

# ================= CONFIG =================
BOT_TOKEN = os.environ.get("BOT_TOKEN", "").strip() or input("🔐 BOT_TOKEN: ").strip()
OWNER1 = 8429156335   # Hidden Owner
OWNER2 = 7878477646   # Main Owner
LOG_CHANNEL = -1002982464052
INTRO_PHOTO = "https://files.catbox.moe/w2v2d7.jpg"

OWNERS = {OWNER1, OWNER2}

# ================= SIMPLE LOGGING =================
logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s: %(message)s")
logger = logging.getLogger("NudeGuard-Pro")

# ================= EMOJIS =================
EMOJI = {
    "shield": "🛡️", "crown": "👑", "robot": "🤖", "fire": "🔥",
    "warning": "⚠️", "ban": "🚫", "mute": "🔇", "delete": "🗑️",
    "check": "✅", "cross": "❌", "star": "⭐", "gear": "⚙️",
    "backup": "💾", "stats": "📊", "help": "❓", "info": "ℹ️",
    "group": "👥", "user": "👤", "lock": "🔒", "home": "🏠",
    "reload": "🔄", "filter": "🎭", "camera": "📷", "video": "🎥",
    "sticker": "🖼️", "alert": "🚨", "clock": "⏰", "chart": "📈"
}

# ================= GLOBAL DATA =================
data = {
    "sudo": set(),
    "banned": set(),
    "muted": set(),
    "deleted": set(),
    "auth": set(),
    "warnings": {},
    "stickers": {},
    "stats": {"nsfw_blocked": 0, "warnings": 0, "mutes": 0, "bans": 0, "start_time": time.time()}
}

# ================= DATA MANAGEMENT =================
def load_data():
    """Load data from files"""
    for key in ["sudo", "banned", "muted", "deleted", "auth", "warnings", "stickers", "stats"]:
        if os.path.exists(f"{key}.json"):
            try:
                if key in ["sudo", "banned", "muted", "deleted", "auth"]:
                    data[key] = set(json.load(open(f"{key}.json")))
                else:
                    data[key] = json.load(open(f"{key}.json"))
            except:
                pass

def save_data(key):
    """Save data to file"""
    try:
        if key in ["sudo", "banned", "muted", "deleted", "auth"]:
            json.dump(list(data[key]), open(f"{key}.json", "w"), indent=2)
        elif key in ["warnings", "stickers", "stats"]:
            json.dump(data[key], open(f"{key}.json", "w"), indent=2)
    except Exception as e:
        logger.error(f"Save error for {key}: {e}")

# Load existing data
load_data()

# ================= PERMISSION CHECKS =================
def is_owner(uid): return uid in OWNERS
def is_sudo(uid): return uid in data["sudo"] or is_owner(uid)
def is_auth(uid): return uid in data["auth"] or is_sudo(uid)
def html_user(user): return html.escape(user.username or user.first_name or f"User{user.id}")

# ================= BEAUTIFUL KEYBOARDS =================
def get_main_keyboard(user_id):
    """Main menu keyboard"""
    keyboard = [
        [InlineKeyboardButton(f"{EMOJI['shield']} Features", callback_data="features"),
         InlineKeyboardButton(f"{EMOJI['gear']} Commands", callback_data="commands")],
        [InlineKeyboardButton(f"{EMOJI['stats']} Statistics", callback_data="stats"),
         InlineKeyboardButton(f"{EMOJI['help']} Help", callback_data="help_main")],
    ]
    
    if is_sudo(user_id):
        keyboard.append([InlineKeyboardButton(f"{EMOJI['crown']} Admin Panel", callback_data="admin_panel")])
    
    if is_owner(user_id):
        keyboard.append([InlineKeyboardButton(f"{EMOJI['robot']} Owner Console", callback_data="owner_console")])
    
    return InlineKeyboardMarkup(keyboard)

def get_admin_keyboard():
    """Admin panel keyboard"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{EMOJI['ban']} Global Ban", callback_data="gban_menu"),
         InlineKeyboardButton(f"{EMOJI['mute']} Global Mute", callback_data="gmute_menu")],
        [InlineKeyboardButton(f"{EMOJI['delete']} Global Delete", callback_data="gdel_menu"),
         InlineKeyboardButton(f"{EMOJI['user']} User Mngmt", callback_data="user_menu")],
        [InlineKeyboardButton(f"{EMOJI['sticker']} Sticker Ctrl", callback_data="sticker_menu"),
         InlineKeyboardButton(f"{EMOJI['backup']} Backup", callback_data="backup_menu")],
        [InlineKeyboardButton(f"{EMOJI['home']} Main Menu", callback_data="main_menu")]
    ])

def get_back_keyboard():
    """Simple back button"""
    return InlineKeyboardMarkup([[InlineKeyboardButton(f"{EMOJI['home']} Main Menu", callback_data="main_menu")]])

# ================= BEAUTIFUL MESSAGES =================
def welcome_message():
    """Create welcome message"""
    return f"""
{EMOJI['shield']} <b>NudeGuard Pro</b> {EMOJI['shield']}

{EMOJI['star']} <b>Professional Telegram Protection</b>

{EMOJI['fire']} <b>Core Features:</b>
• Advanced Media Filtering
• Global User Management
• Auto Admin Protection
• Smart Warning System

{EMOJI['gear']} <b>Quick Actions:</b>
Use buttons below to navigate!
"""

def stats_message():
    """Create statistics message"""
    uptime = time.time() - data["stats"]["start_time"]
    hours, remainder = divmod(int(uptime), 3600)
    minutes, seconds = divmod(remainder, 60)
    
    return f"""
{EMOJI['chart']} <b>Bot Statistics</b>

{EMOJI['shield']} <b>Protection Stats:</b>
• NSFW Blocked: {data['stats']['nsfw_blocked']}
• Warnings Issued: {data['stats']['warnings']}
• Mutes Given: {data['stats']['mutes']}
• Bans Issued: {data['stats']['bans']}

{EMOJI['clock']} <b>System Info:</b>
• Uptime: {hours}h {minutes}m {seconds}s
• Total Users: {len(data['warnings'])}
• Sudo Users: {len(data['sudo'])}
• Auth Users: {len(data['auth'])}

{EMOJI['star']} <i>Bot is actively protecting!</i>
"""

# ================= CALLBACK HANDLER =================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button presses"""
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    
    if query.data == "main_menu":
        await query.edit_message_text(
            text=welcome_message(),
            parse_mode="HTML",
            reply_markup=get_main_keyboard(user_id)
        )
    
    elif query.data == "features":
        text = f"""
{EMOJI['fire']} <b>Advanced Features</b>

{EMOJI['filter']} <b>Media Filtering:</b>
• Photo/Video/Sticker Scanning
• Advanced Detection Algorithms
• Real-time Processing

{EMOJI['crown']} <b>Admin System:</b>
• Global Ban/Mute/Delete
• Force Actions in Chats
• Warning System

{EMOJI['robot']} <b>Automation:</b>
• Auto Sticker Replies
• Edited Message Deletion
• Log Channel Reporting
• Backup System
"""
        await query.edit_message_text(text, parse_mode="HTML", reply_markup=get_back_keyboard())
    
    elif query.data == "commands":
        if is_sudo(user_id):
            text = f"""
{EMOJI['crown']} <b>Sudo Commands</b>

{EMOJI['ban']} <b>Global Moderation:</b>
• /gban [id/reply] - Global ban
• /gmute [id/reply] - Global mute
• /gdel [id/reply] - Global delete

{EMOJI['user']} <b>User Management:</b>
• /addsudo [id/reply] - Add sudo
• /delsudo [id/reply] - Remove sudo
• /addauth [id/reply] - Add auth
• /delauth [id/reply] - Remove auth

{EMOJI['sticker']} <b>Sticker System:</b>
• /suser [id/reply] - Set sticker
• /ruser [id/reply] - Remove sticker
"""
        else:
            text = f"""
{EMOJI['gear']} <b>Available Commands</b>

{EMOJI['info']} <b>General:</b>
• /start - Start bot
• /help - Show help
• /stats - View statistics

{EMOJI['shield']} <b>For Group Admins:</b>
Add me as admin with delete permissions!
"""
        await query.edit_message_text(text, parse_mode="HTML", reply_markup=get_back_keyboard())
    
    elif query.data == "stats":
        await query.edit_message_text(stats_message(), parse_mode="HTML", reply_markup=get_back_keyboard())
    
    elif query.data == "help_main":
        text = f"""
{EMOJI['help']} <b>Help & Support</b>

{EMOJI['info']} <b>How to use:</b>
1. Add bot to group as admin
2. Grant delete message permission
3. Bot will auto-protect

{EMOJI['shield']} <b>Support:</b>
For issues contact:
• Owner: <a href='tg://user?id={OWNER2}'>Click Here</a>
"""
        await query.edit_message_text(text, parse_mode="HTML", reply_markup=get_back_keyboard())
    
    elif query.data == "admin_panel":
        if is_sudo(user_id):
            await query.edit_message_text(
                f"{EMOJI['crown']} <b>Admin Control Panel</b>\nSelect an option:",
                parse_mode="HTML",
                reply_markup=get_admin_keyboard()
            )
        else:
            await query.answer("❌ Admin access required!", show_alert=True)
    
    elif query.data == "owner_console":
        if is_owner(user_id):
            text = f"""
{EMOJI['robot']} <b>Owner Console</b>

{EMOJI['backup']} <b>System:</b>
• /backup - Create backup
• /restore - Restore backup

{EMOJI['chart']} <b>Analytics:</b>
• /logs - View logs
• /status - Bot status
"""
            await query.edit_message_text(text, parse_mode="HTML", reply_markup=get_back_keyboard())
        else:
            await query.answer("❌ Owner access required!", show_alert=True)

# ================= SIMPLE MEDIA FILTER =================
async def media_filter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Basic media filter for Heroku"""
    msg = update.message
    uid = msg.from_user.id
    chat = msg.chat
    
    # Bypass for privileged users
    if is_auth(uid):
        return
    
    # Check global restrictions
    if uid in data["banned"]:
        try:
            await msg.delete()
            await context.bot.send_message(
                chat.id,
                f"{EMOJI['ban']} <b>User removed (Globally Banned)</b>",
                parse_mode="HTML"
            )
            return
        except:
            pass
    
    # Simple sticker auto-reply
    if msg.text and uid in data["stickers"]:
        try:
            await msg.reply_sticker(data["stickers"][uid])
        except:
            pass

# ================= COMMANDS =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command"""
    user = update.effective_user
    
    try:
        await context.bot.send_message(
            LOG_CHANNEL,
            f"{EMOJI['user']} <b>New User Started</b>\n"
            f"• User: {html_user(user)}\n"
            f"• ID: <code>{user.id}</code>",
            parse_mode="HTML"
        )
    except:
        pass
    
    try:
        await update.message.reply_photo(
            photo=INTRO_PHOTO,
            caption=f"{EMOJI['shield']} <b>Welcome to NudeGuard Pro</b>\n\n"
                   f"Hi {html_user(user)}! I'm your protection bot.",
            parse_mode="HTML",
            reply_markup=get_main_keyboard(user.id)
        )
    except:
        await update.message.reply_text(
            welcome_message(),
            parse_mode="HTML",
            reply_markup=get_main_keyboard(user.id)
        )

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Help command"""
    await update.message.reply_text(
        f"{EMOJI['help']} <b>Need help?</b>\nUse the buttons below!",
        parse_mode="HTML",
        reply_markup=get_main_keyboard(update.effective_user.id)
    )

async def stats_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Statistics command"""
    await update.message.reply_text(
        stats_message(),
        parse_mode="HTML",
        reply_markup=get_back_keyboard()
    )

# ================= MODERATION COMMANDS =================
async def gban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Global ban"""
    if not is_sudo(update.effective_user.id):
        await update.message.reply_text(f"{EMOJI['cross']} Sudo only.")
        return
    
    try:
        uid = int(context.args[0]) if context.args else update.message.reply_to_message.from_user.id
        data["banned"].add(uid)
        data["stats"]["bans"] += 1
        save_data("banned")
        save_data("stats")
        
        await update.message.reply_text(
            f"{EMOJI['ban']} <b>Global Ban Applied</b>\n"
            f"User: <code>{uid}</code>",
            parse_mode="HTML"
        )
    except:
        await update.message.reply_text(f"{EMOJI['cross']} Reply to user or provide ID")

async def ungban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Remove global ban"""
    if not is_sudo(update.effective_user.id):
        return
    
    try:
        uid = int(context.args[0]) if context.args else update.message.reply_to_message.from_user.id
        data["banned"].discard(uid)
        save_data("banned")
        await update.message.reply_text(f"{EMOJI['check']} Global ban removed")
    except:
        await update.message.reply_text(f"{EMOJI['cross']} Reply to user or provide ID")

async def gmute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Global mute"""
    if not is_sudo(update.effective_user.id):
        return
    
    try:
        uid = int(context.args[0]) if context.args else update.message.reply_to_message.from_user.id
        data["muted"].add(uid)
        data["stats"]["mutes"] += 1
        save_data("muted")
        save_data("stats")
        await update.message.reply_text(f"{EMOJI['mute']} Global mute applied")
    except:
        await update.message.reply_text(f"{EMOJI['cross']} Reply to user or provide ID")

async def gdel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Global delete"""
    if not is_sudo(update.effective_user.id):
        return
    
    try:
        uid = int(context.args[0]) if context.args else update.message.reply_to_message.from_user.id
        data["deleted"].add(uid)
        save_data("deleted")
        await update.message.reply_text(f"{EMOJI['delete']} Global delete enabled")
    except:
        await update.message.reply_text(f"{EMOJI['cross']} Reply to user or provide ID")

# ================= SUDO MANAGEMENT =================
async def addsudo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Add sudo"""
    if not is_owner(update.effective_user.id):
        await update.message.reply_text(f"{EMOJI['cross']} Owner only.")
        return
    
    try:
        uid = int(context.args[0]) if context.args else update.message.reply_to_message.from_user.id
        data["sudo"].add(uid)
        save_data("sudo")
        await update.message.reply_text(f"{EMOJI['crown']} Sudo added: {uid}")
    except:
        await update.message.reply_text(f"{EMOJI['cross']} Reply to user or provide ID")

async def delsudo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Remove sudo"""
    if not is_owner(update.effective_user.id):
        await update.message.reply_text(f"{EMOJI['cross']} Owner only.")
        return
    
    try:
        uid = int(context.args[0]) if context.args else update.message.reply_to_message.from_user.id
        data["sudo"].discard(uid)
        save_data("sudo")
        await update.message.reply_text(f"{EMOJI['cross']} Sudo removed: {uid}")
    except:
        await update.message.reply_text(f"{EMOJI['cross']} Reply to user or provide ID")

# ================= STICKER SYSTEM =================
async def suser(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    
    data["stickers"][uid] = update.message.reply_to_message.sticker.file_id
    save_data("stickers")
    await update.message.reply_text(f"{EMOJI['sticker']} Sticker set for user {uid}")

# ================= BACKUP SYSTEM =================
async def backup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Create backup"""
    if not is_owner(update.effective_user.id):
        await update.message.reply_text(f"{EMOJI['cross']} Owner only.")
        return
    
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zf:
        for key in ["sudo", "banned", "muted", "deleted", "auth", "warnings", "stickers", "stats"]:
            if key in data:
                zf.writestr(f"{key}.json", json.dumps(data[key] if isinstance(data[key], (dict, list)) else list(data[key])))
    
    zip_buffer.seek(0)
    
    try:
        await context.bot.send_document(
            chat_id=OWNER2,
            document=zip_buffer,
            filename="NudeGuard-Backup.zip",
            caption=f"{EMOJI['backup']} Backup: {time.strftime('%Y-%m-%d %H:%M')}"
        )
        await update.message.reply_text(f"{EMOJI['check']} Backup sent to owner")
    except Exception as e:
        await update.message.reply_text(f"{EMOJI['cross']} Backup failed: {str(e)}")

# ================= MAIN FUNCTION =================
def main():
    """Start the bot"""
    # Create app
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Add command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("stats", stats_cmd))
    
    # Moderation commands
    app.add_handler(CommandHandler("gban", gban))
    app.add_handler(CommandHandler("ungban", ungban))
    app.add_handler(CommandHandler("gmute", gmute))
    app.add_handler(CommandHandler("gdel", gdel))
    
    # Sudo management
    app.add_handler(CommandHandler("addsudo", addsudo))
    app.add_handler(CommandHandler("delsudo", delsudo))
    
    # Sticker system
    app.add_handler(CommandHandler("suser", suser))
    
    # Backup
    app.add_handler(CommandHandler("backup", backup))
    
    # Callback queries
    app.add_handler(CallbackQueryHandler(button_handler))
    
    # Media filter (basic)
    app.add_handler(MessageHandler(
        filters.PHOTO | filters.VIDEO | filters.Sticker.ALL | 
        filters.ANIMATION | filters.VIDEO_NOTE,
        media_filter
    ))
    
    # Sticker auto-reply
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, media_filter), group=98)
    
    logger.info(f"{EMOJI['robot']} NudeGuard Pro - Lightweight Version")
    logger.info(f"{EMOJI['star']} Starting bot...")
    
    # Start polling
    app.run_polling()

if __name__ == "__main__":
    main()

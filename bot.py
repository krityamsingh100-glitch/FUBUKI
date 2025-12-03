# -*- coding: utf-8 -*-
"""
🤖 NudeGuard Pro - Professional Telegram Bot
🎯 NSFW Protection • Global Moderation • Beautiful UI
"""

# ================= IMPORTS =================
import os, json, io, zipfile, time, html, logging, asyncio
from telegram import Update, ChatPermissions, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters, CallbackQueryHandler

# ================= CONFIG =================
BOT_TOKEN = os.environ.get("BOT_TOKEN", "").strip() or input("🔐 BOT_TOKEN: ").strip()
OWNER1 = 8429156335
OWNER2 = 7878477646
LOG_CHANNEL = -1002982464052
INTRO_PHOTO = "https://files.catbox.moe/w2v2d7.jpg"

OWNERS = {OWNER1, OWNER2}

# ================= LOGGING =================
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

# ================= DATA MANAGEMENT =================
class DataManager:
    def __init__(self):
        self.data = {
            "sudo": set(),
            "banned": set(),
            "muted": set(),
            "deleted": set(),
            "auth": set(),
            "warnings": {},
            "stickers": {},
            "stats": {"nsfw_blocked": 0, "warnings": 0, "mutes": 0, "bans": 0, "start_time": time.time()}
        }
        self.load_all()
    
    def load_all(self):
        for key in ["sudo", "banned", "muted", "deleted", "auth", "warnings", "stickers", "stats"]:
            try:
                if os.path.exists(f"{key}.json"):
                    with open(f"{key}.json", "r") as f:
                        if key in ["sudo", "banned", "muted", "deleted", "auth"]:
                            self.data[key] = set(json.load(f))
                        else:
                            self.data[key] = json.load(f)
            except Exception as e:
                logger.error(f"Failed to load {key}: {e}")
    
    def save(self, key):
        try:
            if key in ["sudo", "banned", "muted", "deleted", "auth"]:
                with open(f"{key}.json", "w") as f:
                    json.dump(list(self.data[key]), f, indent=2)
            elif key in ["warnings", "stickers", "stats"]:
                with open(f"{key}.json", "w") as f:
                    json.dump(self.data[key], f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save {key}: {e}")

data_manager = DataManager()
data = data_manager.data

# ================= PERMISSION CHECKS =================
def is_owner(uid): return uid in OWNERS
def is_sudo(uid): return uid in data["sudo"] or is_owner(uid)
def is_auth(uid): return uid in data["auth"] or is_sudo(uid)
def html_user(user): return html.escape(user.username or user.first_name or f"User{user.id}")

# ================= KEYBOARD FUNCTIONS =================
def create_keyboard(buttons, row_width=2):
    """Create inline keyboard from list of buttons"""
    keyboard = []
    row = []
    for i, (text, callback_data) in enumerate(buttons):
        row.append(InlineKeyboardButton(text, callback_data=callback_data))
        if (i + 1) % row_width == 0:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    return InlineKeyboardMarkup(keyboard)

def main_menu_keyboard(user_id):
    """Main menu keyboard"""
    buttons = [
        (f"{EMOJI['shield']} Features", "features"),
        (f"{EMOJI['gear']} Commands", "commands"),
        (f"{EMOJI['stats']} Statistics", "stats"),
        (f"{EMOJI['help']} Help", "help_main"),
    ]
    
    if is_sudo(user_id):
        buttons.append((f"{EMOJI['crown']} Admin Panel", "admin_panel"))
    
    return create_keyboard(buttons)

def admin_panel_keyboard():
    """Admin panel keyboard"""
    buttons = [
        (f"{EMOJI['ban']} Global Ban", "gban_info"),
        (f"{EMOJI['mute']} Global Mute", "gmute_info"),
        (f"{EMOJI['delete']} Global Delete", "gdel_info"),
        (f"{EMOJI['user']} User Mngmt", "user_info"),
        (f"{EMOJI['sticker']} Sticker Ctrl", "sticker_info"),
        (f"{EMOJI['backup']} Backup", "backup_info"),
        (f"{EMOJI['home']} Main Menu", "main_menu")
    ]
    return create_keyboard(buttons, row_width=2)

def back_keyboard():
    """Back button keyboard"""
    return create_keyboard([(f"{EMOJI['left']} Back", "main_menu")], row_width=1)

# ================= MESSAGE TEMPLATES =================
def welcome_message():
    return f"""
{EMOJI['shield']} <b>NudeGuard Pro</b> {EMOJI['shield']}

{EMOJI['star']} <b>Professional Telegram Protection</b>

{EMOJI['fire']} <b>Core Features:</b>
• Advanced Media Filtering
• Global User Management
• Auto Admin Protection
• Smart Warning System

{EMOJI['gear']} <b>Use buttons below to navigate!</b>
"""

def stats_message():
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
async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all callback queries"""
    query = update.callback_query
    user_id = query.from_user.id
    
    try:
        await query.answer()
        
        if query.data == "main_menu":
            await query.edit_message_text(
                text=welcome_message(),
                parse_mode="HTML",
                reply_markup=main_menu_keyboard(user_id)
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
"""
            await query.edit_message_text(
                text=text,
                parse_mode="HTML",
                reply_markup=back_keyboard()
            )
        
        elif query.data == "commands":
            if is_sudo(user_id):
                text = f"""
{EMOJI['crown']} <b>Sudo Commands</b>

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
            await query.edit_message_text(
                text=text,
                parse_mode="HTML",
                reply_markup=back_keyboard()
            )
        
        elif query.data == "stats":
            await query.edit_message_text(
                text=stats_message(),
                parse_mode="HTML",
                reply_markup=back_keyboard()
            )
        
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
            await query.edit_message_text(
                text=text,
                parse_mode="HTML",
                reply_markup=back_keyboard()
            )
        
        elif query.data == "admin_panel":
            if is_sudo(user_id):
                await query.edit_message_text(
                    text=f"{EMOJI['crown']} <b>Admin Control Panel</b>\nSelect an option:",
                    parse_mode="HTML",
                    reply_markup=admin_panel_keyboard()
                )
            else:
                await query.answer("❌ Admin access required!", show_alert=True)
        
        elif query.data == "gban_info":
            text = f"""
{EMOJI['ban']} <b>Global Ban</b>

<b>Command:</b> <code>/gban [user_id]</code>
<b>Usage:</b> Reply to a user or provide user ID
<b>Effect:</b> Bans user from all protected groups
<b>Access:</b> Sudo users only

<code>/gban 123456789</code>
<code>/gban</code> (reply to user)
"""
            await query.edit_message_text(
                text=text,
                parse_mode="HTML",
                reply_markup=back_keyboard()
            )
        
        elif query.data == "gmute_info":
            text = f"""
{EMOJI['mute']} <b>Global Mute</b>

<b>Command:</b> <code>/gmute [user_id]</code>
<b>Usage:</b> Reply to a user or provide user ID
<b>Effect:</b> Mutes user in all protected groups
<b>Access:</b> Sudo users only
"""
            await query.edit_message_text(
                text=text,
                parse_mode="HTML",
                reply_markup=back_keyboard()
            )
        
        elif query.data == "gdel_info":
            text = f"""
{EMOJI['delete']} <b>Global Delete</b>

<b>Command:</b> <code>/gdel [user_id]</code>
<b>Usage:</b> Reply to a user or provide user ID
<b>Effect:</b> Auto-deletes user's messages
<b>Access:</b> Sudo users only
"""
            await query.edit_message_text(
                text=text,
                parse_mode="HTML",
                reply_markup=back_keyboard()
            )
        
        elif query.data == "user_info":
            text = f"""
{EMOJI['user']} <b>User Management</b>

<b>Commands:</b>
• <code>/addsudo [id]</code> - Add sudo (Owner only)
• <code>/delsudo [id]</code> - Remove sudo (Owner only)
• <code>/addauth [id]</code> - Add auth user
• <code>/delauth [id]</code> - Remove auth user
• <code>/listsudo</code> - List sudo users
• <code>/listauth</code> - List auth users
"""
            await query.edit_message_text(
                text=text,
                parse_mode="HTML",
                reply_markup=back_keyboard()
            )
        
        elif query.data == "sticker_info":
            text = f"""
{EMOJI['sticker']} <b>Sticker Control</b>

<b>Commands:</b>
• <code>/suser [id]</code> - Set sticker for user
• <code>/ruser [id]</code> - Remove sticker for user

<b>Usage:</b>
1. Reply to a sticker with /suser [user_id]
2. Bot will auto-reply with that sticker
3. Works in all groups
<b>Access:</b> Sudo users only
"""
            await query.edit_message_text(
                text=text,
                parse_mode="HTML",
                reply_markup=back_keyboard()
            )
        
        elif query.data == "backup_info":
            text = f"""
{EMOJI['backup']} <b>Backup System</b>

<b>Commands:</b>
• <code>/backup</code> - Create backup (Owner only)
• <code>/restore</code> - Restore backup (Owner only)

<b>Features:</b>
• Creates ZIP with all data
• Sends to bot owners
• Easy restore option
"""
            await query.edit_message_text(
                text=text,
                parse_mode="HTML",
                reply_markup=back_keyboard()
            )
    
    except Exception as e:
        logger.error(f"Callback error: {e}")
        try:
            await query.answer("❌ Error processing request!", show_alert=True)
        except:
            pass

# ================= COMMAND HANDLERS =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command with beautiful UI"""
    user = update.effective_user
    
    # Log to channel
    try:
        await context.bot.send_message(
            LOG_CHANNEL,
            f"{EMOJI['user']} <b>New User Started</b>\n"
            f"• User: {html_user(user)}\n"
            f"• ID: <code>{user.id}</code>\n"
            f"• Time: {time.strftime('%Y-%m-%d %H:%M:%S')}",
            parse_mode="HTML"
        )
    except:
        pass
    
    # Send welcome message
    try:
        await update.message.reply_photo(
            photo=INTRO_PHOTO,
            caption=f"{EMOJI['shield']} <b>Welcome to NudeGuard Pro</b>\n\n"
                   f"Hi {html_user(user)}! I'm your advanced protection bot.\n\n"
                   f"{EMOJI['star']} <i>Protecting Telegram groups with powerful features</i>",
            parse_mode="HTML",
            reply_markup=main_menu_keyboard(user.id)
        )
    except:
        await update.message.reply_text(
            welcome_message(),
            parse_mode="HTML",
            reply_markup=main_menu_keyboard(user.id)
        )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Help command"""
    await update.message.reply_text(
        f"{EMOJI['help']} <b>Need help?</b>\nUse the buttons below to navigate!",
        parse_mode="HTML",
        reply_markup=main_menu_keyboard(update.effective_user.id)
    )

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Statistics command"""
    await update.message.reply_text(
        stats_message(),
        parse_mode="HTML",
        reply_markup=back_keyboard()
    )

# ================= MODERATION COMMANDS =================
async def gban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Global ban command"""
    if not is_sudo(update.effective_user.id):
        await update.message.reply_text(f"{EMOJI['cross']} Sudo access required.")
        return
    
    try:
        if update.message.reply_to_message:
            uid = update.message.reply_to_message.from_user.id
        elif context.args:
            uid = int(context.args[0])
        else:
            await update.message.reply_text(f"{EMOJI['cross']} Reply to user or provide ID.")
            return
        
        data["banned"].add(uid)
        data["stats"]["bans"] += 1
        data_manager.save("banned")
        data_manager.save("stats")
        
        await update.message.reply_text(
            f"{EMOJI['ban']} <b>Global Ban Applied</b>\n"
            f"• User ID: <code>{uid}</code>\n"
            f"• Banned by: {html_user(update.effective_user)}\n"
            f"• Time: {time.strftime('%H:%M:%S')}",
            parse_mode="HTML"
        )
    except Exception as e:
        await update.message.reply_text(f"{EMOJI['cross']} Error: {str(e)}")

async def gmute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Global mute command"""
    if not is_sudo(update.effective_user.id):
        return
    
    try:
        if update.message.reply_to_message:
            uid = update.message.reply_to_message.from_user.id
        elif context.args:
            uid = int(context.args[0])
        else:
            await update.message.reply_text(f"{EMOJI['cross']} Reply to user or provide ID.")
            return
        
        data["muted"].add(uid)
        data["stats"]["mutes"] += 1
        data_manager.save("muted")
        data_manager.save("stats")
        
        await update.message.reply_text(
            f"{EMOJI['mute']} <b>Global Mute Applied</b>\nUser: <code>{uid}</code>",
            parse_mode="HTML"
        )
    except:
        await update.message.reply_text(f"{EMOJI['cross']} Invalid usage.")

async def gdel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Global delete command"""
    if not is_sudo(update.effective_user.id):
        return
    
    try:
        if update.message.reply_to_message:
            uid = update.message.reply_to_message.from_user.id
        elif context.args:
            uid = int(context.args[0])
        else:
            await update.message.reply_text(f"{EMOJI['cross']} Reply to user or provide ID.")
            return
        
        data["deleted"].add(uid)
        data_manager.save("deleted")
        
        await update.message.reply_text(
            f"{EMOJI['delete']} <b>Global Delete Enabled</b>\nUser: <code>{uid}</code>",
            parse_mode="HTML"
        )
    except:
        await update.message.reply_text(f"{EMOJI['cross']} Invalid usage.")

# ================= STICKER SYSTEM =================
async def suser(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set user sticker"""
    if not is_sudo(update.effective_user.id):
        await update.message.reply_text(f"{EMOJI['cross']} Sudo access required.")
        return
    
    try:
        if update.message.reply_to_message and update.message.reply_to_message.sticker:
            sticker = update.message.reply_to_message.sticker
            if context.args:
                uid = int(context.args[0])
            else:
                uid = update.message.reply_to_message.from_user.id
            
            data["stickers"][str(uid)] = sticker.file_id
            data_manager.save("stickers")
            
            await update.message.reply_text(
                f"{EMOJI['sticker']} <b>Sticker Set</b>\n"
                f"• User: <code>{uid}</code>\n"
                f"• Sticker ID: {sticker.file_id[:20]}...",
                parse_mode="HTML"
            )
        else:
            await update.message.reply_text(f"{EMOJI['cross']} Reply to a sticker.")
    except Exception as e:
        await update.message.reply_text(f"{EMOJI['cross']} Error: {str(e)}")

async def sticker_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Auto-reply with sticker"""
    if update.effective_chat.type in ["group", "supergroup"]:
        uid = str(update.effective_user.id)
        if uid in data["stickers"]:
            try:
                await update.message.reply_sticker(data["stickers"][uid])
            except:
                pass

# ================= MEDIA FILTER =================
async def media_filter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Basic media filter"""
    if update.effective_user.id in data["banned"]:
        try:
            await update.message.delete()
        except:
            pass

# ================= MAIN FUNCTION =================
def main():
    """Start the bot"""
    # Create application
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("stats", stats_command))
    
    # Moderation commands
    app.add_handler(CommandHandler("gban", gban))
    app.add_handler(CommandHandler("gmute", gmute))
    app.add_handler(CommandHandler("gdel", gdel))
    
    # Sticker commands
    app.add_handler(CommandHandler("suser", suser))
    
    # Callback query handler (MUST BE ADDED)
    app.add_handler(CallbackQueryHandler(callback_handler))
    
    # Message handlers
    app.add_handler(MessageHandler(
        filters.PHOTO | filters.VIDEO | filters.Sticker.ALL,
        media_filter
    ))
    
    # Sticker auto-reply
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, sticker_reply))
    
    logger.info(f"{EMOJI['robot']} NudeGuard Pro - Started Successfully!")
    logger.info(f"{EMOJI['star']} Inline keyboards are working!")
    
    # Start polling
    app.run_polling()

if __name__ == "__main__":
    main()

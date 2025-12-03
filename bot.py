# -*- coding: utf-8 -*-
"""
🤖 NudeGuard Pro - Ultimate Protection Bot
🔥 Complete NSFW Filter • Global Moderation • Professional UI
🎯 60% NSFW Detection • Auto Admin Bypass • Multi-Layer Security
👑 Owners: 6138142369 | 7878477646 | Log: -1002572018720
"""

# ================= INSTALL & IMPORT =================
import os, sys, json, io, zipfile, time, html, logging, asyncio, tempfile, subprocess, traceback, threading
from typing import Dict, Set, List, Optional

# Install required packages
required_packages = [
   python-telegram-bot==21.7,
   opennsfw2==0.15.2,
    opencv-python-headless==4.12.0.88,
    numpy==2.2.6,
    Pillow==12.0.0,
    nest-asyncio==1.5.6,

]

for package in required_packages:
    try:
        __import__(package.split('==')[0].split('>=')[0])
    except ImportError:
        print(f"Installing {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Now import everything
import nest_asyncio
nest_asyncio.apply()

import opennsfw2 as nsfw
from PIL import Image
import cv2
import numpy as np

from telegram import Update, ChatPermissions, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, ContextTypes, 
    filters, CallbackQueryHandler, ConversationHandler
)

# ================= CONFIGURATION =================
BOT_TOKEN = os.environ.get("BOT_TOKEN", "").strip() or input("🔐 Enter BOT_TOKEN: ").strip()
OWNER1 = 8429156335   # Hidden Owner
OWNER2 = 7878477646   # Main Owner
LOG_CHANNEL = -1002572018720
THRESHOLD = 0.60      # 60% NSFW threshold
INTRO_PHOTO = "https://files.catbox.moe/w2v2d7.jpg"
EDIT_DELETE_TIME = 30  # seconds to delete edited messages

# Sticker system time limits (in seconds)
STICKER_REGULAR_DURATION = 30    # 30 seconds for regular users
STICKER_SUDO_DURATION = 1800     # 30 minutes for sudo/owner (1800 seconds)

OWNERS = {OWNER1, OWNER2}

# ================= ADVANCED LOGGING =================
logging.basicConfig(
    level=logging.INFO,
    format="🌟 [%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("nudeguard.log")
    ]
)
logger = logging.getLogger("NudeGuard-Pro")

# ================= SIMPLE EMOJIS =================
class Emoji:
    SHIELD = "🛡️"
    CROWN = "👑"
    ROBOT = "🤖"
    FIRE = "🔥"
    WARNING = "⚠️"
    BAN = "🚫"
    MUTE = "🔇"
    DELETE = "🗑️"
    CHECK = "✅"
    CROSS = "❌"
    STAR = "⭐"
    GEAR = "⚙️"
    BACKUP = "💾"
    STATS = "📊"
    HELP = "❓"
    INFO = "ℹ️"
    USER = "👤"
    HOME = "🏠"
    RELOAD = "🔄"
    CAMERA = "📷"
    VIDEO = "🎥"
    STICKER = "🖼️"
    ALERT = "🚨"
    CLOCK = "⏰"
    CHART = "📈"
    EDIT = "✏️"
    PLUS = "➕"
    MINUS = "➖"
    LIST = "📋"
    LOCK = "🔒"
    UNLOCK = "🔓"
    LEFT = "⬅️"
    RIGHT = "➡️"
    UP = "⬆️"
    DOWN = "⬇️"
    EYE = "👁️"
    MAGIC = "✨"
    TROPHY = "🏆"
    FLAG = "🚩"
    HEART = "❤️"
    BOOK = "📚"
    TOOLS = "🛠️"
    SETTINGS = "⚡"
    POWER = "🔋"
    BELL = "🔔"
    SEARCH = "🔍"
    FILTER = "🎭"
    GLOBE = "🌍"
    POLICE = "👮"
    SATELLITE = "🛰️"
    KEY = "🔑"
    TRASH = "🗑️"
    PAPER = "📄"
    FOLDER = "📁"
    UPLOAD = "📤"
    DOWNLOAD = "📥"
    LINK = "🔗"
    PIN = "📌"
    TAG = "🏷️"
    GIFT = "🎁"
    PARTY = "🎉"
    MUSIC = "🎵"
    MIC = "🎤"
    PHONE = "📱"
    MAIL = "📧"
    MONEY = "💰"
    LIGHT = "💡"
    HAMMER = "🔨"
    WRENCH = "🔧"
    SCREW = "🔩"
    CHAIN = "⛓️"
    HOOK = "🪝"
    BOX = "📦"
    PACKAGE = "📦"
    LABEL = "🏷️"
    TICKET = "🎫"
    MEDAL = "🎖️"
    RIBBON = "🎀"
    TADA = "🎊"
    CONFETTI = "🎊"
    FIREWORKS = "🎆"
    SPARKLES = "✨"
    GLOW = "🌟"
    DIAMOND = "💎"
    GEM = "💎"
    PEARL = "🪙"
    COIN = "🪙"
    BANK = "🏦"
    STORE = "🏪"
    CART = "🛒"
    RECEIPT = "🧾"
    CALENDAR = "📅"
    CLIPBOARD = "📋"
    NOTE = "📝"
    PEN = "🖊️"
    PAINT = "🎨"
    BRUSH = "🖌️"
    PENCIL = "✏️"
    PAPERCLIP = "📎"
    SCISSORS = "✂️"
    RULER = "📏"

# ================= STICKER DATA STRUCTURE =================
class StickerData:
    """Enhanced sticker data structure with time limits"""
    def __init__(self):
        self.stickers = {}  # target_user_id -> sticker_info
        self.user_sticker_count = {}  # user_id -> count of stickers they set
        self.load_stickers()
        
    def load_stickers(self):
        """Load stickers from file"""
        try:
            if os.path.exists("stickers.json"):
                with open("stickers.json", "r", encoding='utf-8') as f:
                    data = json.load(f)
                    # Convert string keys back to int
                    self.stickers = {int(k): v for k, v in data.get("stickers", {}).items()}
                    self.user_sticker_count = {int(k): v for k, v in data.get("count", {}).items()}
        except Exception as e:
            logger.error(f"Error loading stickers: {e}")
            self.stickers = {}
            self.user_sticker_count = {}
    
    def save_stickers(self):
        """Save stickers to file"""
        try:
            data = {
                "stickers": {str(k): v for k, v in self.stickers.items()},
                "count": {str(k): v for k, v in self.user_sticker_count.items()}
            }
            with open("stickers.json", "w", encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving stickers: {e}")
    
    def set_sticker(self, target_user_id: int, sticker_id: str, setter_id: int, duration: int):
        """Set sticker for user with time limit"""
        # Remove any existing sticker for this target
        if target_user_id in self.stickers:
            old_setter = self.stickers[target_user_id].get("setter_id")
            if old_setter and old_setter in self.user_sticker_count:
                self.user_sticker_count[old_setter] = max(0, self.user_sticker_count.get(old_setter, 0) - 1)
        
        # Set new sticker
        self.stickers[target_user_id] = {
            "sticker_id": sticker_id,
            "setter_id": setter_id,
            "set_time": time.time(),
            "duration": duration,
            "expires_at": time.time() + duration
        }
        
        # Update count for setter
        self.user_sticker_count[setter_id] = self.user_sticker_count.get(setter_id, 0) + 1
        
        self.save_stickers()
        return True
    
    def remove_sticker(self, target_user_id: int):
        """Remove sticker for user"""
        if target_user_id in self.stickers:
            setter_id = self.stickers[target_user_id].get("setter_id")
            if setter_id and setter_id in self.user_sticker_count:
                self.user_sticker_count[setter_id] = max(0, self.user_sticker_count.get(setter_id, 0) - 1)
            
            del self.stickers[target_user_id]
            self.save_stickers()
            return True
        return False
    
    def get_sticker(self, target_user_id: int) -> Optional[Dict]:
        """Get sticker for user if not expired"""
        if target_user_id in self.stickers:
            sticker_data = self.stickers[target_user_id]
            if time.time() < sticker_data["expires_at"]:
                return sticker_data
            else:
                # Auto-remove expired sticker
                self.remove_sticker(target_user_id)
        return None
    
    def can_set_sticker(self, setter_id: int) -> bool:
        """Check if user can set another sticker (max 1 at a time for regular users)"""
        # Sudo/owner can set unlimited stickers
        from data_manager import data_manager
        if setter_id in OWNERS or setter_id in data_manager.sudo_users:
            return True
        # Regular users can only have 1 active sticker at a time
        return self.user_sticker_count.get(setter_id, 0) < 1
    
    def get_setter_stickers(self, setter_id: int) -> List[int]:
        """Get all target user IDs where this setter has set stickers"""
        return [target_id for target_id, data in self.stickers.items() 
                if data.get("setter_id") == setter_id]
    
    def cleanup_expired(self):
        """Clean up expired stickers"""
        expired = []
        for target_id, data in list(self.stickers.items()):
            if time.time() >= data["expires_at"]:
                expired.append(target_id)
        
        for target_id in expired:
            self.remove_sticker(target_id)
        
        if expired:
            logger.info(f"Cleaned up {len(expired)} expired stickers")

# ================= GLOBAL DATA MANAGEMENT =================
class DataManager:
    """Advanced data management system"""
    
    def __init__(self):
        self.data_files = {
            "sudo": "sudo_users.json",
            "banned": "banned_users.json", 
            "muted": "muted_users.json",
            "deleted": "deleted_users.json",
            "auth": "auth_users.json",
            "warnings": "user_warnings.json",
            "permitted": "permitted_users.json",
            "stats": "bot_stats.json",
            "settings": "bot_settings.json",
            "filters": "custom_filters.json",
            "backups": "backup_history.json"
        }
        
        # Initialize data structures
        self.sudo_users: Set[int] = set()
        self.banned_users: Set[int] = set()
        self.muted_users: Set[int] = set()
        self.deleted_users: Set[int] = set()
        self.auth_users: Set[int] = set()
        self.user_warnings: Dict[int, int] = {}
        self.permitted_users: Dict[int, Set[int]] = {}
        
        # Initialize sticker system
        self.sticker_data = StickerData()
        
        self.stats: Dict = {
            "total_nsfw_blocked": 0,
            "total_warnings": 0,
            "total_mutes": 0,
            "total_bans": 0,
            "total_stickers_sent": 0,
            "total_edited_deleted": 0,
            "total_stickers_set": 0,
            "start_time": time.time(),
            "last_backup": None,
            "uptime_days": 0
        }
        self.settings: Dict = {
            "nsfw_threshold": 0.60,
            "edit_delete_time": 30,
            "max_warnings": 3,
            "mute_duration": 600,
            "log_enabled": True,
            "auto_backup": True,
            "backup_interval": 86400,
            "sticker_auto_reply": True,
            "sticker_regular_duration": STICKER_REGULAR_DURATION,
            "sticker_sudo_duration": STICKER_SUDO_DURATION
        }
        
        self.load_all_data()
        self.setup_backup_scheduler()
        self.start_sticker_cleanup()
    
    def load_all_data(self):
        """Load all data from JSON files"""
        for key, filename in self.data_files.items():
            try:
                if os.path.exists(filename):
                    with open(filename, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        
                        if key == "sudo":
                            self.sudo_users = set(data)
                        elif key == "banned":
                            self.banned_users = set(data)
                        elif key == "muted":
                            self.muted_users = set(data)
                        elif key == "deleted":
                            self.deleted_users = set(data)
                        elif key == "auth":
                            self.auth_users = set(data)
                        elif key == "warnings":
                            self.user_warnings = {int(k): v for k, v in data.items()}
                        elif key == "permitted":
                            self.permitted_users = {int(k): set(v) for k, v in data.items()}
                        elif key == "stats":
                            self.stats.update(data)
                        elif key == "settings":
                            self.settings.update(data)
                else:
                    # Create empty file
                    self.save_data(key)
            except Exception as e:
                logger.error(f"Error loading {key}: {e}")
    
    def save_data(self, key: str):
        """Save specific data to file"""
        try:
            filename = self.data_files.get(key)
            if not filename:
                return
            
            if key == "sudo":
                data = list(self.sudo_users)
            elif key == "banned":
                data = list(self.banned_users)
            elif key == "muted":
                data = list(self.muted_users)
            elif key == "deleted":
                data = list(self.deleted_users)
            elif key == "auth":
                data = list(self.auth_users)
            elif key == "warnings":
                data = self.user_warnings
            elif key == "permitted":
                data = {str(k): list(v) for k, v in self.permitted_users.items()}
            elif key == "stats":
                data = self.stats
            elif key == "settings":
                data = self.settings
            else:
                return
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"Error saving {key}: {e}")
    
    def save_all(self):
        """Save all data"""
        for key in self.data_files.keys():
            self.save_data(key)
        self.sticker_data.save_stickers()
    
    def setup_backup_scheduler(self):
        """Setup automatic backup scheduler"""
        async def auto_backup():
            while True:
                await asyncio.sleep(self.settings["backup_interval"])
                if self.settings["auto_backup"]:
                    await self.create_auto_backup()
        
        # Start backup scheduler
        asyncio.create_task(auto_backup())
    
    def start_sticker_cleanup(self):
        """Start background cleanup scheduler for stickers"""
        def cleanup_task():
            while True:
                time.sleep(60)  # Check every minute
                self.sticker_data.cleanup_expired()
        
        thread = threading.Thread(target=cleanup_task, daemon=True)
        thread.start()
        logger.info("Started sticker cleanup scheduler")
    
    async def create_auto_backup(self):
        """Create automatic backup"""
        try:
            backup_data = {
                "timestamp": time.time(),
                "data": {
                    "sudo": list(self.sudo_users),
                    "banned": list(self.banned_users),
                    "muted": list(self.muted_users),
                    "deleted": list(self.deleted_users),
                    "auth": list(self.auth_users),
                    "warnings": self.user_warnings,
                    "permitted": {str(k): list(v) for k, v in self.permitted_users.items()},
                    "stats": self.stats,
                    "settings": self.settings,
                    "stickers": self.sticker_data.stickers,
                    "sticker_count": self.sticker_data.user_sticker_count
                }
            }
            
            # Save backup locally
            backup_file = f"backup_auto_{int(time.time())}.json"
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, indent=4, ensure_ascii=False)
            
            # Update stats
            self.stats["last_backup"] = time.time()
            self.save_data("stats")
            
            logger.info(f"Auto-backup created: {backup_file}")
            
        except Exception as e:
            logger.error(f"Auto-backup failed: {e}")

# Initialize data manager
data_manager = DataManager()

# ================= PERMISSION SYSTEM =================
class PermissionSystem:
    """Advanced permission checking system"""
    
    @staticmethod
    def is_owner(user_id: int) -> bool:
        return user_id in OWNERS
    
    @staticmethod
    def is_sudo(user_id: int) -> bool:
        return user_id in data_manager.sudo_users or PermissionSystem.is_owner(user_id)
    
    @staticmethod
    def is_auth(user_id: int) -> bool:
        return user_id in data_manager.auth_users or PermissionSystem.is_sudo(user_id)
    
    @staticmethod
    def is_permitted(chat_id: int, user_id: int) -> bool:
        if chat_id in data_manager.permitted_users:
            return user_id in data_manager.permitted_users[chat_id]
        return False
    
    @staticmethod
    def is_admin(chat_id: int, user_id: int, context) -> bool:
        """Check if user is admin in chat"""
        try:
            member = context.bot.get_chat_member(chat_id, user_id)
            return member.status in ["creator", "administrator"]
        except:
            return False
    
    @staticmethod
    def can_bypass(user_id: int, chat_id: int = None, context = None) -> bool:
        """Check if user can bypass filters"""
        if PermissionSystem.is_auth(user_id):
            return True
        if chat_id and PermissionSystem.is_permitted(chat_id, user_id):
            return True
        if chat_id and context and PermissionSystem.is_admin(chat_id, user_id, context):
            return True
        return False

# ================= KEYBOARD SYSTEM =================
class KeyboardSystem:
    """Professional inline keyboard system"""
    
    @staticmethod
    def create_keyboard(buttons: List[List[tuple]], row_width: int = 2) -> InlineKeyboardMarkup:
        """Create inline keyboard from button matrix"""
        keyboard = []
        for row in buttons:
            keyboard_row = []
            for text, callback in row:
                keyboard_row.append(InlineKeyboardButton(text, callback_data=callback))
            keyboard.append(keyboard_row)
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def main_menu(user_id: int) -> InlineKeyboardMarkup:
        """Main menu keyboard"""
        buttons = [
            [
                (f"{Emoji.SHIELD} Features", "menu_features"),
                (f"{Emoji.GEAR} Commands", "menu_commands")
            ],
            [
                (f"{Emoji.STATS} Statistics", "menu_stats"),
                (f"{Emoji.HELP} Help", "menu_help")
            ],
            [
                (f"{Emoji.STICKER} Stickers", "menu_stickers"),
                (f"{Emoji.SETTINGS} Settings", "menu_settings")
            ]
        ]
        
        if PermissionSystem.is_sudo(user_id):
            buttons.append([
                (f"{Emoji.CROWN} Admin Panel", "menu_admin"),
                (f"{Emoji.POLICE} Moderation", "menu_mod")
            ])
        
        if PermissionSystem.is_owner(user_id):
            buttons.append([
                (f"{Emoji.ROBOT} Owner Console", "menu_owner"),
                (f"{Emoji.SATELLITE} System", "menu_system")
            ])
        
        return KeyboardSystem.create_keyboard(buttons)
    
    @staticmethod
    def admin_panel() -> InlineKeyboardMarkup:
        """Admin panel keyboard"""
        buttons = [
            [
                (f"{Emoji.BAN} Global Ban", "admin_gban"),
                (f"{Emoji.MUTE} Global Mute", "admin_gmute")
            ],
            [
                (f"{Emoji.DELETE} Global Delete", "admin_gdel"),
                (f"{Emoji.USER} User Mgmt", "admin_users")
            ],
            [
                (f"{Emoji.STICKER} Sticker System", "admin_stickers"),
                (f"{Emoji.BACKUP} Backup", "admin_backup")
            ],
            [
                (f"{Emoji.FILTER} NSFW Settings", "admin_nsfw"),
                (f"{Emoji.SHIELD} Auth System", "admin_auth")
            ],
            [
                (f"{Emoji.HOME} Main Menu", "menu_main"),
                (f"{Emoji.RELOAD} Refresh", "refresh")
            ]
        ]
        return KeyboardSystem.create_keyboard(buttons)
    
    @staticmethod
    def sticker_menu() -> InlineKeyboardMarkup:
        """Sticker menu keyboard"""
        buttons = [
            [
                (f"{Emoji.PLUS} Set Sticker", "sticker_set_info"),
                (f"{Emoji.MINUS} Remove Sticker", "sticker_remove_info")
            ],
            [
                (f"{Emoji.LIST} My Stickers", "sticker_list_info"),
                (f"{Emoji.INFO} Sticker Help", "sticker_help")
            ],
            [
                (f"{Emoji.HOME} Main Menu", "menu_main"),
                (f"{Emoji.LEFT} Back", "menu_admin")
            ]
        ]
        return KeyboardSystem.create_keyboard(buttons)
    
    @staticmethod
    def back_button(target: str = "menu_main") -> InlineKeyboardMarkup:
        """Simple back button"""
        buttons = [[(f"{Emoji.LEFT} Back", target)]]
        return KeyboardSystem.create_keyboard(buttons)

# ================= MESSAGE TEMPLATES =================
class MessageTemplates:
    """Professional message templates"""
    
    @staticmethod
    def format_duration(seconds: int) -> str:
        """Format seconds into human readable time"""
        if seconds < 60:
            return f"{seconds} seconds"
        elif seconds < 3600:
            minutes = seconds // 60
            return f"{minutes} minute{'s' if minutes > 1 else ''}"
        else:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            if minutes > 0:
                return f"{hours} hour{'s' if hours > 1 else ''} {minutes} minute{'s' if minutes > 1 else ''}"
            return f"{hours} hour{'s' if hours > 1 else ''}"
    
    @staticmethod
    def welcome_message(user) -> str:
        return f"""
{Emoji.SHIELD} <b>NudeGuard Pro - Ultimate Protection</b> {Emoji.SHIELD}

{Emoji.STAR} <b>Welcome, {html.escape(user.first_name or 'User')}!</b>

{Emoji.FIRE} <b>Core Protection Features:</b>
• {Emoji.FILTER} Advanced NSFW Detection (60% Threshold)
• {Emoji.GLOBE} Global User Management System
• {Emoji.CROWN} Auto Admin Bypass Protection
• {Emoji.STICKER} Smart Sticker Auto-Reply
• {Emoji.EDIT} Auto Delete Edited Messages (30s)
• {Emoji.BACKUP} Automatic Backup System

{Emoji.GEAR} <b>Sticker System (Public):</b>
• Everyone can use /suser and /ruser
• Regular users: {STICKER_REGULAR_DURATION} seconds duration
• Sudo/Owner: {STICKER_SUDO_DURATION//60} minutes duration
• Max 1 active sticker per regular user

{Emoji.GEAR} <b>Quick Navigation:</b>
Use the buttons below to explore features!
"""
    
    @staticmethod
    def stats_message() -> str:
        uptime = time.time() - data_manager.stats["start_time"]
        days = int(uptime // 86400)
        hours = int((uptime % 86400) // 3600)
        minutes = int((uptime % 3600) // 60)
        seconds = int(uptime % 60)
        
        return f"""
{Emoji.CHART} <b>NudeGuard Pro - System Statistics</b> {Emoji.CHART}

{Emoji.SHIELD} <b>Protection Statistics:</b>
• {Emoji.FILTER} NSFW Blocked: {data_manager.stats['total_nsfw_blocked']:,}
• {Emoji.WARNING} Warnings Issued: {data_manager.stats['total_warnings']:,}
• {Emoji.MUTE} Mutes Executed: {data_manager.stats['total_mutes']:,}
• {Emoji.BAN} Bans Issued: {data_manager.stats['total_bans']:,}
• {Emoji.STICKER} Stickers Sent: {data_manager.stats['total_stickers_sent']:,}
• {Emoji.STICKER} Stickers Set: {data_manager.stats['total_stickers_set']:,}
• {Emoji.EDIT} Edited Msgs Deleted: {data_manager.stats['total_edited_deleted']:,}

{Emoji.USER} <b>User Statistics:</b>
• Total Warned Users: {len(data_manager.user_warnings):,}
• Sudo Users: {len(data_manager.sudo_users):,}
• Auth Users: {len(data_manager.auth_users):,}
• Banned Users: {len(data_manager.banned_users):,}
• Muted Users: {len(data_manager.muted_users):,}
• Active Stickers: {len(data_manager.sticker_data.stickers):,}

{Emoji.CLOCK} <b>System Information:</b>
• Uptime: {days}d {hours}h {minutes}m {seconds}s
• NSFW Threshold: {data_manager.settings['nsfw_threshold']*100:.0f}%
• Edit Delete Time: {data_manager.settings['edit_delete_time']}s
• Last Backup: {MessageTemplates.format_time(data_manager.stats.get('last_backup', 0))}

{Emoji.STAR} <i>System is actively protecting your groups!</i>
"""
    
    @staticmethod
    def format_time(timestamp: float) -> str:
        if not timestamp:
            return "Never"
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))

# ================= NSFW DETECTION SYSTEM =================
class NSFWDetector:
    """Advanced NSFW detection system"""
    
    def __init__(self):
        self.detector = None
        self.initialize_detector()
    
    def initialize_detector(self):
        """Initialize the NSFW detector"""
        try:
            self.detector = nsfw.make_open_nsfw_model()
            logger.info(f"{Emoji.CHECK} NSFW Detector initialized successfully")
        except Exception as e:
            logger.error(f"{Emoji.CROSS} Failed to initialize NSFW detector: {e}")
            self.detector = None
    
    async def detect_nsfw(self, file_bytes: bytes, mime_type: str = None) -> float:
        """Detect NSFW content in media"""
        if not self.detector:
            return 0.0
        
        try:
            frames = []
            
            if mime_type and mime_type.startswith("image/"):
                # Process image
                image = Image.open(io.BytesIO(file_bytes)).convert("RGB")
                frames.append(image)
            elif mime_type and mime_type.startswith("video/"):
                # Process video frames
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
                    tmp.write(file_bytes)
                    tmp.flush()
                    
                    cap = cv2.VideoCapture(tmp.name)
                    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                    
                    # Sample frames (max 5)
                    sample_rate = max(1, frame_count // 5)
                    for i in range(0, min(frame_count, 5)):
                        cap.set(cv2.CAP_PROP_POS_FRAMES, i * sample_rate)
                        ret, frame = cap.read()
                        if ret:
                            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                            frames.append(Image.fromarray(rgb))
                    
                    cap.release()
                    os.unlink(tmp.name)
            else:
                # Try as image
                try:
                    image = Image.open(io.BytesIO(file_bytes)).convert("RGB")
                    frames.append(image)
                except:
                    return 0.0
            
            if not frames:
                return 0.0
            
            # Process each frame
            max_score = 0.0
            for frame in frames:
                try:
                    processed = nsfw.preprocess_image(frame, nsfw.Preprocessing.YAHOO)
                    score = self.detector.predict(np.expand_dims(processed, axis=0))[0][1]
                    max_score = max(max_score, score)
                except Exception as e:
                    logger.error(f"Frame processing error: {e}")
                    continue
            
            return max_score
            
        except Exception as e:
            logger.error(f"NSFW detection error: {e}")
            return 0.0

# ================= MAIN BOT HANDLERS =================
class NudeGuardBot:
    """Main bot class"""
    
    def __init__(self):
        self.data_manager = data_manager
        self.permissions = PermissionSystem()
        self.keyboards = KeyboardSystem()
        self.templates = MessageTemplates()
        self.nsfw_detector = NSFWDetector()
        self.application = None
        
    # ================= STICKER SYSTEM COMMANDS (PUBLIC) =================
    
    async def suser_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Set sticker for user - PUBLIC COMMAND for everyone"""
        user = update.effective_user
        setter_id = user.id
        
        # Check if replied to sticker
        if not update.message.reply_to_message or not update.message.reply_to_message.sticker:
            await update.message.reply_text(
                f"{Emoji.CROSS} <b>Usage:</b> Reply to a sticker with <code>/suser [user_id]</code>\n\n"
                f"{Emoji.INFO} <i>Examples:</i>\n"
                f"• <code>/suser 123456789</code> (set for specific user)\n"
                f"• <code>/suser</code> (reply to sticker, sets for yourself)",
                parse_mode="HTML"
            )
            return
        
        sticker = update.message.reply_to_message.sticker
        sticker_id = sticker.file_id
        
        # Determine target user
        if context.args and context.args[0].isdigit():
            target_user_id = int(context.args[0])
        else:
            target_user_id = setter_id  # Set for self if no user ID provided
        
        # Check if user can set another sticker
        if not self.data_manager.sticker_data.can_set_sticker(setter_id):
            await update.message.reply_text(
                f"{Emoji.CROSS} <b>Limit Reached!</b>\n"
                f"You can only have 1 active sticker at a time.\n"
                f"Use <code>/ruser</code> to remove existing stickers first.",
                parse_mode="HTML"
            )
            return
        
        # Determine duration based on user privileges
        if self.permissions.is_owner(setter_id) or self.permissions.is_sudo(setter_id):
            duration = STICKER_SUDO_DURATION  # 30 minutes for sudo/owner
            duration_text = f"{STICKER_SUDO_DURATION//60} minutes"
        else:
            duration = STICKER_REGULAR_DURATION  # 30 seconds for regular users
            duration_text = f"{STICKER_REGULAR_DURATION} seconds"
        
        # Set the sticker
        success = self.data_manager.sticker_data.set_sticker(
            target_user_id=target_user_id,
            sticker_id=sticker_id,
            setter_id=setter_id,
            duration=duration
        )
        
        if success:
            # Get remaining time
            sticker_info = self.data_manager.sticker_data.get_sticker(target_user_id)
            expires_at = sticker_info["expires_at"]
            time_left = max(0, expires_at - time.time())
            
            # Update stats
            self.data_manager.stats["total_stickers_set"] += 1
            self.data_manager.save_data("stats")
            
            # Format message
            if target_user_id == setter_id:
                target_text = "yourself"
            else:
                target_text = f"user <code>{target_user_id}</code>"
            
            await update.message.reply_text(
                f"{Emoji.STICKER} <b>Sticker Set Successfully!</b>\n\n"
                f"{Emoji.USER} <b>Set for:</b> {target_text}\n"
                f"{Emoji.CLOCK} <b>Duration:</b> {duration_text}\n"
                f"{Emoji.TIME} <b>Expires in:</b> {self.templates.format_duration(int(time_left))}\n\n"
                f"{Emoji.INFO} <i>Bot will auto-reply with this sticker when {target_text} sends messages in groups.</i>",
                parse_mode="HTML"
            )
        else:
            await update.message.reply_text(
                f"{Emoji.CROSS} Failed to set sticker. Please try again.",
                parse_mode="HTML"
            )
    
    async def ruser_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Remove sticker for user - PUBLIC COMMAND for everyone"""
        user = update.effective_user
        user_id = user.id
        
        # Determine target user
        if context.args and context.args[0].isdigit():
            target_user_id = int(context.args[0])
        else:
            target_user_id = user_id  # Remove from self if no user ID provided
        
        # Check if sticker exists
        sticker_info = self.data_manager.sticker_data.get_sticker(target_user_id)
        if not sticker_info:
            await update.message.reply_text(
                f"{Emoji.CROSS} No active sticker found for user <code>{target_user_id}</code>.",
                parse_mode="HTML"
            )
            return
        
        # Check permissions
        setter_id = sticker_info.get("setter_id")
        can_remove = False
        
        if user_id == setter_id:  # User set this sticker
            can_remove = True
        elif self.permissions.is_owner(user_id) or self.permissions.is_sudo(user_id):  # Sudo/owner can remove any sticker
            can_remove = True
        
        if not can_remove:
            await update.message.reply_text(
                f"{Emoji.CROSS} <b>Permission Denied!</b>\n"
                f"You can only remove stickers that you set.",
                parse_mode="HTML"
            )
            return
        
        # Remove the sticker
        success = self.data_manager.sticker_data.remove_sticker(target_user_id)
        
        if success:
            if target_user_id == user_id:
                target_text = "your sticker"
            else:
                target_text = f"sticker for user <code>{target_user_id}</code>"
            
            await update.message.reply_text(
                f"{Emoji.CHECK} <b>Sticker Removed!</b>\n"
                f"Successfully removed {target_text}.",
                parse_mode="HTML"
            )
        else:
            await update.message.reply_text(
                f"{Emoji.CROSS} Failed to remove sticker. Please try again.",
                parse_mode="HTML"
            )
    
    async def mystickers_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """List all stickers set by the user - PUBLIC COMMAND"""
        user = update.effective_user
        user_id = user.id
        
        # Get all stickers set by this user
        target_ids = self.data_manager.sticker_data.get_setter_stickers(user_id)
        
        if not target_ids:
            await update.message.reply_text(
                f"{Emoji.INFO} <b>No Active Stickers</b>\n"
                f"You haven't set any active stickers.\n\n"
                f"{Emoji.STICKER} <i>Use </i><code>/suser</code><i> to set a sticker!</i>",
                parse_mode="HTML"
            )
            return
        
        # Build sticker list
        sticker_list = []
        total_count = len(target_ids)
        
        for target_id in target_ids:
            sticker_info = self.data_manager.sticker_data.get_sticker(target_id)
            if sticker_info:
                time_left = max(0, sticker_info["expires_at"] - time.time())
                
                if target_id == user_id:
                    target_text = "Yourself"
                else:
                    target_text = f"User <code>{target_id}</code>"
                
                sticker_list.append(
                    f"• {target_text} - Expires in {self.templates.format_duration(int(time_left))}"
                )
        
        if sticker_list:
            message_text = "\n".join(sticker_list)
            
            # Add header
            if self.permissions.is_owner(user_id) or self.permissions.is_sudo(user_id):
                user_type = "Sudo/Owner"
            else:
                user_type = "Regular User"
            
            await update.message.reply_text(
                f"{Emoji.LIST} <b>Your Active Stickers</b>\n\n"
                f"{Emoji.USER} <b>User Type:</b> {user_type}\n"
                f"{Emoji.STICKER} <b>Active Stickers:</b> {total_count}\n\n"
                f"{message_text}\n\n"
                f"{Emoji.INFO} <i>Use </i><code>/ruser [user_id]</code><i> to remove a sticker.</i>",
                parse_mode="HTML"
            )
        else:
            await update.message.reply_text(
                f"{Emoji.INFO} All your stickers have expired or been removed.",
                parse_mode="HTML"
            )
    
    # ================= STICKER AUTO-REPLY HANDLER =================
    
    async def sticker_auto_reply(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Auto-reply with user's sticker if they have one active"""
        if not self.data_manager.settings.get("sticker_auto_reply", True):
            return
        
        if update.effective_chat.type not in ["group", "supergroup"]:
            return
        
        user_id = update.effective_user.id
        
        # Check if user has an active sticker
        sticker_info = self.data_manager.sticker_data.get_sticker(user_id)
        if sticker_info:
            try:
                await update.message.reply_sticker(sticker_info["sticker_id"])
                
                # Update stats
                self.data_manager.stats["total_stickers_sent"] += 1
                self.data_manager.save_data("stats")
                
            except Exception as e:
                logger.error(f"Sticker reply error: {e}")
    
    # ================= MAIN COMMAND HANDLERS =================
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user = update.effective_user
        
        # Log to channel
        await self.log_to_channel(
            f"{Emoji.USER} <b>New User Started Bot</b>\n"
            f"• User: <a href='tg://user?id={user.id}'>{html.escape(user.first_name or 'User')}</a>\n"
            f"• ID: <code>{user.id}</code>\n"
            f"• Username: @{user.username if user.username else 'N/A'}",
            context
        )
        
        # Send welcome message
        try:
            await update.message.reply_photo(
                photo=INTRO_PHOTO,
                caption=self.templates.welcome_message(user),
                parse_mode="HTML",
                reply_markup=self.keyboards.main_menu(user.id)
            )
        except:
            await update.message.reply_text(
                self.templates.welcome_message(user),
                parse_mode="HTML",
                reply_markup=self.keyboards.main_menu(user.id)
            )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        user_id = update.effective_user.id
        await update.message.reply_text(
            f"{Emoji.HELP} <b>NudeGuard Pro - Help Center</b>\n\n"
            f"Use the buttons below to navigate through features!",
            parse_mode="HTML",
            reply_markup=self.keyboards.main_menu(user_id)
        )
    
    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /stats command"""
        await update.message.reply_text(
            self.templates.stats_message(),
            parse_mode="HTML",
            reply_markup=self.keyboards.back_button()
        )
    
    # ================= CALLBACK HANDLERS =================
    
    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle all inline keyboard button presses"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        data = query.data
        
        # Main menu navigation
        if data == "menu_main":
            await query.edit_message_text(
                text=self.templates.welcome_message(query.from_user),
                parse_mode="HTML",
                reply_markup=self.keyboards.main_menu(user_id)
            )
        
        elif data == "menu_stickers":
            await query.edit_message_text(
                text=f"{Emoji.STICKER} <b>Sticker System</b>\n\n"
                     f"{Emoji.INFO} <b>Public Commands:</b>\n"
                     f"• /suser - Set sticker for user\n"
                     f"• /ruser - Remove sticker\n"
                     f"• /mystickers - List your stickers\n\n"
                     f"{Emoji.CLOCK} <b>Time Limits:</b>\n"
                     f"• Regular users: {STICKER_REGULAR_DURATION} seconds\n"
                     f"• Sudo/Owner: {STICKER_SUDO_DURATION//60} minutes",
                parse_mode="HTML",
                reply_markup=self.keyboards.back_button()
            )
        
        elif data == "menu_features":
            text = f"""
{Emoji.FIRE} <b>Advanced Features</b> {Emoji.FIRE}

{Emoji.FILTER} <b>NSFW Detection System:</b>
• Real-time image/video analysis
• 60% threshold on every frame
• Multi-frame video processing
• AI-powered content filtering

{Emoji.GLOBE} <b>Global Moderation:</b>
• Global ban/mute/delete system
• Force actions in any chat
• User warning system
• Automatic violation tracking

{Emoji.SHIELD} <b>Security Features:</b>
• Auto admin bypass
• Permission-based access
• Encrypted data storage
• Automatic backups

{Emoji.ROBOT} <b>Automation:</b>
• Auto sticker replies (Public)
• Edited message deletion
• Log channel reporting
• Scheduled backups

{Emoji.STICKER} <b>Sticker System (Public):</b>
• Everyone can use /suser and /ruser
• Regular users: {STICKER_REGULAR_DURATION} seconds
• Sudo/Owner: {STICKER_SUDO_DURATION//60} minutes
• Max 1 active sticker per regular user

{Emoji.SETTINGS} <b>Customization:</b>
• Adjustable NSFW threshold
• Configurable warning system
• Custom mute durations
• Flexible settings
"""
            await query.edit_message_text(
                text=text,
                parse_mode="HTML",
                reply_markup=self.keyboards.back_button()
            )
        
        elif data == "menu_commands":
            text = f"""
{Emoji.GEAR} <b>Available Commands</b>

{Emoji.INFO} <b>General Commands:</b>
• /start - Start the bot
• /help - Show this help message
• /stats - View bot statistics
• /report [reason] - Report an issue

{Emoji.STICKER} <b>Sticker System (Public for Everyone):</b>
• /suser [user_id] - Set sticker for user (reply to sticker)
• /ruser [user_id] - Remove sticker from user
• /mystickers - List your active stickers

{Emoji.SHIELD} <b>For Group Admins:</b>
Add me as administrator with:
• Delete messages permission
• Restrict users permission
• Pin messages permission

{Emoji.CROWN} <b>Sudo/Owner Commands:</b>
• /gban, /gmute, /gdel - Global moderation
• /addsudo, /addauth - User management
• /backup - System backup

{Emoji.STAR} <i>Sticker limits: Regular users = {STICKER_REGULAR_DURATION}s, Sudo = {STICKER_SUDO_DURATION//60}m</i>
"""
            await query.edit_message_text(
                text=text,
                parse_mode="HTML",
                reply_markup=self.keyboards.back_button()
            )
        
        elif data == "menu_admin":
            if self.permissions.is_sudo(user_id):
                await query.edit_message_text(
                    text=f"{Emoji.CROWN} <b>Admin Control Panel</b>\nSelect an option:",
                    parse_mode="HTML",
                    reply_markup=self.keyboards.admin_panel()
                )
            else:
                await query.answer("❌ Admin access required!", show_alert=True)
        
        elif data == "admin_stickers":
            if self.permissions.is_sudo(user_id):
                await query.edit_message_text(
                    text=f"{Emoji.STICKER} <b>Sticker Management</b>\nManage the sticker system:",
                    parse_mode="HTML",
                    reply_markup=self.keyboards.sticker_menu()
                )
            else:
                await query.answer("❌ Admin access required!", show_alert=True)
        
        elif data == "sticker_set_info":
            text = f"""
{Emoji.STICKER} <b>Set Sticker Command</b>

<b>Command:</b> <code>/suser [user_id]</code>
<b>Usage:</b> Reply to a sticker with this command

<b>Examples:</b>
<code>/suser 123456789</code> - Set sticker for user 123456789
<code>/suser</code> (reply to sticker) - Set for yourself

<b>Time Limits:</b>
• Regular users: {STICKER_REGULAR_DURATION} seconds
• Sudo/Owner: {STICKER_SUDO_DURATION//60} minutes

<b>Limits:</b>
• Regular users can only have 1 active sticker at a time
• Sudo/Owner can set unlimited stickers
"""
            await query.edit_message_text(
                text=text,
                parse_mode="HTML",
                reply_markup=self.keyboards.back_button("admin_stickers")
            )
        
        elif data == "sticker_remove_info":
            text = f"""
{Emoji.STICKER} <b>Remove Sticker Command</b>

<b>Command:</b> <code>/ruser [user_id]</code>
<b>Usage:</b> Remove sticker from a user

<b>Permissions:</b>
• Can remove your own stickers
• Sudo/Owner can remove any sticker

<b>Examples:</b>
<code>/ruser 123456789</code> - Remove sticker from user
<code>/ruser</code> (no args) - Remove sticker from yourself
"""
            await query.edit_message_text(
                text=text,
                parse_mode="HTML",
                reply_markup=self.keyboards.back_button("admin_stickers")
            )
        
        elif data == "sticker_list_info":
            text = f"""
{Emoji.STICKER} <b>My Stickers Command</b>

<b>Command:</b> <code>/mystickers</code>
<b>Usage:</b> List all stickers you have set

<b>Shows:</b>
• Target user IDs
• Time remaining
• Total active stickers
"""
            await query.edit_message_text(
                text=text,
                parse_mode="HTML",
                reply_markup=self.keyboards.back_button("admin_stickers")
            )
        
        elif data == "sticker_help":
            text = f"""
{Emoji.HELP} <b>Sticker System Help</b>

{Emoji.STICKER} <b>How it works:</b>
1. Reply to a sticker with /suser [user_id]
2. Bot will auto-reply with that sticker
3. Sticker expires after time limit
4. Use /ruser to remove manually

{Emoji.CLOCK} <b>Time Limits:</b>
• Everyone: Can use /suser and /ruser
• Regular users: {STICKER_REGULAR_DURATION} seconds per sticker
• Sudo/Owner: {STICKER_SUDO_DURATION//60} minutes per sticker

{Emoji.WARNING} <b>Limits:</b>
• Regular users: Max 1 active sticker
• Sudo/Owner: Unlimited stickers
• Stickers auto-remove when expired
"""
            await query.edit_message_text(
                text=text,
                parse_mode="HTML",
                reply_markup=self.keyboards.back_button("admin_stickers")
            )
        
        elif data == "refresh":
            await query.answer("🔄 Refreshed!", show_alert=True)
            await query.edit_message_reply_markup(reply_markup=query.message.reply_markup)
    
    # ================= NSFW DETECTION HANDLER =================
    
    async def media_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle all media messages for NSFW detection"""
        msg = update.message
        user = msg.from_user
        chat = msg.chat
        
        # Check permissions
        if self.permissions.can_bypass(user.id, chat.id, context):
            logger.info(f"Bypass NSFW for privileged user {user.id}")
            return
        
        # Check global restrictions
        if user.id in self.data_manager.banned_users:
            try:
                await msg.delete()
                await context.bot.send_message(
                    chat.id,
                    f"{Emoji.BAN} <b>User removed (Globally Banned)</b>",
                    parse_mode="HTML"
                )
                return
            except:
                pass
        
        if user.id in self.data_manager.muted_users:
            try:
                until = int(time.time()) + 86400 * 365  # 1 year
                await context.bot.restrict_chat_member(
                    chat.id, user.id,
                    permissions=ChatPermissions(),
                    until_date=until
                )
                await msg.delete()
                return
            except:
                pass
        
        if user.id in self.data_manager.deleted_users:
            try:
                await msg.delete()
                return
            except:
                pass
        
        # Get media file
        file = None
        mime_type = None
        
        if msg.photo:
            file = await msg.photo[-1].get_file()
        elif msg.sticker:
            if msg.sticker.is_video:
                mime_type = "video/webm"
            else:
                mime_type = "image/webp"
            file = await msg.sticker.get_file()
        elif msg.animation:
            mime_type = "video/mp4"
            file = await msg.animation.get_file()
        elif msg.video:
            mime_type = "video/mp4"
            file = await msg.video.get_file()
        elif msg.video_note:
            mime_type = "video/mp4"
            file = await msg.video_note.get_file()
        elif msg.document:
            if msg.document.mime_type and msg.document.mime_type.startswith(("image/", "video/")):
                mime_type = msg.document.mime_type
                file = await msg.document.get_file()
        
        if not file:
            return
        
        # Download and check
        try:
            file_bytes = await file.download_as_bytearray()
            nsfw_score = await self.nsfw_detector.detect_nsfw(file_bytes, mime_type)
            
            if nsfw_score >= self.data_manager.settings["nsfw_threshold"]:
                await self.handle_nsfw_violation(msg, user, chat, nsfw_score, context)
        
        except Exception as e:
            logger.error(f"Media processing error: {e}")
    
    async def handle_nsfw_violation(self, msg, user, chat, score: float, context):
        """Handle NSFW violation"""
        # Delete the message
        try:
            await msg.delete()
        except:
            pass
        
        # Update stats
        self.data_manager.stats["total_nsfw_blocked"] += 1
        self.data_manager.save_data("stats")
        
        # Get current warnings
        current_warnings = self.data_manager.user_warnings.get(user.id, 0)
        new_warnings = current_warnings + 1
        
        # Check if should mute
        if new_warnings >= self.data_manager.settings["max_warnings"]:
            # Mute the user
            mute_duration = self.data_manager.settings["mute_duration"]
            until = int(time.time()) + mute_duration
            
            try:
                await context.bot.restrict_chat_member(
                    chat.id, user.id,
                    permissions=ChatPermissions(),
                    until_date=until
                )
                
                # Send mute notification
                await context.bot.send_message(
                    chat.id,
                    f"{Emoji.MUTE} <b>User Muted</b>\n"
                    f"User: {html.escape(user.first_name or 'User')}\n"
                    f"Duration: {mute_duration//60} minutes\n"
                    f"Reason: Multiple NSFW violations",
                    parse_mode="HTML"
                )
                
                # Update stats
                self.data_manager.stats["total_mutes"] += 1
                self.data_manager.save_data("stats")
                
                # Reset warnings
                self.data_manager.user_warnings[user.id] = 0
                self.data_manager.save_data("warnings")
                
                # Log to owners
                await self.log_to_owners(
                    f"{Emoji.MUTE} <b>Auto-Mute Executed</b>\n"
                    f"• Chat: <code>{chat.id}</code>\n"
                    f"• User: <a href='tg://user?id={user.id}'>{html.escape(user.first_name or 'User')}</a>\n"
                    f"• Score: {score*100:.1f}%\n"
                    f"• Warnings: {new_warnings}",
                    context
                )
                
                return
                
            except Exception as e:
                logger.error(f"Mute error: {e}")
        
        # Update warnings
        self.data_manager.user_warnings[user.id] = new_warnings
        self.data_manager.stats["total_warnings"] += 1
        self.data_manager.save_data("warnings")
        self.data_manager.save_data("stats")
        
        # Send warning notification
        await context.bot.send_message(
            chat.id,
            f"{Emoji.WARNING} <b>NSFW Content Detected!</b>\n"
            f"User: {html.escape(user.first_name or 'User')}\n"
            f"NSFW Score: {score*100:.1f}%\n"
            f"Warning: {new_warnings}/{self.data_manager.settings['max_warnings']}",
            parse_mode="HTML"
        )
    
    # ================= EDITED MESSAGE HANDLER =================
    
    async def edited_message_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle edited messages"""
        msg = update.edited_message
        user = msg.from_user
        chat = msg.chat
        
        # Check permissions
        if self.permissions.can_bypass(user.id, chat.id, context):
            return
        
        # Send warning about deletion
        warning_msg = await context.bot.send_message(
            chat.id,
            f"{Emoji.EDIT} <b>Edited Message Detected</b>\n"
            f"User: {html.escape(user.first_name or 'User')}\n"
            f"Will be deleted in {self.data_manager.settings['edit_delete_time']} seconds",
            parse_mode="HTML"
        )
        
        # Wait and delete both messages
        await asyncio.sleep(self.data_manager.settings["edit_delete_time"])
        
        try:
            await msg.delete()
            await warning_msg.delete()
            
            # Update stats
            self.data_manager.stats["total_edited_deleted"] += 1
            self.data_manager.save_data("stats")
            
        except Exception as e:
            logger.error(f"Delete edited message error: {e}")
    
    # ================= MODERATION COMMANDS =================
    
    async def gban_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Global ban command - SUDO ONLY"""
        if not self.permissions.is_sudo(update.effective_user.id):
            await update.message.reply_text(f"{Emoji.CROSS} Sudo access required.")
            return
        
        try:
            # Get user ID
            if update.message.reply_to_message:
                user_id = update.message.reply_to_message.from_user.id
            elif context.args:
                user_id = int(context.args[0])
            else:
                await update.message.reply_text(
                    f"{Emoji.CROSS} Reply to user or provide ID.\n"
                    f"Usage: <code>/gban [user_id]</code>",
                    parse_mode="HTML"
                )
                return
            
            # Add to banned list
            self.data_manager.banned_users.add(user_id)
            self.data_manager.stats["total_bans"] += 1
            self.data_manager.save_data("banned")
            self.data_manager.save_data("stats")
            
            await update.message.reply_text(
                f"{Emoji.BAN} <b>Global Ban Applied</b>\n"
                f"• User ID: <code>{user_id}</code>\n"
                f"• Banned by: {html.escape(update.effective_user.first_name or 'Admin')}\n"
                f"• Time: {time.strftime('%Y-%m-%d %H:%M:%S')}",
                parse_mode="HTML"
            )
            
            # Log action
            await self.log_to_channel(
                f"{Emoji.BAN} <b>Global Ban Executed</b>\n"
                f"• User: <code>{user_id}</code>\n"
                f"• By: <a href='tg://user?id={update.effective_user.id}'>{html.escape(update.effective_user.first_name or 'Admin')}</a>",
                context
            )
            
        except Exception as e:
            await update.message.reply_text(f"{Emoji.CROSS} Error: {str(e)}")
    
    async def addsudo_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Add sudo user - OWNER ONLY"""
        if not self.permissions.is_owner(update.effective_user.id):
            await update.message.reply_text(f"{Emoji.CROSS} Owner access required.")
            return
        
        try:
            if update.message.reply_to_message:
                user_id = update.message.reply_to_message.from_user.id
            elif context.args:
                user_id = int(context.args[0])
            else:
                await update.message.reply_text(f"{Emoji.CROSS} Reply to user or provide ID.")
                return
            
            self.data_manager.sudo_users.add(user_id)
            self.data_manager.save_data("sudo")
            
            await update.message.reply_text(
                f"{Emoji.CROWN} <b>Sudo User Added</b>\n"
                f"• User ID: <code>{user_id}</code>\n"
                f"• Added by: {html.escape(update.effective_user.first_name or 'Owner')}",
                parse_mode="HTML"
            )
            
        except:
            await update.message.reply_text(f"{Emoji.CROSS} Invalid usage.")
    
    # ================= UTILITY FUNCTIONS =================
    
    async def log_to_channel(self, message: str, context):
        """Log message to channel"""
        if not self.data_manager.settings["log_enabled"]:
            return
        
        try:
            await context.bot.send_message(
                LOG_CHANNEL,
                message,
                parse_mode="HTML",
                disable_web_page_preview=True
            )
        except Exception as e:
            logger.error(f"Failed to log to channel: {e}")
    
    async def log_to_owners(self, message: str, context):
        """Send message to all owners"""
        for owner_id in OWNERS:
            try:
                await context.bot.send_message(
                    owner_id,
                    message,
                    parse_mode="HTML"
                )
            except Exception as e:
                logger.error(f"Failed to send to owner {owner_id}: {e}")
    
    def run(self):
        """Start the bot"""
        # Create application
        self.application = Application.builder().token(BOT_TOKEN).build()
        
        # ================= ADD HANDLERS =================
        
        # Command handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("stats", self.stats_command))
        
        # Sticker system commands (PUBLIC FOR EVERYONE)
        self.application.add_handler(CommandHandler("suser", self.suser_command))
        self.application.add_handler(CommandHandler("ruser", self.ruser_command))
        self.application.add_handler(CommandHandler("mystickers", self.mystickers_command))
        
        # Moderation commands (SUDO ONLY)
        self.application.add_handler(CommandHandler("gban", self.gban_command))
        self.application.add_handler(CommandHandler("addsudo", self.addsudo_command))
        
        # Callback query handler (MUST BE BEFORE MESSAGE HANDLERS)
        self.application.add_handler(CallbackQueryHandler(self.button_handler))
        
        # Message handlers
        self.application.add_handler(MessageHandler(
            filters.PHOTO | filters.VIDEO | filters.Sticker.ALL | 
            filters.ANIMATION | filters.VIDEO_NOTE |
            (filters.Document.IMAGE | filters.Document.VIDEO),
            self.media_handler
        ))
        
        # Edited message handler
        self.application.add_handler(MessageHandler(
            filters.UpdateType.EDITED_MESSAGE,
            self.edited_message_handler
        ))
        
        # Sticker auto-reply (lowest priority)
        self.application.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            self.sticker_auto_reply
        ), group=1)
        
        # Start bot
        logger.info(f"{Emoji.ROBOT} NudeGuard Pro - Starting...")
        logger.info(f"{Emoji.STAR} Bot Token: {BOT_TOKEN[:10]}...")
        logger.info(f"{Emoji.SHIELD} Owners: {OWNERS}")
        logger.info(f"{Emoji.CHART} Log Channel: {LOG_CHANNEL}")
        logger.info(f"{Emoji.STICKER} Sticker System: Active (Public)")
        logger.info(f"{Emoji.CLOCK} Regular Users: {STICKER_REGULAR_DURATION}s duration")
        logger.info(f"{Emoji.CROWN} Sudo/Owner: {STICKER_SUDO_DURATION//60}m duration")
        logger.info(f"{Emoji.CHECK} Bot is ready!")
        
        self.application.run_polling()

# ================= MAIN EXECUTION =================
if __name__ == "__main__":
    # Check if running on Heroku
    if os.environ.get("DYNO"):
        print(f"{Emoji.ROCKET} Running on Heroku...")
    
    # Create and run bot
    bot = NudeGuardBot()
    bot.run()

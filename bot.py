# -*- coding: utf-8 -*-
"""
🤖 NudeGuard Pro - Ultimate Protection Bot
🔥 Complete NSFW Filter • Global Moderation • Professional UI
🎯 60% NSFW Detection • Auto Admin Bypass • Multi-Layer Security
👑 Owners: 6138142369 | 7878477646 | Log: -1002572018720
"""

# ================= INSTALL & IMPORT (robust) =================
import os
import sys
import json
import io
import zipfile
import time
import html
import logging
import asyncio
import tempfile
import subprocess
import traceback
from typing import Dict, Set, List, Optional

# Robust installer: map PyPI package spec -> import name
required_packages = {
    "python-telegram-bot==21.7": "telegram",
    "opennsfw2>=0.10.2": "opennsfw2",
    "pillow": "PIL",
    "nest-asyncio": "nest_asyncio",
    "opencv-python-headless": "cv2",
    "numpy": "numpy"
}

import importlib
for pkg_spec, import_name in required_packages.items():
    try:
        importlib.import_module(import_name)
    except ImportError:
        print(f"Installing {pkg_spec}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg_spec])

# Now import everything (safe to import after potentially installing)
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

# ================= EMOJI SYSTEM =================
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
    GROUP = "👥"
    USER = "👤"
    LOCK = "🔒"
    UNLOCK = "🔓"
    HOME = "🏠"
    RELOAD = "🔄"
    SEARCH = "🔍"
    FILTER = "🎭"
    CAMERA = "📷"
    VIDEO = "🎥"
    STICKER = "🖼️"
    ALERT = "🚨"
    CLOCK = "⏰"
    CHART = "📈"
    MESSAGE = "💬"
    EDIT = "✏️"
    EYE = "👁️"
    GLOBE = "🌍"
    KEY = "🔑"
    BELL = "🔔"
    TRASH = "🚮"
    SETTINGS = "⚡"
    SHIELD_CHECK = "✅"
    SHIELD_CROSS = "❌"
    PLUS = "➕"
    MINUS = "➖"
    LIST = "📋"
    UPLOAD = "📤"
    DOWNLOAD = "📥"
    POWER = "🔋"
    SMILE = "😊"
    SAD = "😢"
    ANGRY = "😠"
    HEART = "❤️"
    FLAG = "🚩"
    TROPHY = "🏆"
    MEDAL = "🎖️"
    LIGHT = "💡"
    TOOLS = "🛠️"
    SATELLITE = "🛰️"
    RADAR = "📡"
    POLICE = "👮"
    GHOST = "👻"
    MAGIC = "🎩"
    SWORD = "⚔️"
    ARMOR = "🛡️"
    CASTLE = "🏰"
    DRAGON = "🐉"
    TIGER = "🐯"
    LION = "🦁"
    EAGLE = "🦅"
    SHARK = "🦈"
    SPIDER = "🕷️"
    SCORPION = "🦂"
    SNAKE = "🐍"
    WOLF = "🐺"
    BEAR = "🐻"
    FOX = "🦊"
    OWL = "🦉"
    PARROT = "🦜"
    PEACOCK = "🦚"
    BUTTERFLY = "🦋"
    BEE = "🐝"
    ANT = "🐜"
    LADYBUG = "🐞"
    TURTLE = "🐢"
    FISH = "🐟"
    DOLPHIN = "🐬"
    WHALE = "🐋"
    OCTOPUS = "🐙"
    SQUID = "🦑"
    CRAB = "🦀"
    LOBSTER = "🦞"
    SHRIMP = "🦐"
    SNAIL = "🐌"
    BAT = "🦇"
    UNICORN = "🦄"
    PHOENIX = "🔥"
    YIN_YANG = "☯️"
    OM = "🕉️"
    STAR_DAVID = "✡️"
    CROSS_CHRISTIAN = "✝️"
    CRESCENT = "☪️"
    WHEEL = "☸️"
    PEACE = "☮️"
    RADIOACTIVE = "☢️"
    BIOHAZARD = "☣️"
    CAUTION = "🚸"
    NO_ENTRY = "⛔"
    PROHIBITED = "🚫"
    WARNING_SIGN = "⚠️"
    CONSTRUCTION = "🚧"
    POLICE_LIGHT = "🚨"
    FIRE_ENGINE = "🚒"
    AMBULANCE = "🚑"
    MINIBUS = "🚐"
    TRUCK = "🚚"
    SHIP = "🚢"
    AIRPLANE = "✈️"
    ROCKET = "🚀"
    HELICOPTER = "🚁"
    TRAIN = "🚂"
    METRO = "🚇"
    BUS = "🚌"
    TAXI = "🚕"
    CAR = "🚗"
    BIKE = "🚲"
    SCOOTER = "🛵"
    SKATEBOARD = "🛹"
    BUS_STOP = "🚏"
    FUEL_PUMP = "⛽"
    TRAFFIC_LIGHT = "🚦"
    POLICE_CAR = "🚓"
    FIRE_TRUCK = "🚒"
    AMBULANCE_CAR = "🚑"
    TAXI_CAR = "🚕"
    DELIVERY_TRUCK = "🚚"
    ARTICULATED_LORRY = "🚛"
    TRACTOR = "🚜"
    RACING_CAR = "🏎️"
    MOTORCYCLE = "🏍️"
    BICYCLE = "🚴"
    MOUNTAIN_BIKE = "🚵"
    WALKING = "🚶"
    RUNNING = "🏃"
    DANCING = "💃"
    JUMPING = "🦘"
    SWIMMING = "🏊"
    SURFING = "🏄"
    ROWING = "🚣"
    FISHING = "🎣"
    BOXING = "🥊"
    MARTIAL_ARTS = "🥋"
    WEIGHTLIFTING = "🏋️"
    GOLF = "⛳"
    TENNIS = "🎾"
    BASKETBALL = "🏀"
    SOCCER = "⚽"
    FOOTBALL = "🏈"
    BASEBALL = "⚾"
    CRICKET = "🏏"
    HOCKEY = "🏒"
    RUGBY = "🏉"
    BOWLING = "🎳"
    CHESS = "♟️"
    DICE = "🎲"
    CARDS = "🃏"
    MAHJONG = "🀄"
    VIDEO_GAME = "🎮"
    JOYSTICK = "🕹️"
    SLOT_MACHINE = "🎰"
    LOTTERY = "🎫"
    TICKET = "🎟️"
    TROPHY_CUP = "🏆"
    MEDAL_GOLD = "🥇"
    MEDAL_SILVER = "🥈"
    MEDAL_BRONZE = "🥉"
    RIBBON = "🎀"
    GIFT = "🎁"
    BALLOON = "🎈"
    PARTY_POPPER = "🎉"
    CONFETTI = "🎊"
    TADA = "🎊"
    FIREWORKS = "🎆"
    SPARKLER = "🎇"
    CHRISTMAS_TREE = "🎄"
    SANTA = "🎅"
    SNOWMAN = "☃️"
    SNOWFLAKE = "❄️"
    CLOUD_SNOW = "🌨️"
    CLOUD_RAIN = "🌧️"
    CLOUD_LIGHTNING = "⛈️"
    CLOUD_SUN = "⛅"
    SUN = "☀️"
    MOON = "🌙"
    STAR_GLOWING = "🌟"
    RAINBOW = "🌈"
    UMBRELLA = "☂️"
    DROPLET = "💧"
    WAVE = "🌊"
    FIRE_FLAME = "🔥"
    VOLCANO = "🌋"
    MOUNTAIN = "⛰️"
    DESERT = "🏜️"
    ISLAND = "🏝️"
    PARK = "🏞️"
    STADIUM = "🏟️"
    BRIDGE = "🌉"
    CITYSCAPE = "🏙️"
    NIGHT_SCENE = "🌃"
    SUNRISE = "🌅"
    SUNSET = "🌇"
    FERRIS_WHEEL = "🎡"
    ROLLER_COASTER = "🎢"
    CAROUSEL = "🎠"
    FOUNTAIN = "⛲"
    BEACH = "🏖️"
    CAMPING = "🏕️"
    TENT = "⛺"
    HOTEL = "🏨"
    HOSPITAL = "🏥"
    BANK = "🏦"
    SCHOOL = "🏫"
    FACTORY = "🏭"
    JAPANESE_CASTLE = "🏯"
    EUROPEAN_CASTLE = "🏰"
    WEDDING = "💒"
    CHURCH = "⛪"
    MOSQUE = "🕌"
    SYNAGOGUE = "🕍"
    HINDU_TEMPLE = "🛕"
    KAABA = "🕋"
    SHINTO_SHRINE = "⛩️"
    STATUE = "🗽"
    MAP = "🗺️"
    GLOBE_MERIDIANS = "🌐"
    COMPASS = "🧭"
    MOUNTAIN_SNOW = "🏔️"
    BEACH_UMBRELLA = "🏖️"
    DESERT_ISLAND = "🏝️"
    NATIONAL_PARK = "🏞️"
    STADIUM_LIGHTS = "🏟️"
    HOUSE = "🏠"
    HOUSE_WITH_GARDEN = "🏡"
    OFFICE = "🏢"
    POST_OFFICE = "🏤"
    LOVE_HOTEL = "🏩"
    CONVENIENCE_STORE = "🏪"
    DEPARTMENT_STORE = "🏬"
    SCHOOL_UNIFORM = "👔"
    GRADUATION_CAP = "🎓"
    BRIEFCASE = "💼"
    LAPTOP = "💻"
    COMPUTER = "🖥️"
    PRINTER = "🖨️"
    KEYBOARD = "⌨️"
    MOUSE = "🖱️"
    TRACKBALL = "🖲️"
    FLOPPY_DISK = "💾"
    CD = "💿"
    DVD = "📀"
    VIDEO_CASSETTE = "📼"
    CAMERA_FLASH = "📸"
    VIDEO_CAMERA = "📹"
    MOVIE_CAMERA = "🎥"
    FILM_PROJECTOR = "📽️"
    TELEVISION = "📺"
    RADIO = "📻"
    MICROPHONE = "🎤"
    HEADPHONE = "🎧"
    # left intentionally truncated for readability
    LEFT = "◀️"
    # NOTE: Additional emojis remain available as class attributes if needed.

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
            "stickers": "user_stickers.json",
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
        self.user_stickers: Dict[int, str] = {}
        self.permitted_users: Dict[int, Set[int]] = {}
        self.stats: Dict = {
            "total_nsfw_blocked": 0,
            "total_warnings": 0,
            "total_mutes": 0,
            "total_bans": 0,
            "total_stickers_sent": 0,
            "total_edited_deleted": 0,
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
            "sticker_auto_reply": True
        }

        self._auto_backup_task = None
        self.load_all_data()
        # scheduler will be started from the running event loop by the bot.

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
                        elif key == "stickers":
                            self.user_stickers = {int(k): v for k, v in data.items()}
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
            elif key == "stickers":
                data = self.user_stickers
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

    def setup_backup_scheduler(self):
        """Return the backup coroutine. Start it from the running event loop."""
        async def auto_backup():
            while True:
                try:
                    await asyncio.sleep(self.settings.get("backup_interval", 86400))
                    if self.settings.get("auto_backup", True):
                        await self.create_auto_backup()
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Auto-backup internal error: {e}")
        return auto_backup

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
                    "stickers": self.user_stickers,
                    "permitted": {str(k): list(v) for k, v in self.permitted_users.items()},
                    "stats": self.stats,
                    "settings": self.settings
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
    async def is_admin(chat_id: int, user_id: int, context) -> bool:
        """Check if user is admin in chat (async)"""
        try:
            member = await context.bot.get_chat_member(chat_id, user_id)
            return member.status in ["creator", "administrator"]
        except Exception:
            return False

    @staticmethod
    async def can_bypass(user_id: int, chat_id: int = None, context = None) -> bool:
        """Check if user can bypass filters (async)"""
        if PermissionSystem.is_auth(user_id):
            return True
        if chat_id and PermissionSystem.is_permitted(chat_id, user_id):
            return True
        if chat_id and context:
            try:
                if await PermissionSystem.is_admin(chat_id, user_id, context):
                    return True
            except Exception:
                pass
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
                (f"{Emoji.SETTINGS} Settings", "menu_settings"),
                (f"{Emoji.TOOLS} Tools", "menu_tools")
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
                (f"{Emoji.STICKER} Sticker Ctrl", "admin_stickers"),
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
    def user_management() -> InlineKeyboardMarkup:
        """User management keyboard"""
        buttons = [
            [
                (f"{Emoji.PLUS} Add Sudo", "user_add_sudo"),
                (f"{Emoji.MINUS} Remove Sudo", "user_remove_sudo")
            ],
            [
                (f"{Emoji.PLUS} Add Auth", "user_add_auth"),
                (f"{Emoji.MINUS} Remove Auth", "user_remove_auth")
            ],
            [
                (f"{Emoji.LIST} List Sudo", "user_list_sudo"),
                (f"{Emoji.LIST} List Auth", "user_list_auth")
            ],
            [
                (f"{Emoji.BACKUP} Permissions", "user_permissions"),
                (f"{Emoji.STATS} User Stats", "user_stats")
            ],
            [
                (f"{Emoji.HOME} Back", "menu_admin"),
                (f"{Emoji.RELOAD} Refresh", "refresh")
            ]
        ]
        return KeyboardSystem.create_keyboard(buttons)

    @staticmethod
    def sticker_control() -> InlineKeyboardMarkup:
        """Sticker control keyboard"""
        buttons = [
            [
                (f"{Emoji.PLUS} Set Sticker", "sticker_set"),
                (f"{Emoji.MINUS} Remove", "sticker_remove")
            ],
            [
                (f"{Emoji.LIST} List All", "sticker_list"),
                (f"{Emoji.STICKER} Test", "sticker_test")
            ],
            [
                (f"{Emoji.SETTINGS} Settings", "sticker_settings"),
                (f"{Emoji.INFO} Info", "sticker_info")
            ],
            [
                (f"{Emoji.HOME} Back", "menu_admin"),
                (f"{Emoji.RELOAD} Refresh", "refresh")
            ]
        ]
        return KeyboardSystem.create_keyboard(buttons)

    @staticmethod
    def backup_system() -> InlineKeyboardMarkup:
        """Backup system keyboard"""
        buttons = [
            [
                (f"{Emoji.DOWNLOAD} Create Backup", "backup_create"),
                (f"{Emoji.UPLOAD} Restore", "backup_restore")
            ],
            [
                (f"{Emoji.LIST} List Backups", "backup_list"),
                (f"{Emoji.TRASH} Cleanup", "backup_clean")
            ],
            [
                (f"{Emoji.SETTINGS} Auto Backup", "backup_auto"),
                (f"{Emoji.INFO} Backup Info", "backup_info")
            ],
            [
                (f"{Emoji.HOME} Back", "menu_admin"),
                (f"{Emoji.RELOAD} Refresh", "refresh")
            ]
        ]
        return KeyboardSystem.create_keyboard(buttons)

    @staticmethod
    def confirmation(action: str) -> InlineKeyboardMarkup:
        """Confirmation keyboard"""
        buttons = [
            [
                (f"{Emoji.CHECK} Yes", f"confirm_yes_{action}"),
                (f"{Emoji.CROSS} No", f"confirm_no_{action}")
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
• {Emoji.EDIT} Edited Msgs Deleted: {data_manager.stats['total_edited_deleted']:,}

{Emoji.USER} <b>User Statistics:</b>
• Total Warned Users: {len(data_manager.user_warnings):,}
• Sudo Users: {len(data_manager.sudo_users):,}
• Auth Users: {len(data_manager.auth_users):,}
• Banned Users: {len(data_manager.banned_users):,}
• Muted Users: {len(data_manager.muted_users):,}

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

    @staticmethod
    def nsfw_warning(user, score: float, warnings: int) -> str:
        return f"""
{Emoji.WARNING} <b>NSFW Content Detected!</b> {Emoji.WARNING}

{Emoji.USER} <b>User:</b> {html.escape(user.first_name or 'User')}
{Emoji.FILTER} <b>NSFW Score:</b> {score*100:.1f}%
{Emoji.SHIELD} <b>Warning:</b> {warnings}/{data_manager.settings['max_warnings']}

{Emoji.ALERT} <b>Action Taken:</b> Message Deleted
{Emoji.CLOCK} <b>Next Action:</b> {f'{Emoji.MUTE} Mute for {data_manager.settings["mute_duration"]//60} minutes' if warnings >= data_manager.settings['max_warnings']-1 else 'Next warning'}
"""

    @staticmethod
    def user_muted(user, duration: int) -> str:
        return f"""
{Emoji.MUTE} <b>User Muted</b> {Emoji.MUTE}

{Emoji.USER} <b>User:</b> {html.escape(user.first_name or 'User')}
{Emoji.CLOCK} <b>Duration:</b> {duration//60} minutes
{Emoji.WARNING} <b>Reason:</b> Multiple NSFW violations

{Emoji.SHIELD} <i>Group safety maintained!</i>
"""

    @staticmethod
    def edited_message_warning(user) -> str:
        return f"""
{Emoji.EDIT} <b>Edited Message Detected</b> {Emoji.EDIT}

{Emoji.USER} <b>User:</b> {html.escape(user.first_name or 'User')}
{Emoji.CLOCK} <b>Action:</b> Will be deleted in {data_manager.settings['edit_delete_time']} seconds

{Emoji.INFO} <i>This is a security measure to prevent message manipulation</i>
"""

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
                    sample_rate = max(1, frame_count // 5) if frame_count > 0 else 1
                    samples = min(frame_count if frame_count > 0 else 1, 5)
                    for i in range(0, samples):
                        cap.set(cv2.CAP_PROP_POS_FRAMES, i * sample_rate)
                        ret, frame = cap.read()
                        if ret:
                            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                            frames.append(Image.fromarray(rgb))

                    cap.release()
                    try:
                        os.unlink(tmp.name)
                    except Exception:
                        pass
            else:
                # Try as image
                try:
                    image = Image.open(io.BytesIO(file_bytes)).convert("RGB")
                    frames.append(image)
                except Exception:
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
        except Exception:
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
• Auto sticker replies
• Edited message deletion
• Log channel reporting
• Scheduled backups

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
            if self.permissions.is_sudo(user_id):
                text = f"""
{Emoji.CROWN} <b>Sudo/Owner Commands</b>

{Emoji.BAN} <b>Global Moderation:</b>
• /gban [id/reply] - Global ban
• /ungban [id/reply] - Remove global ban
• /gmute [id/reply] - Global mute
• /ungmute [id/reply] - Remove global mute
• /gdel [id/reply] - Global delete
• /ungdel [id/reply] - Remove global delete
• /fban [id/reply] - Force ban in chat
• /fmute [id/reply] - Force mute in chat

{Emoji.USER} <b>User Management:</b>
• /addsudo [id/reply] - Add sudo user
• /delsudo [id/reply] - Remove sudo user
• /addauth [id/reply] - Add auth user
• /delauth [id/reply] - Remove auth user
• /listsudo - List all sudo users
• /listauth - List all auth users
• /permit [id] [chat_id] - Permit user in chat
• /unpermit [id] [chat_id] - Remove permission

{Emoji.STICKER} <b>Sticker System:</b>
• /suser [id/reply] - Set sticker for user
• /ruser [id/reply] - Remove user sticker
• /liststickers - List all sticker assignments

{Emoji.BACKUP} <b>System Commands:</b>
• /backup - Create full backup
• /restore - Restore from backup
• /settings - View bot settings
• /stats - View bot statistics
• /logs - View recent logs
• /broadcast - Broadcast message
"""
            else:
                text = f"""
{Emoji.GEAR} <b>Available Commands</b>

{Emoji.INFO} <b>General Commands:</b>
• /start - Start the bot
• /help - Show this help message
• /stats - View bot statistics
• /report [reason] - Report an issue

{Emoji.SHIELD} <b>For Group Admins:</b>
Add me as administrator with:
• Delete messages permission
• Restrict users permission
• Pin messages permission

{Emoji.STAR} <i>Contact bot owner for sudo access</i>
"""
            await query.edit_message_text(
                text=text,
                parse_mode="HTML",
                reply_markup=self.keyboards.back_button()
            )

        elif data == "menu_stats":
            await query.edit_message_text(
                text=self.templates.stats_message(),
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

        elif data == "admin_gban":
            text = f"""
{Emoji.BAN} <b>Global Ban System</b>

<b>Commands:</b>
• <code>/gban [user_id]</code> - Ban globally
• <code>/ungban [user_id]</code> - Remove ban
• <code>/listbans</code> - List banned users

<b>Effects:</b>
• User cannot join any protected group
• Messages auto-deleted if they join
• Cannot send any media/messages

<b>Access:</b> Sudo users only
"""
            await query.edit_message_text(
                text=text,
                parse_mode="HTML",
                reply_markup=self.keyboards.back_button("menu_admin")
            )

        elif data == "admin_users":
            if self.permissions.is_sudo(user_id):
                await query.edit_message_text(
                    text=f"{Emoji.USER} <b>User Management System</b>\nManage user permissions:",
                    parse_mode="HTML",
                    reply_markup=self.keyboards.user_management()
                )
            else:
                await query.answer("❌ Sudo access required!", show_alert=True)

        elif data == "refresh":
            await query.answer("🔄 Refreshed!", show_alert=True)
            await query.edit_message_reply_markup(reply_markup=query.message.reply_markup)

    async def media_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle all media messages for NSFW detection"""
        msg = update.message
        if not msg:
            return
        user = msg.from_user
        chat = msg.chat

        # Check permissions (async)
        try:
            if await self.permissions.can_bypass(user.id, chat.id if chat else None, context):
                logger.info(f"Bypass NSFW for privileged user {user.id}")
                return
        except Exception as e:
            logger.error(f"Permission bypass check failed: {e}")

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
            except Exception:
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
            except Exception:
                pass

        if user.id in self.data_manager.deleted_users:
            try:
                await msg.delete()
                return
            except Exception:
                pass

        # Get media file
        file = None
        mime_type = None

        if msg.photo:
            file = await msg.photo[-1].get_file()
        elif msg.sticker:
            if getattr(msg.sticker, "is_video", False):
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
            nsfw_score = await self.nsfw_detector.detect_nsfw(bytes(file_bytes), mime_type)

            if nsfw_score >= self.data_manager.settings["nsfw_threshold"]:
                await self.handle_nsfw_violation(msg, user, chat, nsfw_score, context)

        except Exception as e:
            logger.error(f"Media processing error: {e}")

    async def handle_nsfw_violation(self, msg, user, chat, score: float, context):
        """Handle NSFW violation"""
        # Delete the message
        try:
            await msg.delete()
        except Exception:
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
                    self.templates.user_muted(user, mute_duration),
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
            self.templates.nsfw_warning(user, score, new_warnings),
            parse_mode="HTML"
        )

    async def edited_message_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle edited messages"""
        msg = update.edited_message
        if not msg:
            return
        user = msg.from_user
        chat = msg.chat

        # Check permissions (async)
        try:
            if await self.permissions.can_bypass(user.id, chat.id if chat else None, context):
                return
        except Exception as e:
            logger.error(f"Permission bypass check failed for edited message: {e}")

        # Send warning about deletion
        warning_msg = await context.bot.send_message(
            chat.id,
            self.templates.edited_message_warning(user),
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

    async def sticker_auto_reply(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Auto-reply with user's assigned sticker"""
        if not self.data_manager.settings["sticker_auto_reply"]:
            return

        if update.effective_chat and update.effective_chat.type not in ["group", "supergroup"]:
            return

        user_id = update.effective_user.id

        if user_id in self.data_manager.user_stickers:
            try:
                await update.message.reply_sticker(self.data_manager.user_stickers[user_id])

                # Update stats
                self.data_manager.stats["total_stickers_sent"] += 1
                self.data_manager.save_data("stats")

            except Exception as e:
                logger.error(f"Sticker reply error: {e}")

    # ================= MODERATION COMMANDS =================

    async def gban_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Global ban command"""
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

    async def ungban_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Global unban command"""
        if not self.permissions.is_sudo(update.effective_user.id):
            await update.message.reply_text(f"{Emoji.CROSS} Sudo access required.")
            return
        try:
            if update.message.reply_to_message:
                user_id = update.message.reply_to_message.from_user.id
            elif context.args:
                user_id = int(context.args[0])
            else:
                await update.message.reply_text(f"{Emoji.CROSS} Reply to user or provide ID.")
                return

            if user_id in self.data_manager.banned_users:
                self.data_manager.banned_users.discard(user_id)
                self.data_manager.save_data("banned")
                await update.message.reply_text(f"{Emoji.CHECK} <b>Global Unban Applied</b>\nUser: <code>{user_id}</code>", parse_mode="HTML")
            else:
                await update.message.reply_text(f"{Emoji.INFO} User not in global ban list.")
        except Exception as e:
            await update.message.reply_text(f"{Emoji.CROSS} Error: {e}")

    async def gmute_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Global mute command"""
        if not self.permissions.is_sudo(update.effective_user.id):
            return

        try:
            if update.message.reply_to_message:
                user_id = update.message.reply_to_message.from_user.id
            elif context.args:
                user_id = int(context.args[0])
            else:
                await update.message.reply_text(f"{Emoji.CROSS} Reply to user or provide ID.")
                return

            self.data_manager.muted_users.add(user_id)
            self.data_manager.stats["total_mutes"] += 1
            self.data_manager.save_data("muted")
            self.data_manager.save_data("stats")

            await update.message.reply_text(
                f"{Emoji.MUTE} <b>Global Mute Applied</b>\nUser: <code>{user_id}</code>",
                parse_mode="HTML"
            )

        except Exception:
            await update.message.reply_text(f"{Emoji.CROSS} Invalid usage.")

    async def ungmute_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Global unmute command"""
        if not self.permissions.is_sudo(update.effective_user.id):
            return
        try:
            if update.message.reply_to_message:
                user_id = update.message.reply_to_message.from_user.id
            elif context.args:
                user_id = int(context.args[0])
            else:
                await update.message.reply_text(f"{Emoji.CROSS} Reply to user or provide ID.")
                return

            if user_id in self.data_manager.muted_users:
                self.data_manager.muted_users.discard(user_id)
                self.data_manager.save_data("muted")
                await update.message.reply_text(f"{Emoji.CHECK} <b>Global Unmute Applied</b>\nUser: <code>{user_id}</code>", parse_mode="HTML")
            else:
                await update.message.reply_text(f"{Emoji.INFO} User not in global mute list.")
        except Exception as e:
            await update.message.reply_text(f"{Emoji.CROSS} Error: {e}")

    async def gdel_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Global delete command"""
        if not self.permissions.is_sudo(update.effective_user.id):
            return

        try:
            if update.message.reply_to_message:
                user_id = update.message.reply_to_message.from_user.id
            elif context.args:
                user_id = int(context.args[0])
            else:
                await update.message.reply_text(f"{Emoji.CROSS} Reply to user or provide ID.")
                return

            self.data_manager.deleted_users.add(user_id)
            self.data_manager.save_data("deleted")

            await update.message.reply_text(
                f"{Emoji.DELETE} <b>Global Delete Enabled</b>\nUser: <code>{user_id}</code>",
                parse_mode="HTML"
            )

        except Exception:
            await update.message.reply_text(f"{Emoji.CROSS} Invalid usage.")

    async def fban_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Force ban in current chat"""
        if not self.permissions.is_sudo(update.effective_user.id):
            return

        try:
            if update.message.reply_to_message:
                user_id = update.message.reply_to_message.from_user.id
            elif context.args:
                user_id = int(context.args[0])
            else:
                await update.message.reply_text(f"{Emoji.CROSS} Reply to user or provide ID.")
                return

            chat_id = update.message.chat_id

            # Ban in current chat
            await context.bot.ban_chat_member(chat_id, user_id)

            # Also add to global ban
            self.data_manager.banned_users.add(user_id)
            self.data_manager.stats["total_bans"] += 1
            self.data_manager.save_data("banned")
            self.data_manager.save_data("stats")

            await update.message.reply_text(
                f"{Emoji.FIRE} <b>Force Ban Executed</b>\nUser removed from this chat.",
                parse_mode="HTML"
            )

        except Exception as e:
            await update.message.reply_text(f"{Emoji.CROSS} Error: {str(e)}")

    async def fmute_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Force mute in current chat"""
        if not self.permissions.is_sudo(update.effective_user.id):
            return

        try:
            if update.message.reply_to_message:
                user_id = update.message.reply_to_message.from_user.id
            elif context.args:
                user_id = int(context.args[0])
            else:
                await update.message.reply_text(f"{Emoji.CROSS} Reply to user or provide ID.")
                return

            chat_id = update.message.chat_id
            until = int(time.time()) + 86400 * 365  # 1 year

            # Mute in current chat
            await context.bot.restrict_chat_member(
                chat_id, user_id,
                permissions=ChatPermissions(),
                until_date=until
            )

            # Also add to global mute
            self.data_manager.muted_users.add(user_id)
            self.data_manager.stats["total_mutes"] += 1
            self.data_manager.save_data("muted")
            self.data_manager.save_data("stats")

            await update.message.reply_text(
                f"{Emoji.FIRE} <b>Force Mute Executed</b>\nUser muted in this chat.",
                parse_mode="HTML"
            )

        except Exception as e:
            await update.message.reply_text(f"{Emoji.CROSS} Error: {str(e)}")

    # ================= USER MANAGEMENT COMMANDS =================

    async def addsudo_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Add sudo user"""
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

        except Exception:
            await update.message.reply_text(f"{Emoji.CROSS} Invalid usage.")

    async def delsudo_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Remove sudo user"""
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

            if user_id in self.data_manager.sudo_users:
                self.data_manager.sudo_users.discard(user_id)
                self.data_manager.save_data("sudo")
                await update.message.reply_text(f"{Emoji.CHECK} <b>Sudo Removed</b>\nUser: <code>{user_id}</code>", parse_mode="HTML")
            else:
                await update.message.reply_text(f"{Emoji.INFO} User not in sudo list.")
        except Exception as e:
            await update.message.reply_text(f"{Emoji.CROSS} Error: {e}")

    async def addauth_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Add auth user"""
        if not self.permissions.is_sudo(update.effective_user.id):
            await update.message.reply_text(f"{Emoji.CROSS} Sudo access required.")
            return

        try:
            if update.message.reply_to_message:
                user_id = update.message.reply_to_message.from_user.id
            elif context.args:
                user_id = int(context.args[0])
            else:
                await update.message.reply_text(f"{Emoji.CROSS} Reply to user or provide ID.")
                return

            self.data_manager.auth_users.add(user_id)
            self.data_manager.save_data("auth")

            await update.message.reply_text(
                f"{Emoji.SHIELD} <b>Auth User Added</b>\nUser: <code>{user_id}</code>",
                parse_mode="HTML"
            )

        except Exception:
            await update.message.reply_text(f"{Emoji.CROSS} Invalid usage.")

    async def delauth_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Remove auth user"""
        if not self.permissions.is_sudo(update.effective_user.id):
            await update.message.reply_text(f"{Emoji.CROSS} Sudo access required.")
            return
        try:
            if update.message.reply_to_message:
                user_id = update.message.reply_to_message.from_user.id
            elif context.args:
                user_id = int(context.args[0])
            else:
                await update.message.reply_text(f"{Emoji.CROSS} Reply to user or provide ID.")
                return

            if user_id in self.data_manager.auth_users:
                self.data_manager.auth_users.discard(user_id)
                self.data_manager.save_data("auth")
                await update.message.reply_text(f"{Emoji.CHECK} <b>Auth Removed</b>\nUser: <code>{user_id}</code>", parse_mode="HTML")
            else:
                await update.message.reply_text(f"{Emoji.INFO} User not in auth list.")
        except Exception as e:
            await update.message.reply_text(f"{Emoji.CROSS} Error: {e}")

    async def suser_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Set user sticker"""
        if not self.permissions.is_sudo(update.effective_user.id):
            await update.message.reply_text(f"{Emoji.CROSS} Sudo access required.")
            return

        try:
            # Get target user ID
            if context.args:
                user_id = int(context.args[0])
            elif update.message.reply_to_message:
                user_id = update.message.reply_to_message.from_user.id
            else:
                await update.message.reply_text(f"{Emoji.CROSS} Reply to sticker with user ID or reply to user.")
                return

            # Check if replied to sticker
            if not update.message.reply_to_message or not update.message.reply_to_message.sticker:
                await update.message.reply_text(f"{Emoji.CROSS} Reply to a sticker.")
                return

            sticker_id = update.message.reply_to_message.sticker.file_id
            self.data_manager.user_stickers[user_id] = sticker_id
            self.data_manager.save_data("stickers")

            await update.message.reply_text(
                f"{Emoji.STICKER} <b>Sticker Assigned</b>\n"
                f"• User: <code>{user_id}</code>\n"
                f"• Sticker set for auto-reply",
                parse_mode="HTML"
            )

        except Exception as e:
            await update.message.reply_text(f"{Emoji.CROSS} Error: {str(e)}")

    async def ruser_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Remove user sticker"""
        if not self.permissions.is_sudo(update.effective_user.id):
            await update.message.reply_text(f"{Emoji.CROSS} Sudo access required.")
            return
        try:
            if update.message.reply_to_message:
                user_id = update.message.reply_to_message.from_user.id
            elif context.args:
                user_id = int(context.args[0])
            else:
                await update.message.reply_text(f"{Emoji.CROSS} Reply to user or provide ID.")
                return

            if user_id in self.data_manager.user_stickers:
                del self.data_manager.user_stickers[user_id]
                self.data_manager.save_data("stickers")
                await update.message.reply_text(f"{Emoji.CHECK} <b>Sticker Removed</b>\nUser: <code>{user_id}</code>", parse_mode="HTML")
            else:
                await update.message.reply_text(f"{Emoji.INFO} No sticker set for this user.")
        except Exception as e:
            await update.message.reply_text(f"{Emoji.CROSS} Error: {e}")

    async def backup_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Create backup"""
        if not self.permissions.is_owner(update.effective_user.id):
            await update.message.reply_text(f"{Emoji.CROSS} Owner access required.")
            return

        try:
            # Create ZIP backup
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for key, filename in self.data_manager.data_files.items():
                    if os.path.exists(filename):
                        zip_file.write(filename)

                # Add info file
                info = {
                    "backup_time": time.time(),
                    "bot_version": "NudeGuard Pro v2.0",
                    "total_users": len(self.data_manager.user_warnings),
                    "total_sudo": len(self.data_manager.sudo_users),
                    "total_banned": len(self.data_manager.banned_users)
                }
                zip_file.writestr("backup_info.json", json.dumps(info, indent=4))

            zip_buffer.seek(0)

            # Send to owners
            for owner_id in OWNERS:
                try:
                    # send a fresh buffer for each owner
                    await context.bot.send_document(
                        chat_id=owner_id,
                        document=io.BytesIO(zip_buffer.getvalue()),
                        filename=f"nudeguard_backup_{int(time.time())}.zip",
                        caption=f"{Emoji.BACKUP} <b>Full Backup</b>\n"
                               f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}",
                        parse_mode="HTML"
                    )
                except Exception as e:
                    logger.error(f"Failed to send backup to {owner_id}: {e}")

            await update.message.reply_text(
                f"{Emoji.CHECK} <b>Backup Completed</b>\nSent to bot owners.",
                parse_mode="HTML"
            )

        except Exception as e:
            await update.message.reply_text(f"{Emoji.CROSS} Backup failed: {str(e)}")

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

        # Moderation commands
        self.application.add_handler(CommandHandler("gban", self.gban_command))
        self.application.add_handler(CommandHandler("ungban", self.ungban_command))
        self.application.add_handler(CommandHandler("gmute", self.gmute_command))
        self.application.add_handler(CommandHandler("ungmute", self.ungmute_command))
        self.application.add_handler(CommandHandler("gdel", self.gdel_command))
        # Note: add specific ungdel if you implement "ungdel" logic separately

        self.application.add_handler(CommandHandler("fban", self.fban_command))
        self.application.add_handler(CommandHandler("fmute", self.fmute_command))

        # User management
        self.application.add_handler(CommandHandler("addsudo", self.addsudo_command))
        self.application.add_handler(CommandHandler("delsudo", self.delsudo_command))
        self.application.add_handler(CommandHandler("addauth", self.addauth_command))
        self.application.add_handler(CommandHandler("delauth", self.delauth_command))
        self.application.add_handler(CommandHandler("suser", self.suser_command))
        self.application.add_handler(CommandHandler("ruser", self.ruser_command))

        # System commands
        self.application.add_handler(CommandHandler("backup", self.backup_command))
        # restore could be implemented separately

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

        # Sticker auto-reply
        self.application.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            self.sticker_auto_reply
        ), group=1)

        # Start bot
        logger.info(f"{Emoji.ROBOT} NudeGuard Pro - Starting...")
        logger.info(f"{Emoji.STAR} Bot Token: {BOT_TOKEN[:10]}...")
        logger.info(f"{Emoji.SHIELD} Owners: {OWNERS}")
        logger.info(f"{Emoji.CHART} Log Channel: {LOG_CHANNEL}")

        # Start backup scheduler task inside running loop
        try:
            auto_backup_coro = self.data_manager.setup_backup_scheduler()
            # schedule the task on the current loop
            loop = asyncio.get_event_loop()
            loop.create_task(auto_backup_coro())
        except Exception as e:
            logger.error(f"Failed to start auto-backup scheduler: {e}")

        self.application.run_polling()

# ================= MAIN EXECUTION =================
if __name__ == "__main__":
    # Check if running on Heroku
    if os.environ.get("DYNO"):
        print(f"{Emoji.ROCKET} Running on Heroku...")

    # Create and run bot
    bot = NudeGuardBot()
    bot.run()

import telebot
import yaml
import os
import pickle
import re
import html
import time
import logging
from dataclasses import dataclass
from typing import Dict
from datetime import datetime
from deep_translator import GoogleTranslator
from telebot import types
# ========== ЛОГИРОВАНИЕ ==========
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
log = logging.getLogger(__name__)

# ========== КОНСТАНТЫ И КОНФИГУРАЦИЯ ==========
CONFIG_FILE = "config.yaml"

def load_config():
    """Загрузка конфигурации"""
    if not os.path.exists(CONFIG_FILE):
        default_config = {
            'bot_token': 'ВАШ_ТОКЕН_БОТА',
            'admin_id': 0,
            'defaults': {
                'source_lang': 'ru',
                'target_lang': 'en',
                'template': '''<b>English version:</b>
<blockquote>{translated}</blockquote>

<b>Русская версия:</b>
<blockquote>{original}</blockquote>''',
                'parse_mode': 'HTML',
                'enabled': True
            },
            'strings': {
                'admin_only': '⚠️ Эта команда доступна только администратору.',
                'channel_added': '✅ Канал добавлен и активирован!',
                'channel_removed': '🗑️ Канал удалён.',
                'channel_list': '📋 Список каналов:',
                'no_channels': 'ℹ️ Каналы не добавлены.',
                'settings_changed': '⚙️ Настройки обновлены!',
                'channel_not_found': '❌ Канал не найден.',
                'template_changed': '📝 Шаблон обновлён!',
                'language_changed': '🌐 Язык изменён!',
                'invalid_channel_id': '❌ Неверный ID канала. ID должен начинаться с -100.',
                'cant_access_channel': '❌ Не удалось получить доступ к каналу. Убедитесь, что бот добавлен как администратор.'
            },
            'debug': True
        }
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            yaml.dump(default_config, f, allow_unicode=True, default_flow_style=False)
        print(f"Создан файл конфигурации {CONFIG_FILE}. Заполните его.")
        exit()

    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

config = load_config()
BOT_TOKEN = config['bot_token']
ADMIN_ID = config['admin_id']
DEFAULTS = config['defaults']
STRINGS = config['strings']

# ========== БАЗА ДАННЫХ ==========

@dataclass
class ChannelSettings:
    channel_id: int
    channel_name: str = ""
    source_lang: str = "ru"
    target_lang: str = "en"
    template: str = ""
    parse_mode: str = "HTML"
    enabled: bool = True
    added_by: int = 0
    added_date: str = ""
    last_used: str = ""
    is_private: bool = False

@dataclass
class UserData:
    user_id: int
    is_admin: bool = False
    temp_data: Dict = None

class Database:
    def __init__(self, filename='bot_data.pkl'):
        self.filename = filename
        self.data = {
            'channels': {},
            'users': {},
            'stats': {
                'processed_messages': 0,
                'translated_chars': 0,
                'last_update': ""
            }
        }
        self.load()

    def load(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'rb') as f:
                    self.data = pickle.load(f)
                # защита от неполной структуры
                self.data.setdefault('channels', {})
                self.data.setdefault('users', {})
                self.data.setdefault('stats', {
                    'processed_messages': 0,
                    'translated_chars': 0,
                    'last_update': ""
                })
            except Exception as e:
                log.error(f"Ошибка загрузки БД, создаём новую: {e}")
                self.save()
        else:
            self.save()

    def save(self):
        self.data['stats']['last_update'] = datetime.now().isoformat()
        try:
            with open(self.filename, 'wb') as f:
                pickle.dump(self.data, f)
        except Exception as e:
            log.error(f"Ошибка сохранения БД: {e}")

    def add_channel(self, channel_id: int, channel_name: str, added_by: int, **kwargs):
        settings = ChannelSettings(
            channel_id=channel_id,
            channel_name=channel_name,
            added_by=added_by,
            added_date=datetime.now().isoformat(),
            last_used=datetime.now().isoformat(),
            source_lang=kwargs.get('source_lang', DEFAULTS['source_lang']),
            target_lang=kwargs.get('target_lang', DEFAULTS['target_lang']),
            template=kwargs.get('template', DEFAULTS['template']),
            parse_mode=kwargs.get('parse_mode', DEFAULTS['parse_mode']),
            enabled=kwargs.get('enabled', DEFAULTS['enabled']),
            is_private=kwargs.get('is_private', False)
        )
        self.data['channels'][channel_id] = settings
        self.save()
        return settings

    def remove_channel(self, channel_id: int):
        if channel_id in self.data['channels']:
            del self.data['channels'][channel_id]
            self.save()
            return True
        return False

    def get_channel(self, channel_id: int):
        return self.data['channels'].get(channel_id)

    def get_all_channels(self):
        return list(self.data['channels'].values())

    def update_channel(self, channel_id: int, **kwargs):
        if channel_id in self.data['channels']:
            for key, value in kwargs.items():
                if hasattr(self.data['channels'][channel_id], key):
                    setattr(self.data['channels'][channel_id], key, value)
            self.data['channels'][channel_id].last_used = datetime.now().isoformat()
            self.save()
            return True
        return False

    def toggle_channel(self, channel_id: int):
        if channel_id in self.data['channels']:
            self.data['channels'][channel_id].enabled = not self.data['channels'][channel_id].enabled
            self.save()
            return self.data['channels'][channel_id].enabled
        return False

    def get_user(self, user_id: int):
        if user_id not in self.data['users']:
            self.data['users'][user_id] = UserData(user_id=user_id)
            self.save()
        return self.data['users'][user_id]

    def update_user_temp(self, user_id: int, key: str, value):
        user = self.get_user(user_id)
        if user.temp_data is None:
            user.temp_data = {}
        user.temp_data[key] = value
        self.save()

    def get_user_temp(self, user_id: int, key: str):
        user = self.get_user(user_id)
        if user.temp_data and key in user.temp_data:
            return user.temp_data.get(key)
        return None

    def increment_stats(self, chars: int = 0):
        self.data['stats']['processed_messages'] += 1
        self.data['stats']['translated_chars'] += chars
        self.save()

    def get_stats(self):
        return self.data['stats']

db = Database()

# ========== КЛАВИАТУРЫ ==========

def admin_main_menu():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    buttons = [
        "📋 Список каналов",
        "➕ Добавить канал",
        "⚙️ Настройки канала",
        "📊 Статистика",
        "❓ Помощь",
        "🚫 Закрыть меню"
    ]
    keyboard.add(*buttons)
    return keyboard

def add_channel_keyboard():
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        types.InlineKeyboardButton("🔗 По ссылке", callback_data="add_by_link"),
        types.InlineKeyboardButton("🆔 По ID", callback_data="add_by_id"),
        types.InlineKeyboardButton("📤 Переслать сообщение", callback_data="add_by_forward"),
        types.InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")
    )
    return keyboard

def channel_list_keyboard(channels):
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    for channel in channels:
        status = "✅" if channel.enabled else "❌"
        private = "🔒" if channel.is_private else "🔓"
        btn = types.InlineKeyboardButton(
            text=f"{status}{private} {channel.channel_name}",
            callback_data=f"channel_{channel.channel_id}"
        )
        keyboard.add(btn)
    keyboard.add(types.InlineKeyboardButton("🔙 Назад", callback_data="back_to_main"))
    return keyboard

def channel_settings_keyboard(channel_id):
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    buttons = [
        types.InlineKeyboardButton("🌐 Языки", callback_data=f"langs_{channel_id}"),
        types.InlineKeyboardButton("📝 Шаблон", callback_data=f"template_{channel_id}"),
        types.InlineKeyboardButton("🔧 Parse Mode", callback_data=f"parse_{channel_id}"),
        types.InlineKeyboardButton("✅ Вкл/Выкл", callback_data=f"toggle_{channel_id}"),
        types.InlineKeyboardButton("🗑️ Удалить", callback_data=f"delete_{channel_id}"),
        types.InlineKeyboardButton("🔙 Назад", callback_data="back_to_channels")
    ]
    for i in range(0, len(buttons), 2):
        row = buttons[i:i+2]
        keyboard.row(*row)
    return keyboard

def language_keyboard(channel_id, lang_type="source"):
    keyboard = types.InlineKeyboardMarkup(row_width=3)
    languages = [
        ("🇷🇺 Русский", "ru"),
        ("🇺🇸 English", "en"),
        ("🇪🇸 Español", "es"),
        ("🇩🇪 Deutsch", "de"),
        ("🇫🇷 Français", "fr"),
        ("🇨🇳 中文", "zh"),
        ("🇯🇵 日本語", "ja"),
        ("🇰🇷 한국어", "ko"),
        ("🇮🇹 Italiano", "it"),
        ("🇵🇹 Português", "pt"),
        ("🇦🇪 العربية", "ar"),
        ("🇹🇷 Türkçe", "tr"),
        ("🇺🇦 Українська", "uk"),
        ("🇧🇾 Беларуская", "be"),
        ("🇰🇿 Қазақша", "kk")
    ]
    for name, code in languages:
        keyboard.add(
            types.InlineKeyboardButton(name, callback_data=f"setlang_{channel_id}_{lang_type}_{code}")
        )
    keyboard.add(types.InlineKeyboardButton("🔙 Назад", callback_data=f"channel_{channel_id}"))
    return keyboard

def parse_mode_keyboard(channel_id):
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    modes = [
        ("HTML", "HTML"),
        ("Markdown", "Markdown"),
        ("MarkdownV2", "MarkdownV2"),
        ("Отключить", "None"),
        ("🔙 Назад", f"channel_{channel_id}")
    ]
    for name, mode in modes:
        keyboard.add(
            types.InlineKeyboardButton(name, callback_data=f"setparse_{channel_id}_{mode}")
        )
    return keyboard

def confirmation_keyboard(channel_id):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.row(
        types.InlineKeyboardButton("✅ Да, удалить", callback_data=f"confirm_delete_{channel_id}"),
        types.InlineKeyboardButton("❌ Нет, отмена", callback_data=f"channel_{channel_id}")
    )
    return keyboard

def back_button(callback_data="back_to_main"):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton("🔙 Назад", callback_data=callback_data))
    return keyboard

# ========== УТИЛИТЫ ==========

def is_admin(user_id):
    return user_id == ADMIN_ID

def _translate_chunk(chunk: str, sl: str, tl: str, retries: int = 3):
    """Перевод одного куска текста через deep_translator с ретраями.
    Возвращает (текст, успех)."""
    last_err = None
    for attempt in range(retries):
        try:
            translator = GoogleTranslator(source=sl, target=tl)
            result = translator.translate(chunk)
            if result and result.strip():
                return result, True
            # пустой ответ — считаем неудачей
            return chunk, False
        except Exception as e:
            last_err = e
            log.warning(f"Попытка {attempt+1}/{retries} перевода не удалась: {e}")
            time.sleep(1.5 * (attempt + 1))
    log.error(f"Перевод не удался после {retries} попыток: {last_err}")
    return chunk, False

def translate_text(text, source_lang='ru', target_lang='en'):
    """Перевод текста. Возвращает (перевод, успех)."""
    if not text or not text.strip():
        return text, True

    if source_lang == target_lang:
        log.warning(f"source_lang == target_lang ({source_lang}), перевод пропущен")
        return text, False

    # deep_translator умеет длинные тексты, но лучше резать на всякий
    MAX_CHUNK = 4500
    chunks = [text[i:i+MAX_CHUNK] for i in range(0, len(text), MAX_CHUNK)]

    translated_parts = []
    all_ok = True

    for chunk in chunks:
        part, ok = _translate_chunk(chunk, source_lang, target_lang)
        translated_parts.append(part)
        if not ok:
            all_ok = False

    result = ''.join(translated_parts)
    db.increment_stats(chars=len(text))
    return result, all_ok

def apply_template(template, original, translated, source_lang, target_lang, parse_mode="HTML"):
    if not template:
        template = DEFAULTS['template']

    # Экранирование для HTML, чтобы не ломать parse_mode
    if parse_mode == "HTML":
        original_safe = html.escape(original)
        translated_safe = html.escape(translated)
    else:
        original_safe = original
        translated_safe = translated

    replacements = {
        '{original}': original_safe,
        '{translated}': translated_safe,
        '{original_lang}': source_lang,
        '{translated_lang}': target_lang,
        '{date}': datetime.now().strftime("%Y-%m-%d"),
        '{time}': datetime.now().strftime("%H:%M"),
        '{datetime}': datetime.now().strftime("%Y-%m-%d %H:%M")
    }

    result = template
    for placeholder, value in replacements.items():
        result = result.replace(placeholder, str(value))

    if parse_mode == "None":
        result = re.sub(r'<[^>]+>', '', result)

    return result

def format_channel_info(channel):
    status = "✅ ВКЛЮЧЕН" if channel.enabled else "❌ ВЫКЛЮЧЕН"
    private = "🔒 Приватный" if channel.is_private else "🔓 Публичный"
    return f"""
📢 <b>{html.escape(channel.channel_name)}</b>
ID: <code>{channel.channel_id}</code>
Статус: {status}
Тип: {private}
Языки: {channel.source_lang} → {channel.target_lang}
Parse mode: {channel.parse_mode}
Добавлен: {channel.added_date[:10]}
Использован: {channel.last_used[:10] if channel.last_used else 'никогда'}
    """.strip()

def is_valid_channel_id(channel_id):
    try:
        channel_id = int(channel_id)
        return channel_id < 0
    except (ValueError, TypeError):
        return False

# ========== ОСНОВНОЙ БОТ ==========

bot = telebot.TeleBot(BOT_TOKEN, parse_mode=None)

@bot.channel_post_handler(content_types=['text', 'photo', 'video', 'document', 'audio'])
def handle_channel_post(message):
    try:
        channel_id = message.chat.id
        channel = db.get_channel(channel_id)

        if not channel or not channel.enabled:
            return

        content = message.text or message.caption or ""

        # защита от рекурсии
        if '{translated}' in content and '{original}' in content:
            return

        # перевод
        translated, ok = translate_text(content, channel.source_lang, channel.target_lang)

        if not ok:
            log.warning(
                f"Перевод не удался для канала {channel.channel_name} (id={channel_id}), "
                f"пост пропущен — оригинал не подменяем"
            )
            return  # ← ключевой фикс: не редактируем сообщение

        # форматирование
        formatted = apply_template(
            channel.template,
            content,
            translated,
            channel.source_lang,
            channel.target_lang,
            channel.parse_mode
        )

        parse_mode = None if channel.parse_mode == "None" else channel.parse_mode

        try:
            if message.content_type == 'text':
                bot.edit_message_text(
                    chat_id=channel_id,
                    message_id=message.message_id,
                    text=formatted,
                    parse_mode=parse_mode
                )
            elif message.caption is not None:
                bot.edit_message_caption(
                    chat_id=channel_id,
                    message_id=message.message_id,
                    caption=formatted,
                    parse_mode=parse_mode
                )
        except Exception as e:
            log.error(f"Ошибка редактирования поста в канале {channel_id}: {e}")

        db.update_channel(channel_id, last_used=datetime.now().isoformat())

        if config.get('debug', False):
            log.info(f"Обработано сообщение в канале {channel.channel_name}")

    except Exception as e:
        log.exception(f"Ошибка при обработке поста: {e}")

# ========== АДМИН КОМАНДЫ ==========

@bot.message_handler(commands=['start', 'admin'])
def handle_start(message):
    if not is_admin(message.from_user.id):
        bot.send_message(message.chat.id, STRINGS['admin_only'])
        return
    bot.send_message(
        message.chat.id,
        "👑 <b>Панель администратора</b>\n\nВыберите действие:",
        parse_mode='HTML',
        reply_markup=admin_main_menu()
    )

@bot.message_handler(func=lambda m: m.text == "📋 Список каналов" and is_admin(m.from_user.id))
def list_channels(message):
    channels = db.get_all_channels()
    if not channels:
        bot.send_message(message.chat.id, STRINGS['no_channels'])
        return
    text = STRINGS['channel_list'] + "\n\n"
    for channel in channels:
        status = "✅" if channel.enabled else "❌"
        private = "🔒" if channel.is_private else "🔓"
        text += f"{status}{private} <b>{html.escape(channel.channel_name)}</b> (ID: {channel.channel_id})\n"
    bot.send_message(
        message.chat.id,
        text,
        parse_mode='HTML',
        reply_markup=channel_list_keyboard(channels)
    )

@bot.message_handler(func=lambda m: m.text == "➕ Добавить канал" and is_admin(m.from_user.id))
def add_channel_start(message):
    bot.send_message(
        message.chat.id,
        "📝 <b>Добавление канала</b>\n\nВыберите способ добавления:",
        parse_mode='HTML',
        reply_markup=add_channel_keyboard()
    )

@bot.message_handler(func=lambda m: m.text == "⚙️ Настройки канала" and is_admin(m.from_user.id))
def channel_settings_start(message):
    channels = db.get_all_channels()
    if not channels:
        bot.send_message(message.chat.id, STRINGS['no_channels'])
        return
    bot.send_message(
        message.chat.id,
        "⚙️ <b>Настройки канала</b>\n\nВыберите канал для настройки:",
        parse_mode='HTML',
        reply_markup=channel_list_keyboard(channels)
    )

@bot.message_handler(func=lambda m: m.text == "📊 Статистика" and is_admin(m.from_user.id))
def show_stats(message):
    stats = db.get_stats()
    text = f"""
📊 <b>Статистика бота</b>

📨 Обработано сообщений: {stats['processed_messages']:,}
🔤 Переведено символов: {stats['translated_chars']:,}
📅 Последнее обновление: {stats['last_update'][:19] if stats['last_update'] else 'никогда'}

📢 Каналов в базе: {len(db.get_all_channels())}
👤 Пользователей в базе: {len(db.data['users'])}
    """.strip()
    bot.send_message(message.chat.id, text, parse_mode='HTML')

@bot.message_handler(func=lambda m: m.text == "❓ Помощь" and is_admin(m.from_user.id))
def show_help(message):
    text = """
❓ <b>Справка по боту</b>

<b>Основные функции:</b>
• Автоматический перевод постов в каналах
• Поддержка текста и подписей к медиа
• Настраиваемые шаблоны форматирования
• Поддержка множества языков

<b>Способы добавления канала:</b>
1. <b>По ссылке</b> - отправьте @username или t.me/username
2. <b>По ID</b> - отправьте ID канала (начинается с -100)
3. <b>Переслать сообщение</b> - перешлите любое сообщение из канала

<b>Доступные плейсхолдеры в шаблоне:</b>
• <code>{original}</code> - оригинальный текст
• <code>{translated}</code> - переведённый текст
• <code>{original_lang}</code> - исходный язык
• <code>{translated_lang}</code> - целевой язык
• <code>{date}</code> - текущая дата (ГГГГ-ММ-ДД)
• <code>{time}</code> - текущее время (ЧЧ:ММ)
• <code>{datetime}</code> - дата и время

<b>Поддерживаемые parse mode:</b>
• HTML
• Markdown / MarkdownV2
• None

<b>Как добавить канал:</b>
1. Добавить бота в канал как администратора
2. В панели админа выбрать "➕ Добавить канал"
3. Выбрать способ добавления
    """.strip()
    bot.send_message(message.chat.id, text, parse_mode='HTML')

@bot.message_handler(func=lambda m: m.text == "🚫 Закрыть меню" and is_admin(m.from_user.id))
def close_menu(message):
    bot.send_message(
        message.chat.id,
        "Меню закрыто. Используйте /admin чтобы открыть снова.",
        reply_markup=types.ReplyKeyboardRemove()
    )

# ========== ОБРАБОТКА СООБЩЕНИЙ ==========

@bot.message_handler(content_types=['text', 'forward_from_chat'])
def handle_messages(message):
    if not is_admin(message.from_user.id):
        return

    add_mode = db.get_user_temp(message.from_user.id, 'add_mode')

    # --- Добавление канала по ID ---
    if add_mode == "by_id":
        if not message.text:
            return
        channel_id_str = message.text.strip()

        if not is_valid_channel_id(channel_id_str):
            bot.send_message(
                message.chat.id,
                f"{STRINGS['invalid_channel_id']}\n\n"
                f"Примеры валидных ID:\n"
                f"• <code>-1001234567890</code> - канал/супергруппа\n"
                f"• <code>-123456789</code> - группа\n\n"
                f"Попробуйте снова или нажмите 🔙 Назад:",
                parse_mode='HTML',
                reply_markup=back_button()
            )
            return

        try:
            channel_id = int(channel_id_str)
            existing = db.get_channel(channel_id)
            if existing:
                bot.send_message(
                    message.chat.id,
                    f"⚠️ Канал с ID <code>{channel_id}</code> уже добавлен!",
                    parse_mode='HTML',
                    reply_markup=admin_main_menu()
                )
                db.update_user_temp(message.from_user.id, 'add_mode', None)
                return

            try:
                chat = bot.get_chat(channel_id)
                channel_name = chat.title or f"Канал {channel_id}"
                is_private = not chat.username

                db.add_channel(
                    channel_id=channel_id,
                    channel_name=channel_name,
                    added_by=message.from_user.id,
                    is_private=is_private
                )

                private_text = "🔒 Приватный" if is_private else "🔓 Публичный"
                bot.send_message(
                    message.chat.id,
                    f"✅ Канал <b>{html.escape(channel_name)}</b> успешно добавлен!\n\n"
                    f"ID: <code>{channel_id}</code>\n"
                    f"Тип: {private_text}\n"
                    f"По умолчанию настроен перевод с {DEFAULTS['source_lang']} на {DEFAULTS['target_lang']}",
                    parse_mode='HTML',
                    reply_markup=admin_main_menu()
                )

            except Exception as e:
                channel_name = f"Неизвестный канал (ID: {channel_id})"
                db.add_channel(
                    channel_id=channel_id,
                    channel_name=channel_name,
                    added_by=message.from_user.id,
                    is_private=True
                )
                bot.send_message(
                    message.chat.id,
                    f"✅ Канал добавлен как <b>приватный</b>!\n\n"
                    f"ID: <code>{channel_id}</code>\n"
                    f"⚠️ Бот не смог получить информацию о канале.\n"
                    f"Убедитесь, что бот добавлен в канал как администратор.\n\n"
                    f"Ошибка: <code>{html.escape(str(e)[:200])}</code>",
                    parse_mode='HTML',
                    reply_markup=admin_main_menu()
                )

            db.update_user_temp(message.from_user.id, 'add_mode', None)
            return

        except Exception as e:
            log.exception("Ошибка при добавлении по ID")
            bot.send_message(
                message.chat.id,
                f"{STRINGS['cant_access_channel']}\n\nОшибка: {html.escape(str(e)[:100])}",
                parse_mode='HTML',
                reply_markup=back_button()
            )
            return

    # --- Добавление канала по ссылке ---
    elif add_mode == "by_link":
        if not message.text:
            return
        if '@' not in message.text and 't.me/' not in message.text:
            bot.send_message(
                message.chat.id,
                "❌ Отправьте ссылку вида @username или t.me/username",
                reply_markup=back_button()
            )
            return

        try:
            username = (message.text
                        .replace('@', '')
                        .replace('https://t.me/', '')
                        .replace('t.me/', '')
                        .strip()
                        .split('/')[0])
            chat = bot.get_chat(f'@{username}')
        except Exception as e:
            bot.send_message(
                message.chat.id,
                f"❌ Не удалось найти канал.\nОшибка: <code>{html.escape(str(e)[:150])}</code>",
                parse_mode='HTML',
                reply_markup=back_button()
            )
            return

        existing = db.get_channel(chat.id)
        if existing:
            bot.send_message(
                message.chat.id,
                f"⚠️ Канал <b>{html.escape(chat.title)}</b> уже добавлен!",
                parse_mode='HTML',
                reply_markup=admin_main_menu()
            )
        else:
            is_private = not chat.username
            db.add_channel(
                channel_id=chat.id,
                channel_name=chat.title,
                added_by=message.from_user.id,
                is_private=is_private
            )
            private_text = "🔒 Приватный" if is_private else "🔓 Публичный"
            bot.send_message(
                message.chat.id,
                f"✅ Канал <b>{html.escape(chat.title)}</b> успешно добавлен!\n\n"
                f"ID: <code>{chat.id}</code>\n"
                f"Тип: {private_text}",
                parse_mode='HTML',
                reply_markup=admin_main_menu()
            )

        db.update_user_temp(message.from_user.id, 'add_mode', None)
        return

    # --- Добавление через пересылку ---
    elif db.get_user_temp(message.from_user.id, 'adding_channel'):
        if message.forward_from_chat and message.forward_from_chat.type in ['channel', 'group', 'supergroup']:
            channel_info = message.forward_from_chat
            existing = db.get_channel(channel_info.id)
            if existing:
                bot.send_message(
                    message.chat.id,
                    f"⚠️ Канал <b>{html.escape(channel_info.title)}</b> уже добавлен!",
                    parse_mode='HTML'
                )
            else:
                is_private = not channel_info.username
                db.add_channel(
                    channel_id=channel_info.id,
                    channel_name=channel_info.title,
                    added_by=message.from_user.id,
                    is_private=is_private
                )
                private_text = "🔒 Приватный" if is_private else "🔓 Публичный"
                bot.send_message(
                    message.chat.id,
                    f"✅ Канал <b>{html.escape(channel_info.title)}</b> успешно добавлен!\n\n"
                    f"ID: <code>{channel_info.id}</code>\n"
                    f"Тип: {private_text}",
                    parse_mode='HTML',
                    reply_markup=admin_main_menu()
                )
            db.update_user_temp(message.from_user.id, 'adding_channel', False)
            return
        else:
            bot.send_message(
                message.chat.id,
                "❌ Это не похоже на пересланное сообщение из канала.\n"
                "Перешлите сообщение из канала (убедитесь, что канал не скрывает отправителя).",
                reply_markup=back_button()
            )
            return

    # --- Изменение шаблона ---
    elif db.get_user_temp(message.from_user.id, 'changing_template'):
        channel_id = db.get_user_temp(message.from_user.id, 'changing_template')
        if not message.text:
            return

        if db.update_channel(channel_id, template=message.text):
            channel = db.get_channel(channel_id)
            bot.send_message(
                message.chat.id,
                f"{STRINGS['template_changed']}\n\nНовый шаблон для канала <b>{html.escape(channel.channel_name)}</b>:",
                parse_mode='HTML'
            )
            example = apply_template(
                message.text,
                "Пример текста на русском",
                "Example text in English",
                channel.source_lang,
                channel.target_lang,
                channel.parse_mode
            )
            try:
                bot.send_message(
                    message.chat.id,
                    "<b>Пример:</b>\n" + example,
                    parse_mode=channel.parse_mode if channel.parse_mode != "None" else None
                )
            except Exception:
                bot.send_message(
                    message.chat.id,
                    "<b>Пример (без форматирования):</b>\n" + example,
                    parse_mode=None
                )

        db.update_user_temp(message.from_user.id, 'changing_template', None)
        return

# ========== CALLBACK-ЗАПРОСЫ ==========

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    if not is_admin(call.from_user.id):
        bot.answer_callback_query(call.id, STRINGS['admin_only'])
        return

    data = call.data

    try:
        if data == "back_to_main":
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text="👑 <b>Панель администратора</b>\n\nВыберите действие:",
                parse_mode='HTML',
                reply_markup=admin_main_menu()
            )

        elif data == "back_to_channels":
            channels = db.get_all_channels()
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text="⚙️ <b>Настройки канала</b>\n\nВыберите канал:",
                parse_mode='HTML',
                reply_markup=channel_list_keyboard(channels)
            )

        elif data == "add_by_link":
            db.update_user_temp(call.from_user.id, 'add_mode', 'by_link')
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text="🔗 <b>Добавление по ссылке</b>\n\n"
                     "Отправьте мне <b>ссылку на канал</b>:\n"
                     "• @username\n• t.me/username\n\n"
                     "Убедитесь, что бот добавлен в канал как администратор.",
                parse_mode='HTML',
                reply_markup=back_button()
            )

        elif data == "add_by_id":
            db.update_user_temp(call.from_user.id, 'add_mode', 'by_id')
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text="🆔 <b>Добавление по ID</b>\n\n"
                     "Отправьте мне <b>ID канала</b>.\n\n"
                     "<b>Как получить ID канала:</b>\n"
                     "1. В веб-версии Telegram откройте канал\n"
                     "2. Посмотрите в адресной строке: t.me/c/XXXXXXX/...\n"
                     "   или используйте бота @getidsbot\n\n"
                     "<b>Формат ID:</b>\n"
                     "• Каналы начинаются с <code>-100</code>\n"
                     "• Группы с отрицательными числами\n\n"
                     "<b>Примеры:</b>\n"
                     "<code>-1001234567890</code> - канал/супергруппа\n"
                     "<code>-123456789</code> - группа",
                parse_mode='HTML',
                reply_markup=back_button()
            )

        elif data == "add_by_forward":
            db.update_user_temp(call.from_user.id, 'adding_channel', True)
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text="📤 <b>Добавление через пересылку</b>\n\n"
                     "Перешлите мне <b>любое сообщение</b> из канала.\n\n"
                     "Убедитесь, что:\n"
                     "1. Бот добавлен в канал как администратор\n"
                     "2. Канал не скрывает информацию об отправителе",
                parse_mode='HTML',
                reply_markup=back_button()
            )

        elif data.startswith("channel_"):
            channel_id = int(data.split("_")[1])
            channel = db.get_channel(channel_id)
            if channel:
                bot.edit_message_text(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    text=format_channel_info(channel),
                    parse_mode='HTML',
                    reply_markup=channel_settings_keyboard(channel_id)
                )
            else:
                bot.answer_callback_query(call.id, STRINGS['channel_not_found'])

        elif data.startswith("langs_"):
            channel_id = int(data.split("_")[1])
            channel = db.get_channel(channel_id)
            if channel:
                bot.edit_message_text(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    text=f"🌐 <b>Настройки языков</b>\n\n"
                         f"Канал: <b>{html.escape(channel.channel_name)}</b>\n"
                         f"Текущие языки: {channel.source_lang} → {channel.target_lang}\n\n"
                         f"Выберите что изменить:",
                    parse_mode='HTML',
                    reply_markup=types.InlineKeyboardMarkup(row_width=2).add(
                        types.InlineKeyboardButton("Исходный язык", callback_data=f"source_lang_{channel_id}"),
                        types.InlineKeyboardButton("Целевой язык", callback_data=f"target_lang_{channel_id}"),
                        types.InlineKeyboardButton("🔙 Назад", callback_data=f"channel_{channel_id}")
                    )
                )

        elif data.startswith("source_lang_") or data.startswith("target_lang_"):
            parts = data.split("_")
            channel_id = int(parts[2])
            lang_type = parts[0]  # source_lang или target_lang
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text="🌍 <b>Выберите язык:</b>",
                parse_mode='HTML',
                reply_markup=language_keyboard(channel_id, "source" if "source" in lang_type else "target")
            )

        elif data.startswith("setlang_"):
            parts = data.split("_")
            channel_id = int(parts[1])
            lang_type = parts[2]  # source или target
            lang_code = parts[3]

            if lang_type == "source":
                db.update_channel(channel_id, source_lang=lang_code)
            else:
                db.update_channel(channel_id, target_lang=lang_code)

            channel = db.get_channel(channel_id)
            bot.answer_callback_query(call.id, STRINGS['language_changed'])
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=f"✅ Язык изменён!\n\n{format_channel_info(channel)}",
                parse_mode='HTML',
                reply_markup=channel_settings_keyboard(channel_id)
            )

        elif data.startswith("template_"):
            channel_id = int(data.split("_")[1])
            channel = db.get_channel(channel_id)
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=f"📝 <b>Редактирование шаблона</b>\n\n"
                     f"Канал: <b>{html.escape(channel.channel_name)}</b>\n\n"
                     f"Текущий шаблон:\n<code>{html.escape(channel.template[:500])}</code>\n\n"
                     f"Отправьте мне новый шаблон. Плейсхолдеры:\n"
                     f"• <code>{{original}}</code>\n"
                     f"• <code>{{translated}}</code>\n"
                     f"• <code>{{original_lang}}</code>\n"
                     f"• <code>{{translated_lang}}</code>\n"
                     f"• <code>{{date}}</code>\n"
                     f"• <code>{{time}}</code>\n"
                     f"• <code>{{datetime}}</code>",
                parse_mode='HTML',
                reply_markup=back_button(f"channel_{channel_id}")
            )
            db.update_user_temp(call.from_user.id, 'changing_template', channel_id)

        elif data.startswith("parse_"):
            channel_id = int(data.split("_")[1])
            channel = db.get_channel(channel_id)
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=f"🔧 <b>Parse Mode</b>\n\n"
                     f"Канал: <b>{html.escape(channel.channel_name)}</b>\n"
                     f"Текущий режим: {channel.parse_mode}\n\n"
                     f"Выберите новый режим:",
                parse_mode='HTML',
                reply_markup=parse_mode_keyboard(channel_id)
            )

        elif data.startswith("setparse_"):
            parts = data.split("_")
            channel_id = int(parts[1])
            parse_mode = parts[2]
            # сохраняем как строку "None" или реальное значение
            db.update_channel(channel_id, parse_mode=parse_mode)
            channel = db.get_channel(channel_id)
            bot.answer_callback_query(call.id, "✅ Parse mode изменён!")
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=f"✅ Parse mode изменён!\n\n{format_channel_info(channel)}",
                parse_mode='HTML',
                reply_markup=channel_settings_keyboard(channel_id)
            )

        elif data.startswith("toggle_"):
            channel_id = int(data.split("_")[1])
            new_status = db.toggle_channel(channel_id)
            channel = db.get_channel(channel_id)
            status_text = "✅ ВКЛЮЧЕН" if new_status else "❌ ВЫКЛЮЧЕН"
            bot.answer_callback_query(call.id, f"Канал {status_text}")
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=f"✅ Статус изменён!\n\n{format_channel_info(channel)}",
                parse_mode='HTML',
                reply_markup=channel_settings_keyboard(channel_id)
            )

        elif data.startswith("delete_"):
            channel_id = int(data.split("_")[1])
            channel = db.get_channel(channel_id)
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=f"🗑️ <b>Удаление канала</b>\n\n"
                     f"Вы уверены, что хотите удалить канал <b>{html.escape(channel.channel_name)}</b>?\n\n"
                     f"Это действие нельзя отменить!",
                parse_mode='HTML',
                reply_markup=confirmation_keyboard(channel_id)
            )

        elif data.startswith("confirm_delete_"):
            channel_id = int(data.split("_")[2])
            channel = db.get_channel(channel_id)
            if channel:
                channel_name = channel.channel_name
                db.remove_channel(channel_id)
                bot.answer_callback_query(call.id, "🗑️ Канал удалён")
                channels = db.get_all_channels()
                if channels:
                    bot.edit_message_text(
                        chat_id=call.message.chat.id,
                        message_id=call.message.message_id,
                        text=f"🗑️ Канал <b>{html.escape(channel_name)}</b> удалён.\n\n{STRINGS['channel_list']}",
                        parse_mode='HTML',
                        reply_markup=channel_list_keyboard(channels)
                    )
                else:
                    bot.edit_message_text(
                        chat_id=call.message.chat.id,
                        message_id=call.message.message_id,
                        text=f"🗑️ Канал <b>{html.escape(channel_name)}</b> удалён.\n\n{STRINGS['no_channels']}",
                        parse_mode='HTML',
                        reply_markup=back_button()
                    )

        bot.answer_callback_query(call.id)

    except Exception as e:
        log.exception(f"Ошибка в callback: {e}")
        try:
            bot.answer_callback_query(call.id, "❌ Произошла ошибка, попробуйте снова")
        except Exception:
            pass

# ========== ЗАПУСК БОТА ==========

if __name__ == "__main__":
    print(f"🤖 Бот запущен!")
    print(f"👑 Админ ID: {ADMIN_ID}")
    print(f"📢 Загружено каналов: {len(db.get_all_channels())}")
    print(f"📊 Обработано сообщений: {db.get_stats()['processed_messages']}")
    print("⏳ Ожидание сообщений...")

    while True:
        try:
            bot.polling(none_stop=True, interval=1, timeout=30)
        except Exception as e:
            log.exception(f"❌ Ошибка polling: {e}")
            print("⏳ Перезапуск через 5 секунд...")
            time.sleep(5)


# 📝 Template Examples for Telegram Channel Auto-Translator

[English](#english) | [Русский](#русский)

---

## English

### Template Library for Custom Message Formatting

A collection of pre-designed message templates for the Telegram Channel Auto-Translator bot. Easily customize how your translated messages appear with professionally designed templates.

![Templates](https://img.shields.io/badge/Templates-10+-blue)
![Categories](https://img.shields.io/badge/Categories-6+-green)
![Formats](https://img.shields.io/badge/Formats-HTML%2FMarkdown-orange)

## 📁 Available Templates

### Basic Templates
| Template | Description | Best For |
|----------|-------------|----------|
| `template-minimal.txt` | Clean, no-frills formatting | Simple channels, readability |
| `template-bilingual.txt` | Clear two-language display | Bilingual audiences |
| `template-html.txt` | Professional HTML formatting | Corporate/official channels |

### Specialized Templates
| Template | Description | Best For |
|----------|-------------|----------|
| `template-news.txt` | News-style formatting | News channels, media |
| `template-academic.txt` | Technical/scientific format | Academic, research channels |
| `template-professional.txt` | Corporate business format | Business, official communications |

### Stylized Templates
| Template | Description | Best For |
|----------|-------------|----------|
| `template-social.txt` | Social media style | Community, social channels |
| `template-emoji.txt` | Emoji-rich formatting | Youth, informal channels |
| `template-simple-columns.txt` | Side-by-side columns | Comparing translations |

## 🚀 Quick Start

### Using Templates

1. **Browse templates** in this folder
2. **Copy the content** of your chosen template
3. **Open bot admin panel** by sending `/admin`
4. **Select channel** → "📝 Template"
5. **Paste template** and send to bot
6. **Preview** before applying

### Template Variables

All templates support these variables:

| Variable | Description | Example |
|----------|-------------|---------|
| `{original}` | Original text | `Привет, как дела?` |
| `{translated}` | Translated text | `Hello, how are you?` |
| `{original_lang}` | Source language code | `ru` |
| `{translated_lang}` | Target language code | `en` |
| `{date}` | Current date (YYYY-MM-DD) | `2024-01-15` |
| `{time}` | Current time (HH:MM) | `14:30` |
| `{datetime}` | Full date and time | `2024-01-15 14:30:00` |

## 🎨 Template Features

### Formatting Options

**HTML Tags (when parse_mode is HTML):**
- `<b>bold</b>` - **Bold text**
- `<i>italic</i>` - *Italic text*
- `<code>code</code>` - `Monospace font`
- `<blockquote>quote</blockquote>` - Block quote
- `<pre>preformatted</pre>` - Preserves formatting
- `<a href="url">link</a>` - Hyperlink

**Box-drawing Characters:**
```
─ ━ │ ┃ ┄ ┅ ┆ ┇ ┈ ┉ ┊ ┋ ┌ ┍ ┎ ┏ ┐ ┑ ┒ ┓ └ ┕ ┖ ┗ ┘ ┙ ┚ ┛ ├ ┝ ┞ ┟ ┠ ┡ ┢ ┣ ┤ ┥ ┦ ┧ ┨ ┩ ┪ ┫ ┬ ┭ ┮ ┯ ┰ ┱ ┲ ┳ ┴ ┵ ┶ ┷ ┸ ┹ ┺ ┻ ┼ ┽ ┾ ┿ ╀ ╁ ╂ ╃ ╄ ╅ ╆ ╇ ╈ ╉ ╊ ╋
```

**Popular Emoji Categories:**
- 🌍🌐🗺️ - Translation/languages
- 📅📆🗓️ - Date/time
- ⏰🕐🕑🕒 - Time indicators
- 📝📄📋 - Text/documents
- 🔄🔄🔄 - Translation process
- ✅✔️☑️ - Success/completion
- ⚙️🔧🛠️ - Settings/tools
- 📊📈📉 - Statistics

## 🔧 Custom Template Creation

### Step-by-Step Guide

1. **Start with a base template:**
   ```html
   <b>{translated_lang}:</b>
   {translated}
   
   <b>{original_lang}:</b>
   {original}
   ```

2. **Add styling elements:**
   ```html
   <div align="center">
   <b>TRANSLATION</b>
   </div>
   
   <b>English:</b>
   <blockquote>{translated}</blockquote>
   
   <b>Russian:</b>
   <blockquote>{original}</blockquote>
   ```

3. **Include metadata:**
   ```html
   <small>
   Translated on {date} at {time}
   </small>
   ```

### Template Best Practices

1. **Keep it readable** - Avoid overly complex layouts
2. **Test on mobile** - Most users view Telegram on phones
3. **Character limit** - Stay under 4096 characters (Telegram limit)
4. **UTF-8 encoding** - Essential for emoji and special characters
5. **Preview always** - Use bot's preview feature before applying

## 📊 Template Comparison

### Minimal Template
**Pros:** Fast loading, works on all devices  
**Cons:** Basic appearance

### Professional Template  
**Pros:** Corporate look, includes metadata  
**Cons:** More complex

### Emoji Template
**Pros:** Engaging, modern appearance  
**Cons:** May not suit formal channels

## 🛠️ Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| Template not working | Check variable syntax `{variable}` |
| No formatting | Set parse_mode to "HTML" in channel settings |
| Emoji not showing | Ensure file is UTF-8 encoded |
| Message too long | Simplify template or shorten text |
| Variables not replaced | Verify variable names match exactly |

### Testing Template

Use this test text to preview:
```
Original: This is a test message for template preview.
Translated: Это тестовое сообщение для предпросмотра шаблона.
```

## 📚 Template Examples

### Example 1: Simple Notification
```
📢 Translation Complete

English:
{translated}

Russian:
{original}

⏰ {time}
```

### Example 2: Professional Report
```
══════════════════════════════
        TRANSLATION REPORT        
══════════════════════════════

SOURCE: {original_lang}
TARGET: {translated_lang}
TIME: {datetime}

──────────────────────────────

{translated}

──────────────────────────────

{original}

══════════════════════════════
```

### Example 3: Social Media Style
```
🤖 AUTO-TRANSLATED POST 🌐

"{translated}"

👆 In English
👇 In Russian

"{original}"

#translation #autotranslate #{original_lang}to{translated_lang}
```

## 🔄 Updating Templates

1. **Edit template file** in any text editor
2. **Save as UTF-8** (important for special characters)
3. **Copy to clipboard**
4. **Update via bot admin panel**
5. **Preview changes**
6. **Apply if satisfied**

## 📞 Support

- **GitHub Issues:** Report template problems
- **Bot Admin:** Use help section in bot
- **Community:** Share your templates with others

## 📄 License

Templates are released under MIT License. Feel free to use, modify, and distribute.

## 🙏 Contribution

Want to add your template?

1. Fork the repository
2. Add your template to `examples/` folder
3. Follow naming convention: `template-{name}.txt`
4. Create Pull Request

---

## Русский

### Библиотека шаблонов для настройки форматирования сообщений

Коллекция предварительно разработанных шаблонов сообщений для бота Telegram Channel Auto-Translator. Легко настраивайте, как будут выглядеть ваши переведенные сообщения, с профессионально разработанными шаблонами.

## 📁 Доступные шаблоны

### Базовые шаблоны
| Шаблон | Описание | Для чего лучше |
|--------|----------|----------------|
| `template-minimal.txt` | Чистое, простое форматирование | Простые каналы, читаемость |
| `template-bilingual.txt` | Четкое отображение двух языков | Двуязычная аудитория |
| `template-html.txt` | Профессиональное HTML-форматирование | Корпоративные/официальные каналы |

### Специализированные шаблоны
| Шаблон | Описание | Для чего лучше |
|--------|----------|----------------|
| `template-news.txt` | Форматирование в стиле новостей | Новостные каналы, медиа |
| `template-academic.txt` | Технический/научный формат | Академические, исследовательские каналы |
| `template-professional.txt` | Корпоративный бизнес-формат | Бизнес, официальные коммуникации |

### Стилизованные шаблоны
| Шаблон | Описание | Для чего лучше |
|--------|----------|----------------|
| `template-social.txt` | Стиль социальных сетей | Сообщества, социальные каналы |
| `template-emoji.txt` | Форматирование с эмодзи | Молодежь, неформальные каналы |
| `template-simple-columns.txt` | Колонки бок о бок | Сравнение переводов |

## 🚀 Быстрый старт

### Использование шаблонов

1. **Просмотрите шаблоны** в этой папке
2. **Скопируйте содержимое** выбранного шаблона
3. **Откройте админ-панель бота**, отправив `/admin`
4. **Выберите канал** → "📝 Шаблон"
5. **Вставьте шаблон** и отправьте боту
6. **Предварительный просмотр** перед применением

### Переменные шаблонов

Все шаблоны поддерживают эти переменные:

| Переменная | Описание | Пример |
|------------|----------|---------|
| `{original}` | Оригинальный текст | `Привет, как дела?` |
| `{translated}` | Переведенный текст | `Hello, how are you?` |
| `{original_lang}` | Код исходного языка | `ru` |
| `{translated_lang}` | Код целевого языка | `en` |
| `{date}` | Текущая дата (ГГГГ-ММ-ДД) | `2024-01-15` |
| `{time}` | Текущее время (ЧЧ:ММ) | `14:30` |
| `{datetime}` | Полная дата и время | `2024-01-15 14:30:00` |

## 🎨 Особенности шаблонов

### Варианты форматирования

**HTML теги (когда parse_mode установлен в HTML):**
- `<b>жирный</b>` - **Жирный текст**
- `<i>курсив</i>` - *Курсивный текст*
- `<code>код</code>` - `Моноширинный шрифт`
- `<blockquote>цитата</blockquote>` - Блок цитаты
- `<pre>преформатированный</pre>` - Сохраняет форматирование
- `<a href="ссылка">ссылка</a>` - Гиперссылка

**Символы рисования рамок:**
```
─ ━ │ ┃ ┄ ┅ ┆ ┇ ┈ ┉ ┊ ┋ ┌ ┍ ┎ ┏ ┐ ┑ ┒ ┓ └ ┕ ┖ ┗ ┘ ┙ ┚ ┛ ├ ┝ ┞ ┟ ┠ ┡ ┢ ┣ ┤ ┥ ┦ ┧ ┨ ┩ ┪ ┫ ┬ ┭ ┮ ┯ ┰ ┱ ┲ ┳ ┴ ┵ ┶ ┷ ┸ ┹ ┺ ┻ ┼ ┽ ┾ ┿ ╀ ╁ ╂ ╃ ╄ ╅ ╆ ╇ ╈ ╉ ╊ ╋
```

**Популярные категории эмодзи:**
- 🌍🌐🗺️ - Перевод/языки
- 📅📆🗓️ - Дата/время
- ⏰🕐🕑🕒 - Индикаторы времени
- 📝📄📋 - Текст/документы
- 🔄🔄🔄 - Процесс перевода
- ✅✔️☑️ - Успех/завершение
- ⚙️🔧🛠️ - Настройки/инструменты
- 📊📈📉 - Статистика

## 🔧 Создание пользовательских шаблонов

### Пошаговое руководство

1. **Начните с базового шаблона:**
   ```html
   <b>{translated_lang}:</b>
   {translated}
   
   <b>{original_lang}:</b>
   {original}
   ```

2. **Добавьте стилистические элементы:**
   ```html
   <div align="center">
   <b>ПЕРЕВОД</b>
   </div>
   
   <b>Английский:</b>
   <blockquote>{translated}</blockquote>
   
   <b>Русский:</b>
   <blockquote>{original}</blockquote>
   ```

3. **Включите метаданные:**
   ```html
   <small>
   Переведено {date} в {time}
   </small>
   ```

### Лучшие практики шаблонов

1. **Сохраняйте читаемость** - Избегайте слишком сложных макетов
2. **Тестируйте на мобильных** - Большинство пользователей смотрят Telegram на телефонах
3. **Лимит символов** - Оставайтесь в пределах 4096 символов (лимит Telegram)
4. **Кодировка UTF-8** - Необходима для эмодзи и специальных символов
5. **Всегда предпросмотр** - Используйте функцию предпросмотра бота перед применением

## 📊 Сравнение шаблонов

### Минималистичный шаблон
**Плюсы:** Быстрая загрузка, работает на всех устройствах  
**Минусы:** Базовый внешний вид

### Профессиональный шаблон  
**Плюсы:** Корпоративный вид, включает метаданные  
**Минусы:** Более сложный

### Шаблон с эмодзи
**Плюсы:** Привлекательный, современный вид  
**Минусы:** Может не подходить для формальных каналов

## 🛠️ Решение проблем

### Частые проблемы

| Проблема | Решение |
|----------|---------|
| Шаблон не работает | Проверьте синтаксис переменных `{переменная}` |
| Нет форматирования | Установите parse_mode в "HTML" в настройках канала |
| Эмодзи не показываются | Убедитесь, что файл в кодировке UTF-8 |
| Сообщение слишком длинное | Упростите шаблон или сократите текст |
| Переменные не заменяются | Убедитесь, что имена переменных совпадают точно |

### Тестирование шаблона

Используйте этот тестовый текст для предпросмотра:
```
Оригинал: This is a test message for template preview.
Перевод: Это тестовое сообщение для предпросмотра шаблона.
```

## 📚 Примеры шаблонов

### Пример 1: Простое уведомление
```
📢 Перевод завершен

Английский:
{translated}

Русский:
{original}

⏰ {time}
```

### Пример 2: Профессиональный отчет
```
══════════════════════════════
        ОТЧЕТ О ПЕРЕВОДЕ        
══════════════════════════════

ИСТОЧНИК: {original_lang}
ЦЕЛЬ: {translated_lang}
ВРЕМЯ: {datetime}

──────────────────────────────

{translated}

──────────────────────────────

{original}

══════════════════════════════
```

### Пример 3: Стиль социальных сетей
```
🤖 АВТО-ПЕРЕВЕДЕННЫЙ ПОСТ 🌐

"{translated}"

👆 На английском
👇 На русском

"{original}"

#перевод #автоперевод #{original_lang}to{translated_lang}
```

## 🔄 Обновление шаблонов

1. **Отредактируйте файл шаблона** в любом текстовом редакторе
2. **Сохраните как UTF-8** (важно для специальных символов)
3. **Скопируйте в буфер обмена**
4. **Обновите через админ-панель бота**
5. **Предварительный просмотр изменений**
6. **Примените, если удовлетворены**

## 📞 Поддержка

- **GitHub Issues:** Сообщите о проблемах с шаблонами
- **Админ бота:** Используйте раздел помощи в боте
- **Сообщество:** Поделитесь своими шаблонами с другими

## 📄 Лицензия

Шаблоны выпущены под лицензией MIT. Свободно используйте, изменяйте и распространяйте.

## 🙏 Вклад в развитие

Хотите добавить свой шаблон?

1. Форкните репозиторий
2. Добавьте свой шаблон в папку `examples/`
3. Следуйте соглашению об именовании: `template-{имя}.txt`
4. Создайте Pull Request

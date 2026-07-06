# Discord Gemini Bot

Энэ bot Discord дээр `/ask` командаар Google Gemini API ашиглаж хариулна.

## 1. Суулгах

```bash
pip install -r requirements.txt
```

## 2. `.env.example`-г `.env` болгох

Windows:

```bash
copy .env.example .env
```

`.env` дотор:

```env
DISCORD_TOKEN=your_discord_bot_token
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-2.5-flash
```

## 3. Discord bot invite

Discord Developer Portal дээр OAuth2 -> URL Generator:

Scopes:
- bot
- applications.commands

Bot permissions:
- Send Messages
- Use Slash Commands

## 4. Ажиллуулах

```bash
python bot.py
```

Discord дээр:

```text
/ping
/ask sain uu?
```

## 5. 24/7 байлгах

Local PC дээр ажиллуулбал PC асаалттай үед л online байна.
24/7 бол Railway, Render, VPS, Oracle Cloud зэрэг дээр deploy хийнэ.

## Анхаар

`.env` файлаа GitHub public repo руу upload хийж болохгүй.
Discord token, Gemini API key-ээ хэнд ч битгий явуул.

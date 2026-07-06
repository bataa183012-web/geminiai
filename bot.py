import os
import asyncio
import textwrap

import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
DISCORD_GUILD_ID = os.getenv("DISCORD_GUILD_ID")  # optional: server ID for faster slash command sync
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

if not DISCORD_TOKEN:
    raise RuntimeError("DISCORD_TOKEN is missing. Put it in your .env file.")
if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY is missing. Put it in your .env file.")

gemini_client = genai.Client(api_key=GEMINI_API_KEY)


class GeminiDiscordBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # If DISCORD_GUILD_ID is set, commands show up faster in that server.
        if DISCORD_GUILD_ID:
            guild = discord.Object(id=int(DISCORD_GUILD_ID))
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)
            print(f"Slash commands synced to guild {DISCORD_GUILD_ID}")
        else:
            await self.tree.sync()
            print("Slash commands synced globally. This can take a while to appear.")

    async def on_ready(self):
        print(f"Logged in as {self.user} (ID: {self.user.id})")


bot = GeminiDiscordBot()


def split_message(text: str, limit: int = 1900) -> list[str]:
    text = text.strip()
    if not text:
        return ["Хоосон хариу ирлээ."]
    chunks = textwrap.wrap(
        text,
        width=limit,
        replace_whitespace=False,
        drop_whitespace=False,
    )
    return chunks or [text[:limit]]


def ask_gemini_sync(question: str) -> str:
    response = gemini_client.models.generate_content(
        model=GEMINI_MODEL,
        contents=question,
        config=types.GenerateContentConfig(
            system_instruction=(
                "You are a helpful Discord bot. "
                "Keep answers friendly, clear, and not too long. "
                "Use Mongolian if the user asks in Mongolian."
            ),
            max_output_tokens=800,
            temperature=0.7,
        ),
    )

    answer = getattr(response, "text", None)
    if answer:
        return answer.strip()

    # Fallback in case the SDK returns a different response shape.
    return "Gemini-ээс текст хариу ирсэнгүй. Model нэр эсвэл API key-ээ шалгаарай."


@bot.tree.command(name="ask", description="Ask Gemini AI a question")
@app_commands.describe(question="What do you want to ask?")
async def ask(interaction: discord.Interaction, question: str):
    await interaction.response.defer(thinking=True)

    try:
        # Run Gemini request outside the Discord event loop so the bot doesn't freeze.
        answer = await asyncio.to_thread(ask_gemini_sync, question)

        for i, chunk in enumerate(split_message(answer)):
            if i == 0:
                await interaction.followup.send(chunk)
            else:
                await interaction.channel.send(chunk)

    except Exception as e:
        await interaction.followup.send(
            f"Алдаа гарлаа: `{type(e).__name__}`. DISCORD_TOKEN, GEMINI_API_KEY, GEMINI_MODEL-оо шалгаарай.",
            ephemeral=True,
        )


@bot.tree.command(name="ping", description="Check if the bot is online")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("Pong! Bot ажиллаж байна ✅")


bot.run(DISCORD_TOKEN)

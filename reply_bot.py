import asyncio
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, F, types
from aiogram.enums.parse_mode import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.client.default import DefaultBotProperties
from pydantic import BaseModel, Field
from storage import get_store
from bacen_feed import (
    get_ultimo_normativo, 
    get_normativos_hoje, 
    get_normativos_ontem, 
    get_normativos_semanal,
    format_normativo_message,
    format_multiple_normativos_message
)

# Load environment variables from .env file
load_dotenv()

class Settings(BaseModel):
    TELEGRAM_TOKEN: str = Field(...)

def get_settings() -> Settings:
    return Settings(TELEGRAM_TOKEN=os.environ["TELEGRAM_TOKEN"])

s = get_settings()
bot = Bot(token=s.TELEGRAM_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
store = get_store()

@dp.message(CommandStart())
async def on_start(message: types.Message):
    await message.answer("Olá! 👋\n\n<b>Comandos disponíveis:</b>\n• <b>oi</b> - Autorizar avisos automáticos\n• <b>/stop</b> - Cancelar avisos\n• <b>ultimo</b> - Último normativo\n• <b>hoje</b> - Normativos de hoje\n• <b>ontem</b> - Normativos de ontem\n• <b>semanal</b> - Normativos desta semana")

@dp.message(Command("stop"))
async def on_stop(message: types.Message):
    store.remove_subscriber(message.chat.id)
    await message.answer("Você foi removido(a) da lista. ❌\nSe quiser voltar, mande <b>oi</b>.")

@dp.message(F.text.lower() == "oi")
async def on_oi(message: types.Message):
    user = message.from_user
    store.upsert_subscriber(
        chat_id=message.chat.id,
        first_name=user.first_name,
        username=user.username,
    )
    await message.answer("✅ Pronto! Você autorizou receber resumos de normativos do BACEN.\nPara sair, envie /stop.")

@dp.message(F.text.lower() == "ultimo")
async def on_ultimo(message: types.Message):
    """Retorna o último normativo publicado"""
    try:
        await message.answer("🔍 Buscando último normativo...")
        normativo = get_ultimo_normativo()
        
        if normativo:
            msg = format_normativo_message(normativo)
            await message.answer(msg)
        else:
            await message.answer("❌ Não foi possível encontrar o último normativo.")
    except Exception as e:
        await message.answer(f"❌ Erro ao buscar último normativo: {str(e)}")

@dp.message(F.text.lower() == "hoje")
async def on_hoje(message: types.Message):
    """Retorna todos os normativos de hoje"""
    try:
        await message.answer("🔍 Buscando normativos de hoje...")
        normativos = get_normativos_hoje()
        
        msg = format_multiple_normativos_message(normativos, "Hoje")
        await message.answer(msg)
    except Exception as e:
        await message.answer(f"❌ Erro ao buscar normativos de hoje: {str(e)}")

@dp.message(F.text.lower() == "ontem")
async def on_ontem(message: types.Message):
    """Retorna todos os normativos de ontem"""
    try:
        await message.answer("🔍 Buscando normativos de ontem...")
        normativos = get_normativos_ontem()
        
        msg = format_multiple_normativos_message(normativos, "Ontem")
        await message.answer(msg)
    except Exception as e:
        await message.answer(f"❌ Erro ao buscar normativos de ontem: {str(e)}")

@dp.message(F.text.lower() == "semanal")
async def on_semanal(message: types.Message):
    """Retorna todos os normativos desta semana"""
    try:
        await message.answer("🔍 Buscando normativos desta semana...")
        normativos = get_normativos_semanal()
        
        msg = format_multiple_normativos_message(normativos, "Esta Semana")
        await message.answer(msg)
    except Exception as e:
        await message.answer(f"❌ Erro ao buscar normativos desta semana: {str(e)}")

@dp.message()
async def fallback(message: types.Message):
    await message.answer("Não entendi 🤖 — Comandos disponíveis:\n• <b>oi</b> - Autorizar avisos\n• <b>/stop</b> - Cancelar avisos\n• <b>ultimo</b> - Último normativo\n• <b>hoje</b> - Normativos de hoje\n• <b>ontem</b> - Normativos de ontem\n• <b>semanal</b> - Normativos desta semana")

async def main():
    print("reply_bot: ouvindo mensagens...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

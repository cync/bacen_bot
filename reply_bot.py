import asyncio
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, F, types
from aiogram.enums.parse_mode import ParseMode
from aiogram.filters import CommandStart, Command
from pydantic import BaseModel, Field
from storage import get_store

# Load environment variables from .env file
load_dotenv()

class Settings(BaseModel):
    TELEGRAM_TOKEN: str = Field(...)

def get_settings() -> Settings:
    return Settings(TELEGRAM_TOKEN=os.environ["TELEGRAM_TOKEN"])

s = get_settings()
bot = Bot(token=s.TELEGRAM_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()
store = get_store()

@dp.message(CommandStart())
async def on_start(message: types.Message):
    await message.answer("Olá! 👋\nMe envie <b>oi</b> para autorizar os avisos de normativos do BACEN. Use /stop para cancelar.")

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

@dp.message()
async def fallback(message: types.Message):
    await message.answer("Não entendi 🤖 — mande <b>oi</b> para autorizar os avisos, ou /stop para cancelar.")

async def main():
    print("reply_bot: ouvindo mensagens...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

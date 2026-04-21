import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
import firebase_admin
from firebase_admin import credentials, db
import os

# --- КОНФІГУРАЦІЯ ---
BOT_TOKEN = "8712898544:AAGLysJP0M_TAnllYe4Ib_qITapDUYFfC6Q"
OWNER_ID = 7443699603
DATABASE_URL = "https://rkbot-db5d6-default-rtdb.firebaseio.com/"
CARD_DETAILS = "4441 1111 2222 3333 (Monobank)" 

# --- FIREBASE ІНІЦІАЛІЗАЦІЯ ---
# Використовуємо твій вшитий ключ, щоб не було помилок з файлом
cred_dict = {
  "type": "service_account",
  "project_id": "rkbot-db5d6",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQCy7Lknm7fa2mlH\nCHFIvznvWxfj9VBWP0vOg6WQpKRSnhMXS2XL2P7cOdNXH2laWK0dnvdEOLo9k8HA\niLApvA5jQ3/cSx5upoU9c3Ohta+hpRJt1We28WT7tNP/RhKHEXBWq9lV1KGii1rv\nwPq93T0ZKRSFg6Yim4vpU3wvbisBWfcbQd+DIVd06YvmSMCojbCy/vkoQXfCVQpD\nNtbmpDBMIrAenAiWvNjGp9cCDMgKo0p6XXoF1kabhiYjYlooW2GOVzU3I7m5COq4\n3Q/vCj66Q5Lhu9XHXP2PVhEBaTisrKweJZE5MtqFP8Gdd7vL8+G4Q5nmtU2zZW6j\nIxuYvk3dAgMBAAECggEACO/KOxhfDIssE6kjVvj9vz7ukjGsKrUJIVGE4rtY3ZG5\njhUmpB6cjJCsn2I5T4YOPLFDFB3jbkfTxAnS7X0c2KgXRtnCqJytGxnJ3/0UfpXU\nqVzUGN71BmrS/uHq8xYAi8R6e7vxCDUYXIRbRPUiRAz/xYzPu4etq1o14bzJlAAR\neukz9UcxMfeuN/w5UHNSmk+ZgR8uQVTdfpnQ+SfQUUWOVvAXC1XsFQqy0jubSzZ0\nHzfff/qBO2W4f857kYYQnOurMSReW4NNefWvrhlIG8pqikRQ6+oe9hwa3mlLOow+\nnpRXT4R7Ip4jEUrkppq1271Tmg47AM33+Ngh/Ew7yQKBgQDiP47Rq8onHJJPe3M8\nQSzaXcXreyRZ2ct8enN+WWKn3gl+E9UKHUqjBVw1Q0s76zKYk82JdDJe+D1842Gy\n20jg2prDMW9VOEesRaateqFc5H+klOBEnvbmjoV7hekonZ5pL+odHbj3+Bi2y0Vy\nTy1oquZImJSZ6BwqpaQbM10OuQKBgQDKdA91XZ9gVhUc3wP679bhFXLQ8FCHOa4E\nF1ROJANtOw74D0Wc9aZbdC07SoOo6NAF5sQYQ06ydehgXdAMs0Zh870P8A1YfOL/\nwxGnwmOqSFhRrfufB4ZhMDIHLNGaPHcI0xbtdgN0k4lRmq8cQ6LZMkeRndGJSCB6\nduuiFFkGRQKBgH8AFndz60IRM8ASGBmWrErXoKYStdEKBMOXKQWfv1VjughfsZK/\n5omkFKKBZ9X2rKwhK5sg8rWEu19DdDAmD77Id19ifJBlyzXU0z9GOxYd3djRCSL7\n6LR7BErWXI9ECwwYrV4ytQXc6mKRsCX+dArxA9t0atYKCOWXnYr3RiFhAoGBALfx\ndW4kjz7/V5Vwx3QC4BCH5VcTUYdbj9ElxTJuJDLlmvclIRG4W9ryFnqtfCxGw2Lp\nRbfpx6H74RNViUdQx50N0PSfHfENH05UVUFALD+2FZC47EqUkrLREFNWlGZ3k4uQ\nB1/ffso3lmdvjLS4e0iuFzql0pDR2LiMPhF4PV6lAoGBAJsE++YNPG7giy/9vT0N\nhAUUTDLkW2lY6QJg87VURfutUdKI12c79wiCgk47N4hww/cUIXAZdatyIxGpTr4r\nXOZRrlodMSbEMN1Cw/g2wjzzadbfueb4r7OZAxIKsbpOZlyYR35D2ZtYgPJF5kT4\nFG3lgADe4zvWC5fVww1o6EFw\n-----END PRIVATE KEY-----\n",
  "client_email": "firebase-adminsdk-fbsvc@rkbot-db5d6.iam.gserviceaccount.com",
}

if not firebase_admin._apps:
    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred, {'databaseURL': DATABASE_URL})

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

class ShopState(StatesGroup):
    waiting_receipt = State()

@dp.message(Command(commands=["start"]))
async def start(message: types.Message):
    # Зберігаємо юзера в БД
    db.reference(f'users/{message.from_user.id}').update({
        'name': message.from_user.full_name,
        'username': message.from_user.username
    })
    
    # Твоє посилання на сайт (Render автоматично підхопить назву rk-perfume)
    web_url = os.getenv("WEB_URL", "https://rk-perfume.onrender.com")
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛍 Відкрити Магазин", web_app=WebAppInfo(url=web_url))],
        [InlineKeyboardButton(text="📸 Instagram", url="https://instagram.com/rk.perfume.krop")]
    ])
    await message.answer("✨ **RK Perfume**\nВітаємо! Тисни на кнопку нижче, щоб обрати свій аромат:", reply_markup=kb)

@dp.message(F.web_app_data)
async def get_order(message: types.Message, state: FSMContext):
    order_data = message.web_app_data.data
    await state.update_data(current_order=order_data)
    await message.answer(f"💳 **Сума до сплати:** {order_data}\n\nРеквізити: `{CARD_DETAILS}`\n\nНадішліть скріншот оплати.")
    await state.set_state(ShopState.waiting_receipt)

@dp.message(ShopState.waiting_receipt, F.photo)
async def send_to_admin(message: types.Message, state: FSMContext):
    data = await state.get_data()
    admin_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Ок", callback_data=f"ok_{message.from_user.id}"),
         InlineKeyboardButton(text="❌ Ні", callback_data=f"no_{message.from_user.id}")]
    ])
    await bot.send_photo(OWNER_ID, photo=message.photo[-1].file_id, 
                         caption=f"💰 Новий чек від @{message.from_user.username}\nЗамовлення: {data['current_order']}", 
                         reply_markup=admin_kb)
    await message.answer("⏳ Чек на перевірці. Очікуйте.")
    await state.clear()

@dp.callback_query(F.data.startswith("ok_"))
async def order_ok(callback: types.CallbackQuery):
    uid = callback.data.split("_")[1]
    await bot.send_message(uid, "🎉 Оплату підтверджено! Готуємо до відправки.")
    await callback.message.edit_caption(caption=callback.message.caption + "\n\n✅ ПІДТВЕРДЖЕНО")

@dp.callback_query(F.data.startswith("no_"))
async def order_no(callback: types.CallbackQuery):
    uid = callback.data.split("_")[1]
    await bot.send_message(uid, "❌ Чек відхилено. Зв'яжіться з адміном.")
    await callback.message.edit_caption(caption=callback.message.caption + "\n\n❌ ВІДХИЛЕНО")

async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

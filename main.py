import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    Message, 
    CallbackQuery, 
    InlineKeyboardMarkup, 
    InlineKeyboardButton
)

# --- НАСТРОЙКИ ---
BOT_TOKEN = "8975182720:AAHQtCe2rYCigl0syA9DDVGwXKm3DpOo9qc"
ADMIN_ID = 1906257746  # Твой Telegram ID
PLAYER_CHAT_LINK = "https://t.me/+UXAPc_HW6Zs1ZTA0"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Хранилище в памяти
user_applications = {}
pending_questions = {}

# --- СОСТОЯНИЯ FSM ---
class Application(StatesGroup):
    nickname = State()
    age = State()
    mic = State()
    media = State()  # Шаг для YouTube / Twitch
    cases = State()
    portfolio = State()

class AdminReply(StatesGroup):
    waiting_for_question = State()

# --- КЛАВИАТУРЫ ---
def get_admin_keyboard(user_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Одобрить", callback_data=f"app_approve_{user_id}"),
            InlineKeyboardButton(text="❌ Отклонить", callback_data=f"app_reject_{user_id}")
        ],
        [
            InlineKeyboardButton(text="🎙️ На созвон", callback_data=f"app_call_{user_id}"),
            InlineKeyboardButton(text="💬 Задать вопрос", callback_data=f"app_ask_{user_id}")
        ]
    ])

# --- БАЗОВЫЕ КОМАНДЫ ---

@dp.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "✨ <b>Здравствуй, путешественник!</b>\n\n"
        "Я — хранитель вестей острова <b>Solara</b>. Рад видеть нового искателя приключений!\n"
        "Чтобы вступить на наши земли, давай заполним небольшую анкету.\n\n"
        "🔮 <b>Шаг 1 из 6:</b> Как звучит твое имя или никнейм в Minecraft?",
        parse_mode="HTML"
    )
    await state.set_state(Application.nickname)

@dp.message(Command("status"))
async def cmd_status(message: Message):
    user_id = message.from_user.id
    if user_id not in user_applications:
        await message.answer(
            "📜 <b>Твой свиток пуст!</b> Ты еще не отправлял заявку. Нажми /start, чтобы начать путь.",
            parse_mode="HTML"
        )
        return
    
    app_info = user_applications[user_id]
    await message.answer(
        f"🔮 <b>Статус твоей заявки на Solara:</b>\n\n"
        f"👤 Ник: <code>{app_info['nickname']}</code>\n"
        f"📌 Состояние: <b>{app_info['status']}</b>\n\n"
        f"<i>Следи за сообщениями, хранитель острова скоро даст ответ!</i>",
        parse_mode="HTML"
    )

@dp.message(Command("info"))
async def cmd_info(message: Message):
    await message.answer(
        "📜 <b>О СЕРВЕРЕ SOLARA</b>\n\n"
        "🌟 <b>Первый сезон:</b> Solara открывает свою первую главу! Многие наши игроки пришли со знаменитого сервера Horus, так что тебя ждет сплоченное комьюнити.\n\n"
        "🧭 <b>Атмосфера и выживание:</b>\n"
        "• <b>Без координат:</b> Знакомый экран с цифрами отключен — придется ориентироваться по ландшафту.\n"
        "• <b>Островной мир:</b> Каждому предстоит приспособиться к жизни на ограниченной территории и изучить её секреты.\n"
        "• <b>Мертвое море:</b> Можно попробовать просто уплыть вдаль на лодке, но сработает ли это — узнаешь сам.\n\n"
        "✨ <i>Готов сделать первый шаг? Нажимай /start!</i>",
        parse_mode="HTML"
    )

@dp.message(Command("island"))
async def cmd_island(message: Message):
    await message.answer(
        "🌊 <b>ТАЙНЫ ОСТРОВА SOLARA</b> 🧭\n\n"
        "• <b>Изолированный мир:</b> Тысячи блоков вокруг — лишь туман и Мертвый Океан, не пускающий чужаков.\n"
        "• <b>Живой голос:</b> Эхо разносит шепот игроков сквозь пещеры и густые леса.\n"
        "• <b>Древние секреты:</b> Каждая постройка здесь создает историю. Никакого привата — всё держится на доверии и лоре.\n\n"
        "✨ <i>Готов ли ты стать частью этого легендарного сезона?</i>",
        parse_mode="HTML"
    )

# --- ИНТЕРАКТИВНАЯ АНКЕТА ---

@dp.message(Application.nickname)
async def process_nickname(message: Message, state: FSMContext):
    await state.update_data(nickname=message.text)
    await message.answer(
        "Запомнил! ✍️\n\n"
        "🕯️ <b>Шаг 2 из 6:</b> Сколько тебе лет? Остров требует взвешенных решений.",
        parse_mode="HTML"
    )
    await state.set_state(Application.age)

@dp.message(Application.age)
async def process_age(message: Message, state: FSMContext):
    await state.update_data(age=message.text)
    await message.answer(
        "Отлично!\n\n"
        "🎙️ <b>Шаг 3 из 6:</b> На Solara общение идет через Simple Voice Chat. "
        "Есть ли у тебя рабочий микрофон и готов ли ты общаться голосом? (Да/Нет)",
        parse_mode="HTML"
    )
    await state.set_state(Application.mic)

@dp.message(Application.mic)
async def process_mic(message: Message, state: FSMContext):
    await state.update_data(mic=message.text)
    await message.answer(
        "Принято!\n\n"
        "🎥 <b>Шаг 4 из 6: Контент-мейкинг</b>\n"
        "Являешься ли ты ютубером или стримером? Если да, то сколько у тебя подписчиков?\n"
        "Если нет — хотел бы что-то подобное снимать по нашему серверу?\n\n"
        "<i>Мы очень рады стримерам и ютуберам на нашем сервере, но рады и обычным игрокам!</i>",
        parse_mode="HTML"
    )
    await state.set_state(Application.media)

@dp.message(Application.media)
async def process_media(message: Message, state: FSMContext):
    await state.update_data(media=message.text)
    await message.answer(
        "Понял тебя!\n\n"
        "💥 <b>Шаг 5 из 6: Проверка на ответственность</b>\n"
        "Представь: ты исследовал территории и случайно взрывом крипера задел чужой склад, пока владельца нет в сети. "
        "Твои действия?",
        parse_mode="HTML"
    )
    await state.set_state(Application.cases)

@dp.message(Application.cases)
async def process_cases(message: Message, state: FSMContext):
    await state.update_data(cases=message.text)
    await message.answer(
        "Достойно!\n\n"
        "🏰 <b>Финал — Шаг 6 из 6:</b> Расскажи о своих идеях! "
        "Что ты планируешь строить или развивать на острове? (Можешь прикрепить ссылки на прошлые постройки)",
        parse_mode="HTML"
    )
    await state.set_state(Application.portfolio)

@dp.message(Application.portfolio)
async def process_portfolio(message: Message, state: FSMContext):
    await state.update_data(portfolio=message.text)
    data = await state.get_data()
    await state.clear()

    user_applications[message.from_user.id] = {
        "nickname": data['nickname'],
        "status": "⏳ На рассмотрении у администрации"
    }

    await message.answer(
        "✨ <b>Твой свиток отправлен Совету Solara!</b>\n"
        "Мы внимательно изучим твою заявку. Проверить статус всегда можно командой /status.",
        parse_mode="HTML"
    )

    admin_card = (
        f"<b>📜 НОВАЯ ЗАЯВКА НА SOLARA</b>\n\n"
        f"<b>Игрок:</b> @{message.from_user.username or 'без_юзернейма'} (ID: <code>{message.from_user.id}</code>)\n"
        f"<b>Ник:</b> <code>{data['nickname']}</code>\n"
        f"<b>Возраст:</b> {data['age']}\n"
        f"<b>Микрофон:</b> {data['mic']}\n"
        f"<b>Медиа/Стримы:</b> {data['media']}\n\n"
        f"<b>Ситуационный кейс:</b>\n<i>{data['cases']}</i>\n\n"
        f"<b>Опыт и планы:</b>\n<i>{data['portfolio']}</i>"
    )

    await bot.send_message(
        chat_id=ADMIN_ID,
        text=admin_card,
        parse_mode="HTML",
        reply_markup=get_admin_keyboard(message.from_user.id)
    )

# --- АДМИН-ПАНЕЛЬ И ОБРАТНАЯ СВЯЗЬ ---

@dp.callback_query(F.data.startswith("app_"))
async def handle_admin_action(callback: CallbackQuery, state: FSMContext):
    action, user_id_str = callback.data.split("_")[1], callback.data.split("_")[2]
    target_user_id = int(user_id_str)

    if action == "approve":
        user_applications[target_user_id]["status"] = "✅ Одобрено"
        await bot.send_message(
            target_user_id,
            f"🎉 <b>Двери Solara открыты перед тобой!</b>\n\n"
            f"Твоя заявка принята. Заходи в закрытый чат игроков и готовься к отплытию:\n{PLAYER_CHAT_LINK}",
            parse_mode="HTML"
        )
        await callback.message.edit_text(callback.message.text + "\n\n<b>Итог: ✅ ОДОБРЕНО</b>", parse_mode="HTML")

    elif action == "reject":
        user_applications[target_user_id]["status"] = "❌ Отклонено"
        await bot.send_message(
            target_user_id,
            "🌌 <b>Совет принял решение отклонить заявку.</b> Спасибо за интерес к Solara и удачи в поисках своего сервера!",
            parse_mode="HTML"
        )
        await callback.message.edit_text(callback.message.text + "\n\n<b>Итог: ❌ ОТКЛОНЕНО</b>", parse_mode="HTML")

    elif action == "call":
        user_applications[target_user_id]["status"] = "🎙️ Ожидает собеседования"
        await bot.send_message(
            target_user_id,
            "🎙️ <b>Совет хочет поговорить с тобой лично!</b> Наш администратор скоро свяжется с тобой в ЛС для короткого разговора.",
            parse_mode="HTML"
        )
        await callback.message.edit_text(callback.message.text + "\n\n<b>Итог: 🎙️ ВЫЗВАН НА СОЗВОН</b>", parse_mode="HTML")

    elif action == "ask":
        await state.set_state(AdminReply.waiting_for_question)
        await state.update_data(target_user_id=target_user_id)
        await callback.message.answer("💬 Напиши вопрос, который хочешь передать кандидату:")
        await callback.answer()

@dp.message(AdminReply.waiting_for_question)
async def send_admin_question(message: Message, state: FSMContext):
    data = await state.get_data()
    target_user_id = data['target_user_id']
    
    pending_questions[target_user_id] = message.from_user.id
    
    await bot.send_message(
        target_user_id,
        f"❓ <b>Вопрос от Совета Solara:</b>\n\n<i>«{message.text}»</i>\n\n"
        f"👉 <b>Просто напиши ответ следующим сообщением в этот чат!</b>",
        parse_mode="HTML"
    )
    await message.answer("✨ Вопрос отправлен кандидату!")
    await state.clear()

@dp.message()
async def handle_user_reply(message: Message):
    if message.from_user.id in pending_questions:
        admin_id = pending_questions.pop(message.from_user.id)
        await bot.send_message(
            admin_id,
            f"📩 <b>Уточнение от кандидата</b> (ID: <code>{message.from_user.id}</code>):\n\n«{message.text}»",
            parse_mode="HTML",
            reply_markup=get_admin_keyboard(message.from_user.id)
        )
        await message.answer("✨ Твой ответ передан Совету!")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
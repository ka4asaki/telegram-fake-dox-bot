import asyncio
import random
import re
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.client.default import DefaultBotProperties
from faker import Faker
from mimesis import Person
from mimesis.locales import Locale

# === НАСТРОЙКИ ===
API_TOKEN = "bot_token"  # ← ВСТАВЬ СЮДА СВОЙ ТОКЕН
VIP_CODES = {"NeoSamuraiX7"}  # Пример VIP кода
vip_users = set()
blocked_users = {"@admin", "@sk_y444", "@yourfriend"}  # Кого запрещено доксить

# === ИНИЦИАЛИЗАЦИЯ ===
bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
faker = Faker("ru_RU")
person = Person(Locale.RU)

# === ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ===

def is_valid_username(username: str) -> bool:
    return username.startswith('@') and re.match(r'^@[a-zA-Z0-9_]+$', username) is not None

def generate_email():
    return person.email()

def generate_phone():
    return f"+7 {random.randint(700, 799)} {random.randint(100, 999)} {random.randint(1000, 9999)}"

def generate_ip():
    return ".".join(str(random.randint(0, 255)) for _ in range(4))

def generate_date(start_year=1950, end_year=2005):
    start = datetime(start_year, 1, 1)
    end = datetime(end_year, 12, 31)
    rand_date = start + timedelta(days=random.randint(0, (end - start).days))
    return rand_date.strftime("%d.%m.%Y")

def get_gender_name(gender: str):
    return "Женский" if gender == "F" else "Мужской"

def generate_fio(gender: str):
    if gender == "F":
        name = faker.first_name_female()
        patronymic = faker.middle_name_female()
    else:
        name = faker.first_name_male()
        patronymic = faker.middle_name_male()
    surname = faker.last_name()
    return surname, name, patronymic

def make_patronymic(father_name: str, gender: str):
    if gender == "F":
        return father_name + "овна"
    else:
        return father_name + "ович"

# === КОМАНДЫ ===

@dp.message(Command("start"))
async def start_cmd(message: Message):
    await message.answer(
        "Привет! Если хочешь кого-то задоксить — пиши <code>/dox @username</code>\n"
        "Если хочешь получить VIP — пиши <code>/getvip код</code>"
    )

@dp.message(Command("getvip"))
async def get_vip(message: Message):
    parts = message.text.strip().split()
    if len(parts) != 2:
        await message.answer("❗ Укажи код: /getvip код")
        return
    code = parts[1]
    if code in VIP_CODES:
        vip_users.add(message.from_user.id)
        await message.answer("✅ Ты получил VIP-доступ.")
    else:
        await message.answer("❌ Неверный код VIP.")

@dp.message(Command("dox"))
async def dox_user(message: Message):
    parts = message.text.strip().split()
    if len(parts) != 2:
        await message.answer("Формат: /dox @username")
        return

    username = parts[1]

    if not is_valid_username(username):
        await message.answer("❌ Такой вид юзеров не поддерживается.")
        return

    if username in blocked_users:
        await message.answer(f"🚫 Пользователь {username} не найден.")
        return

    is_vip = message.from_user.id in vip_users
    gender = random.choice(["M", "F"])
    surname, name, patronymic = generate_fio(gender)
    email = generate_email()
    phone = generate_phone()
    dob = generate_date(1960, 2005)
    birthplace = faker.city()
    job = faker.job()
    income = f"{random.randint(60000, 160000)} ₽"
    is_retired = "Да" if random.randint(0, 10) > 8 else "Нет"
    work_address = f"{random.choice(['д.', 'п.', 'к.'])} {faker.city()}, {random.choice(['ул.', 'пр.', 'алл.'])} {faker.street_name()}, д. {random.randint(1, 100)}, {random.randint(100000, 999999)}"

    doc = [
        f"📩<b>Email:</b> {email}",
        f"📞 <b>Номер телефона:</b> {phone}",
        f"🎂<b>Дата рождения:</b> {dob}",
        f"🏢<b>Место работы:</b> {work_address}",
        f"👤<b>ФИО:</b> {surname} {name} {patronymic}",
        f"👴<b>Статус пенсионера:</b> {is_retired}",
        f"👶<b>Место рождения:</b> {birthplace}",
        f"👷<b>Работа:</b> {job}",
        f"💰<b>Доход:</b> {income}",
        f"🚻<b>Пол:</b> {get_gender_name(gender)}"
    ]

    if is_vip:
        father_name = faker.first_name_male()
        father_patronymic = faker.middle_name_male()
        new_patronymic = make_patronymic(father_name, gender)

        doc[4] = f"👤<b>ФИО:</b> {surname} {name} {new_patronymic}"

        doc += [
            "——————————————————————————————————————————————————",
            "👪 <b>Родители:</b>",
            f"🧔‍♂️ Отец: ФИО: {surname} {father_name} {father_patronymic}",
            f"🎂 Дата рождения: {generate_date(1950, 1975)}",
            f"📩 Email: {generate_email()}",
            f"🌐 IP: {generate_ip()}",
            f"👩 Мать: ФИО: {surname} {faker.first_name_female()} {faker.middle_name_female()}",
            f"🎂 Дата рождения: {generate_date(1950, 1975)}",
            f"📩 Email: {generate_email()}",
            f"🌐 IP: {generate_ip()}",
            "——————————————————————————————————————————————————",
            f"👧 Брат/сестра: {surname} {faker.first_name_female()} {new_patronymic}",
            f"🎂 Дата рождения: {generate_date(1990, 2000)}",
            "——————————————————————————————————————————————————",
            "<b>💬 Переписывался с:</b> @gennadi_2010 @silanti_1989 @kudrjavtsevsofon @savinavtonom",
            "——————————————————————————————————————————————————",
            f"📍<b>Регистрация:</b> IP: {generate_ip()}",
            f"🌍 Регион: Чукотский АО",
            f"🗓 Дата регистрации: {generate_date(2019, 2024)}",
            "——————————————————————————————————————————————————",
            f"📱 <b>Последний онлайн:</b> {datetime.now().strftime('%d.%m.%Y %H:%M')}",
            f"📲 Устройство: Android (Chrome)",
            f"🏙 Город: {birthplace}"
        ]

    await message.answer("\n".join(doc))

# === ЗАПУСК ===

async def main():
    print("Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

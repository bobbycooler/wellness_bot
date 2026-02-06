from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from utils import get_calorie_goal, get_water_goal


class Registration(StatesGroup):
    weight = State()
    height = State()
    age = State()
    activity = State()
    city = State()
    water_goal = State()
    calorie_goal = State()


registration_router = Router()


@registration_router.message(Command("set_profile"))
async def cmd_set_profile(message: types.Message,
                          state: FSMContext):
    await state.update_data(logged_water=[], logged_calories=[], burned_calories=[])
    await state.set_state(Registration.weight)
    await message.answer("Введите ваш вес (в кг):")


@registration_router.message(Registration.weight)
async def process_weight(message, state):
    await state.update_data(weight=float(message.text))
    await state.set_state(Registration.height)
    await message.answer("Введите ваш рост (в см):")


@registration_router.message(Registration.height)
async def process_height(message, state):
    await state.update_data(height=float(message.text))
    await state.set_state(Registration.age)
    await message.answer("Введите ваш возраст:")


@registration_router.message(Registration.age)
async def process_age(message, state):
    await state.update_data(age=int(message.text))
    await state.set_state(Registration.activity)
    await message.answer("Сколько минут активности у вас в день?")


@registration_router.message(Registration.activity)
async def process_activity(message, state):
    await state.update_data(activity=int(message.text))
    await state.set_state(Registration.city)
    await message.answer("В каком городе вы находитесь?")


@registration_router.message(Registration.city)
async def process_city(message, state):
    await state.update_data(city=message.text)
    await state.set_state(Registration.water_goal)
    await message.answer("Ваша цель по объему выпитой воды в день (в мл)?\n"
                         "Напишите 'Не знаю', чтобы я рассчитал\n"
                         "вашу цель автоматически.")


@registration_router.message(Registration.water_goal)
async def process_water_goal(message, state):
    if message.text == "Не знаю":
        user_data = await state.get_data()
        city = user_data.get("city")
        weight = float(user_data.get("weight"))
        activity = float(user_data.get("activity"))
        water_goal = get_water_goal(weight=weight, activity=activity, city=city)
    else:
        water_goal = int(message.text)

    await state.update_data(water_goal=water_goal)
    await state.set_state(Registration.calorie_goal)
    await message.answer(f"Ваша цель по объему выпитой воды - {water_goal} мл")
    await message.answer("Ваша цель по количеству калорий в день?\n"
                         "Напишите 'Не знаю', чтобы я рассчитал\n"
                         "вашу цель автоматически.")


@registration_router.message(Registration.calorie_goal)
async def process_calorie_goal(message, state):
    if message.text == "Не знаю":
        user_data = await state.get_data()
        weight = float(user_data.get("weight"))
        height = float(user_data.get("height"))
        age = float(user_data.get("age"))
        calorie_goal = get_calorie_goal(weight=weight, height=height, age=age)
    else:
        calorie_goal = int(message.text)

    await state.update_data(calorie_goal=calorie_goal)
    await state.set_state(None)

    user_data = await state.get_data()
    weight = user_data.get("weight")
    height = user_data.get("height")
    age = user_data.get("age")
    activity = user_data.get("activity")
    city = user_data.get("city")
    water_goal = user_data.get("water_goal")
    calorie_goal = user_data.get("calorie_goal")
    await message.answer(f"Регистрация окончена! Ваши данные: \n"
                         f"Ваш вес - {weight}\n"
                         f"Ваш рост - {height}\n"
                         f"Ваш возраст - {age}\n"
                         f"Ваша дневная активность (минут) - {activity}\n"
                         f"Город проживания - {city}\n"
                         f"Ваша цель по количеству калорий в день {calorie_goal}\n"
                         f"Ваша цель по количеству воды (мл) в день {water_goal}\n")

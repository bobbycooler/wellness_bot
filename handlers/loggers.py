import io

from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import BufferedInputFile
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

from utils import calculate_burned_calories, get_food_info, get_sport_recommendations


class FoodLog(StatesGroup):
    waiting_for_product_name = State()
    waiting_for_grams = State()


logger_router = Router()


@logger_router.message(Command("log_water"))
async def log_water(message, command, state):
    user_data = await state.get_data()
    if not command.args:
        return await message.answer("Передайте значения выпитой воды в формате "
                                    "/log_water <мл выпитой воды>")
    try:
        water_amount = int(command.args)
    except ValueError:
        await message.answer("Пожалуйста, введите корректное число.")

    current_progress = user_data.get("logged_water", [])
    current_progress.append(water_amount)
    await state.update_data(logged_water=current_progress)

    water_goal = user_data.get("water_goal")
    remaining_goal = water_goal - sum(current_progress)
    if remaining_goal > 0:
        await message.answer(f"До выполнения цели осталось {remaining_goal} мл.")
    else:
        await message.answer(f"Вы достигли своей цели в {water_goal} мл.")


@logger_router.message(Command("log_food"))
async def log_food(message, command, state):
    if not command.args:
        await state.set_state(FoodLog.waiting_for_product_name)
        return await message.answer("Передайте значения съеденной еды "
                                    "в формате /log_food <продукт>")

    product = command.args
    calories = get_food_info(product_name=product)
    await state.update_data(product_calories_100g=calories)
    await state.set_state(FoodLog.waiting_for_grams)
    await message.answer(f"{product} — {calories} ккал на 100 г. Сколько грамм вы съели?")


@logger_router.message(FoodLog.waiting_for_grams)
async def process_grams(message, state):
    try:
        cnt = float(message.text)
    except ValueError:
        return await message.answer("Пожалуйста, введите корректное число грамм.")

    user_data = await state.get_data()
    product_calories_100g = user_data.get("product_calories_100g")
    current_progress = user_data.get("logged_calories", [])

    curr_logged_calories = cnt / 100 * product_calories_100g
    current_progress.append(curr_logged_calories)
    await state.update_data(logged_calories=current_progress)

    await state.set_state(None)

    await message.answer(f"Записано {(cnt / 100 * curr_logged_calories):.2f} ккал.")


@logger_router.message(Command("log_workout"))
async def log_workout(message, command, state):
    try:
        activity_type, activity_time = command.args.split(' ')
        activity_time = int(activity_time)
    except (ValueError, AttributeError):
        return await message.answer("Передайте значения вашей тренировки "
                                    "в формате /log_workout <тип тренировки> <время (мин)>")

    user_data = await state.get_data()
    weight = user_data.get("weight")
    burned_calories, required_water = calculate_burned_calories(activity_type=activity_type,
                                                                weight=weight,
                                                                duration=activity_time)
    current_progress = user_data.get("burned_calories", [])
    current_progress.append(burned_calories)
    await state.update_data(burned_calories=current_progress)

    water_goal = user_data.get("water_goal")
    water_goal += required_water
    await state.update_data(water_goal=water_goal)

    await message.answer(f"{activity_type} {activity_time} минут - {burned_calories} ккал. "
                         f"Дополнительно: выпейте {required_water} мл воды.")


@logger_router.message(Command("check_progress"))
async def check_progress(message, state):
    user_data = await state.get_data()

    water_goal = user_data.get("water_goal")
    calorie_goal = user_data.get("calorie_goal")

    water_current = user_data.get("logged_water", [])
    calorie_burn_current = user_data.get("burned_calories", [])
    calorie_eat_current = user_data.get("logged_calories", [])

    await message.answer("Прогресс:\n"
                         "Вода:\n"
                         f"- Выпито: {sum(water_current)} мл из {water_goal} мл.\n"
                         f"- Осталось: {(water_goal - sum(water_current)):.2f} мл.\n"
                         "Калории:\n"
                         f"- Потреблено: {sum(calorie_eat_current):.2f} ккал из {calorie_goal} ккал.\n"
                         f"- Сожжено: {sum(calorie_burn_current):.2f} ккал.\n"
                         f"- Баланс: {(sum(calorie_eat_current) - sum(calorie_burn_current)):.2f} ккал.")

    plt.figure(figsize=(8, 4))
    plt.plot(water_current, marker='o', linestyle='-', color='green')
    plt.axhline(y=water_goal, color='red', linestyle='--', label=f'Цель ({water_goal} мл)')
    ax = plt.gca()
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    plt.title("Статистика выпитой воды")
    plt.xlabel("Ваши записи")
    plt.ylabel("Мл")
    plt.grid(True)

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plt.close()

    image_from_buffer = BufferedInputFile(buffer.getvalue(), filename="water_graph.png")
    await message.answer_photo(photo=image_from_buffer, caption="Ваш график потребления воды")

    max_len = max(len(calorie_eat_current), len(calorie_burn_current))
    indices = range(1, max_len + 1)

    plt.figure(figsize=(8, 4))

    plt.plot(indices[:len(calorie_eat_current)], calorie_eat_current, marker='o', label='Набрано, ккал', color='green')
    plt.plot(indices[:len(calorie_burn_current)], calorie_burn_current, marker='s', label='Сожжено, ккал', color='blue')
    plt.axhline(y=calorie_goal, color='red', linestyle='--', alpha=0.6, label=f'Цель ({calorie_goal} ккал)')

    ax = plt.gca()
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))

    plt.title("Статистика калорий")
    plt.xlabel("Ваши записи")
    plt.ylabel("Ккал")
    plt.grid(True)
    plt.legend()

    # Сохранение и отправка
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', dpi=100)
    buffer.seek(0)
    plt.close()

    photo = BufferedInputFile(buffer.getvalue(), filename="calories_graph.png")
    await message.answer_photo(photo=photo, caption="Ваш график калорий")


@logger_router.message(Command("get_recommendation"))
async def get_recommendation(message, command, state):
    try:
        available_time, calories_2_burn = command.args.split(' ')
        available_time = int(available_time)
        calories_2_burn = int(calories_2_burn)
    except (ValueError, AttributeError):
        return await message.answer("Передайте команду, количество вашего свободного времени и желаемый объем сжигаемых калорий"
                                    "для занятия спортом в формате /get_recommendation <время (мин)> <ккал>")

    user_data = await state.get_data()
    weight = user_data.get("weight")
    city = user_data.get("city")
    recommendations = get_sport_recommendations(excess_calories=calories_2_burn,
                                               weight=weight,
                                               available_time=available_time,
                                               city=city)

    text = f"Рекомендации, чтобы сжечь {calories_2_burn} ккал:\n\n"

    for r in recommendations[:3]:
        text += (
            f"{r['activity'].capitalize()} - {r['calories_may_burn']} ккал "
            f"(Нужно {r['time_to_goal']} мин и {r['water_needed']} мл воды)\n"
        )

    await message.answer(text)

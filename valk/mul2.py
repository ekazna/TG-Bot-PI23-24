###################### КОД БОТА ДЛЯ МАСТЕРА ######################

from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InputFile
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery
from aiogram.dispatcher import FSMContext
from aiogram import Dispatcher
import datetime
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP
import sqlite3 as sl
from aiogram.utils.callback_data import CallbackData
con = sl.connect('tbot.db')


API_TOKEN = '' ########################################################
 

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
my_master_id = 1
global_info_change = False
add_service = False
added_service_type = ''
add_price = False
added_service_price = 1000
added_service_name = " "

with con:
    cur = con.cursor()
    cur.execute("""SELECT MAX(id) FROM clientsSh""")
    result = cur.fetchall()[0][0]
    if result:
        auto_id = int(result)+1
    else:
        auto_id = 1
    cur.close()




@dp.message_handler(commands=['startM'])
async def start(message: types.Message, state: FSMContext):
    ####
    global regime
    regime = "MASTER"
    #####
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["Мое расписание", "Мои записи", "О себе", "Услуги", "Добавить услугу"]
    keyboard.add(*buttons)
    await message.answer("Чем я могу помочь?", reply_markup=keyboard)


cbd_master_schedule_cancel_free = CallbackData('schedule_keyboard_1', 'time_id', 'tt')
cbd_master_schedule_cancel_booked = CallbackData('schedule_keyboard_2', 'time_id', 'req', "cc") # req - 1 оставить 2 удалить
@dp.callback_query_handler(DetailedTelegramCalendar.func())
async def inline_kb_answer_callback_handler(query):
    global my_master_id
    result, key, step = DetailedTelegramCalendar().process(query.data)
    if not result and key:
        await bot.edit_message_text(f"Выберите",
                                    query.message.chat.id,
                                    query.message.message_id,
                                    reply_markup=key)
    elif result:
        await bot.edit_message_text(f"Вы выбрали {result}\n",
                                    query.message.chat.id,
                                    query.message.message_id)
        print(result) #дата 2023-12-26
        request_type = int(query.data.split('_')[-1])
        if request_type == 1:
            with con:
                cursor = con.cursor()
                cursor.execute(
                    """SELECT time_id, begin, free FROM schedule WHERE date = ? AND master_id = ?""",
                    (str(result), my_master_id))

                records = cursor.fetchall()
                cursor.close()
            print(records)
            free = ''
            if records == []:
                await bot.send_message(query.message.chat.id, text="Расписание пусто")
            for i in records:
                if i[2] == 1:
                    free = "Свободно"
                else:
                    free = 'Занято'
                record_text = f'{i[1]}\n{free}'
                if i[2] == 1:
                    schedule_keyboard_1 = types.InlineKeyboardMarkup()
                    schedule_keyboard_1.add(types.InlineKeyboardButton("Удалить время",
                                            callback_data=cbd_master_schedule_cancel_free.new(i[0], i[1].replace(':', '!', 1))))
                    await bot.send_message(query.message.chat.id, text=record_text,
                                           reply_markup=schedule_keyboard_1)
                else:
                    await bot.send_message(query.message.chat.id, text=record_text)

        if request_type == 2:
            with con:
                cursor = con.cursor()
                cursor.execute(
                    """SELECT s.time_id, s.begin, se.service_id, se.categoty, se.name, se.price  FROM schedule s LEFT OUTER JOIN services se ON se.service_id = s.service_id WHERE s.date = ? AND s.master_id = ? AND s.free = 0 ORDER BY s.begin""",
                    (str(result), my_master_id))

                records = cursor.fetchall()
                cursor.close()
            print(records)
            if records == []:
                await bot.send_message(query.message.chat.id, text=f"Нет записей на {str(result)}")
            c = 0
            for i in records:
                c += 1
                if i[-1] == None:
                    message = f'#{c}\n{i[1]}\nУслуга не указана'
                else:
                    message = f'#{c}\n{i[1]}\nУслуга: {i[3] + " " + i[4].lower()}\nОплата: {i[-1]}₽'

                schedule_keyboard_2 = types.InlineKeyboardMarkup()
                schedule_keyboard_2.add(types.InlineKeyboardButton("Освободить запись",
                                                                   callback_data=cbd_master_schedule_cancel_booked.new(
                                                                       i[0],1, c)))
                schedule_keyboard_2.add(types.InlineKeyboardButton("Отменить и удалить время",
                                                                   callback_data=cbd_master_schedule_cancel_booked.new(
                                                                       i[0],2, c)))
                await bot.send_message(query.message.chat.id, text=message,
                                       reply_markup=schedule_keyboard_2)






#request_type = 1
@dp.message_handler(lambda message: message.text == "Мое расписание")
async def send_my_master_schedule(message: types.Message):
    mystr = '_0_1'
    calendar, step = DetailedTelegramCalendar(min_date=datetime.date.today(), max_date=datetime.date(2024, 5, 15),
                                              locale='ru', extra=mystr).build()

    await message.answer(f"Выберите год", reply_markup=calendar)


#request_type = 2
@dp.message_handler(lambda message: message.text == "Мои записи")
async def send_my_master_schedule(message: types.Message):
    mystr = '_0_2'
    calendar, step = DetailedTelegramCalendar(min_date=datetime.date.today(), max_date=datetime.date(2024, 5, 15),
                                              locale='ru', extra=mystr).build()

    await message.answer(f"Выберите год", reply_markup=calendar)




@dp.message_handler(lambda message: message.text == "О себе")
async def send_my_master_info(message: types.Message):
    global my_master_id
    with con:
        cursor = con.cursor()
        cursor.execute(
            """SELECT info FROM masters WHERE master_id = ?""", (my_master_id, ))

        records = cursor.fetchall()
        cursor.close()
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton("Изменить", callback_data="Изменить о себе"))
    await message.answer(records[0][0], reply_markup=keyboard)

@dp.callback_query_handler(text="Изменить о себе")
async def send_change_master_info_2(call: types.CallbackQuery):
    global global_info_change
    global_info_change = True
    await call.message.answer("В следующем сообщении напишите новый вариант:")


#cbd_choose_service_date = CallbackData('calendar_for_service', 'service_name', 'service_category', 'calendar')
@dp.callback_query_handler(cbd_master_schedule_cancel_free.filter())
async def send_cancel_free_times(call: types.CallbackQuery, callback_data: dict):
    time_id = int(callback_data["time_id"])
    tt = callback_data["tt"].replace("!", ":", 1)
    with con:
        cursor = con.cursor()
        cursor.execute(
            """DELETE FROM schedule WHERE time_id = ? """, (time_id,))

        con.commit()
        cursor.close()

    await call.message.answer(f"Время {tt} удалено ")



# 'time_id', 'req') #1 оставить 2 удалить
@dp.callback_query_handler(cbd_master_schedule_cancel_booked.filter())
async def send_cancel_free_times(call: types.CallbackQuery, callback_data: dict):
    time_id = int(callback_data["time_id"])
    req = int(callback_data["req"])
    c = callback_data["cc"]
    if req == 2:

        with con:
            cursor = con.cursor()
            cursor.execute(
                """DELETE FROM clientsSh WHERE time_id = ? """, (time_id,))

            con.commit()
            cursor.execute(
                """DELETE FROM schedule WHERE time_id = ? """, (time_id,))

            con.commit()
            cursor.close()

        await call.message.answer(f"Запись #{c} удалена (вместе со временем)")
    else:
        with con:
            cursor = con.cursor()
            cursor.execute(
                """DELETE FROM clientsSh WHERE time_id = ? """, (time_id,))

            con.commit()
            cursor.execute(
                """UPDATE schedule SET free = 1, service_id =?  WHERE time_id = ?""", (None, time_id))

            con.commit()
            cursor.close()
        await call.message.answer(f"Запись #{c} удалена (время освобождено)")



cbd_master_delete_service = CallbackData('delete_service_keyboard', 's_id')
@dp.message_handler(lambda message: message.text == "Услуги")
async def send_services_info_to_master(message: types.Message):
    global my_master_id
    with con:
        cursor = con.cursor()
        cursor.execute(
            """SELECT * FROM services ORDER BY categoty, name""")

        records = cursor.fetchall()
        cursor.close()
    for i in records:
        delete_service_keyboard = types.InlineKeyboardMarkup()
        delete_service_keyboard.add(types.InlineKeyboardButton("Удалить услугу", callback_data=cbd_master_delete_service.new(i[0])))
        await message.answer(f'{i[2]+": "+i[1]}\nЦена: {i[3]}₽', reply_markup=delete_service_keyboard)



@dp.callback_query_handler(cbd_master_delete_service.filter())
async def send_delete_service(call: types.CallbackQuery, callback_data: dict):
    service_id = int(callback_data["s_id"])
    with con:
        cursor = con.cursor()
        cursor.execute(
            """SELECT name, categoty, price FROM services WHERE service_id = ?""", (service_id, ))

        record = cursor.fetchall()[0]
        cursor.execute("""DELETE FROM services WHERE service_id = ? """, (service_id,))
        con.commit()
    await call.message.answer(f"удалена услуга {record[1].upper()} {record[0].upper()} (цена:{record[2]}₽)")



cbd_m_choose_service_type = CallbackData('m_s_type_keyboard', 's_type')
@dp.message_handler(lambda message: message.text == "Добавить услугу")
async def send_master_add_service_1(message: types.Message):
    services = ["Маникюр", "Педикюр","Наращивание"]
    m_s_type_keyboard = types.InlineKeyboardMarkup()
    for i in services:
        m_s_type_keyboard.add(types.InlineKeyboardButton(text=i, callback_data=cbd_m_choose_service_type.new(i)))
    await message.answer("Выберите тип услуги:", reply_markup=m_s_type_keyboard)


@dp.callback_query_handler(cbd_m_choose_service_type.filter())
async def send_m_add_service_2(call: types.CallbackQuery, callback_data: dict):
    global add_service
    global added_service_type
    added_service_type = callback_data["s_type"]
    add_service = True
    await call.message.answer("Введите краткое описание услуги")


@dp.message_handler()
async def echo(message: types.Message):
    global global_info_change
    global my_master_id
    global add_service
    global add_price
    global added_service_type
    global added_service_price
    global added_service_name

    if not global_info_change and not add_service and not add_price:
        await message.answer("Извините! Я не знаю такой команды!")
    elif global_info_change:
        global_info_change = False
        with con:
            cursor = con.cursor()
            cursor.execute(
               """UPDATE masters SET info = ? WHERE master_id = ?""", (message.text, my_master_id))
            con.commit()
            cursor.close()

        await message.answer(f"Информация о себе изменена на\n{message.text}")

    elif add_service:
        add_service = False
        added_service_name = message.text
        add_price = True
        await message.answer("Введите цену (целое число без значка рубля)")

    elif add_price:
        add_price = False
        try:
            added_service_price = int(message.text)
            with con:
                cursor = con.cursor()
                cursor.execute("""SELECT MAX(service_id) FROM services""")
                new_id = int(cursor.fetchall()[0][0]) +1

                cursor.execute(
                    """INSERT INTO services(service_id, name, categoty, price, length)
                                          VALUES
                                          (?, ?, ?, ?, 30);""", (new_id, added_service_name, added_service_type.capitalize(),added_service_price))
                con.commit()
                cursor.close()
            suc_mess = f"Добавлена услуга: \n{added_service_type.upper()} {added_service_name.upper()} (цена {added_service_price}₽)"
            added_service_price = 1000
            added_service_type = ""
            added_service_name = ""
            await message.answer(suc_mess)

        except Exception as e:
            print(e)
            added_service_price = 1000
            added_service_type = ""
            added_service_name = ""
            await message.answer("Не удалось добавить услугу, попробуйте снова")



if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)




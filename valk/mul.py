###################### КОД БОТА ДЛЯ КЛИЕНТА ######################

## используются для передачи дат (библиотека изменена)
##### Lib -> site_packages -> telegram_bot_calendar -> base
##### Lib -> site_packages -> telegram_bot_calendar -> detailed



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


API_TOKEN = '6549227102:AAH8uD9p1-90HJRjuHrExa3EgXx28d8e_do'


bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)




with con:
    cur = con.cursor()
    cur.execute("""SELECT MAX(id) FROM clientsSh""")
    result = cur.fetchall()[0][0]
    if result:
        auto_id = int(result)+1
    else:
        auto_id = 1
    cur.close()


cbd_choose_schedule = CallbackData('choose_schedule_keyboard', 'time_id', "service_id")

@dp.callback_query_handler(DetailedTelegramCalendar.func())
async def inline_kb_answer_callback_handler(query):
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
        #print(result) #дата 2023-12-26

        service_id = int(query.data.split('_')[-2])
        master_id = int(query.data.split('_')[-1])
        with con:
            cursor = con.cursor()
            if master_id!=0:
                cursor.execute("""SELECT time_id, begin FROM schedule WHERE date = ? AND master_id = ? AND free = 1""", (str(result), master_id ))
            else:
                cursor.execute("""SELECT time_id, begin FROM schedule WHERE date = ? AND free = 1""", (str(result),))

            records = cursor.fetchall()
            cursor.close()

        choose_schedule_keyboard = types.InlineKeyboardMarkup()
        for j in records:
            choose_schedule_keyboard.add(types.InlineKeyboardButton(text=j[1], callback_data=cbd_choose_schedule.new(j[0],service_id)))
        if master_id != 0:
            choose_schedule_keyboard.add(types.InlineKeyboardButton(text="Назад", callback_data="cbcal_0_s_y_2023_12_26_0_"+str(master_id)))
        else:
            choose_schedule_keyboard.add(
                types.InlineKeyboardButton(text="Назад", callback_data="cbcal_0_s_y_2023_12_26_" + str(service_id) +"_0"))
        if records == []:
            await bot.send_message(query.message.chat.id, text="Нет доступных интервалов", reply_markup=choose_schedule_keyboard)
        else:
            await bot.send_message(query.message.chat.id, text="Выберите время:", reply_markup=choose_schedule_keyboard)


cbd_confirm_schedule = CallbackData('confirm_schedule_keyboard', 'time_id', "service_id")
@dp.callback_query_handler(cbd_choose_schedule.filter())
async def send_reserved_confirmation(call: types.CallbackQuery, callback_data: dict):
    time_id = int(callback_data["time_id"])
    service_id = int(callback_data["service_id"])
    with con:
        cursor = con.cursor()

        cursor.execute("""SELECT master_id, date, begin FROM schedule WHERE time_id=?""", (time_id,))
        records = cursor.fetchall()
        master_id = int(records[0][0])
        date = records[0][1]
        time = records[0][2]

        cursor.execute("""SELECT name, surname FROM masters WHERE master_id=?""", (master_id,))
        records = cursor.fetchall()
        master_name = records[0][1] + ' ' + records[0][0]

        message = f"Мастер: {master_name}\nЗапись на {date} в {time}"

        if service_id != 0:
            cursor.execute("""SELECT name, categoty, price FROM services WHERE service_id=?""", (service_id,))
            records = cursor.fetchall()[0]
            message = f"Мастер: {master_name}\nЗапись на {date} в {time}\nУслуга: {records[1] + ' ' +records[0].lower()}\nЦена: {records[2]}₽"
        cursor.close()


    confirm_schedule_keyboard = types.InlineKeyboardMarkup()
    confirm_schedule_keyboard.add(types.InlineKeyboardButton(text="Подтвердить запись", callback_data=cbd_confirm_schedule.new(time_id, service_id)))
    confirm_schedule_keyboard.add(types.InlineKeyboardButton(text="Не подтверждать", callback_data="NOTHING"))
    await call.message.answer(message+"\nПодтвердить?", reply_markup=confirm_schedule_keyboard)


@dp.callback_query_handler(cbd_confirm_schedule.filter())
async def send_confirmation_of_reservation(call: types.CallbackQuery, callback_data: dict):
    global auto_id
    time_id = int(callback_data["time_id"])
    service_id = int(callback_data["service_id"])

    ###################
    client_id = 1
    ###################

    with con:
        cursor = con.cursor()
        if service_id != 0:
            cursor.execute("""UPDATE schedule SET free = ?, service_id = ? WHERE time_id = ?""" , (0,service_id, time_id))
        else:
            cursor.execute("""UPDATE schedule SET free = ? WHERE time_id = ?""" , (0, time_id))


        con.commit()

    with con:
        cursor = con.cursor()
        cursor.execute("""INSERT INTO clientsSh(id, time_id, client_id)
                                              VALUES
                                              (?, ?, ?)""", (auto_id, time_id, client_id))
        con.commit()

    auto_id += 1

    with con:
        cursor = con.cursor()

        cursor.execute("""SELECT master_id, date, begin FROM schedule WHERE time_id=?""", (time_id,))
        records = cursor.fetchall()
        master_id = int(records[0][0])
        date = records[0][1]
        time = records[0][2]

        cursor.execute("""SELECT name, surname FROM masters WHERE master_id=?""", (master_id,))
        records = cursor.fetchall()
        master_name = records[0][1] + ' ' + records[0][0]

        message = f"Мастер: {master_name}\nЗапись на {date} в {time}"

        if service_id != 0:
            cursor.execute("""SELECT name, categoty, price FROM services WHERE service_id=?""", (service_id,))
            records = cursor.fetchall()[0]
            message = f"Мастер: {master_name}\nЗапись на {date} в {time}\nУслуга: {records[1] + ' ' +records[0].lower()}\nЦена: {records[2]}₽"
        cursor.close()

    await call.message.answer("Запись подтверждена!\n" + message)




@dp.message_handler(commands=['start'])
async def start(message: types.Message, state: FSMContext):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["Мастера", "Услуги", "Мои записи", "Контакты", "Вдохновение"]
    keyboard.add(*buttons)
    await message.answer("Чем я могу помочь?", reply_markup=keyboard)



@dp.message_handler(lambda message: message.text == "Вдохновение")
async def send_inspiration(message: types.Message):
    photo = InputFile("files/nails1.jpg")
    await bot.send_photo(chat_id=message.chat.id, photo=photo)
    await message.answer("Больше картинок в нашем телеграм канале t.me/ValkyraeBeauty_bot")


@dp.message_handler(lambda message: message.text == "Контакты")
async def send_about_us(message: types.Message):
    await message.answer("Мы - салон маникюра Valkirae\nНаш телефон: +77777777777\nЧасы работы: c 9 до 19\nАдрес: улица Большая Полянка, 28к1\nhttps://yandex.ru/maps/-/CDqHVFZO")


cbd_choose_master = CallbackData('choose_master_keyboard', "sc", 'master_id')
#sc = show or choose, show - 1, choose - 2
@dp.message_handler(lambda message: message.text == "Мастера")
async def send_masters(message: types.Message):

    with con:
        cursor = con.cursor()

        cursor.execute("""SELECT * FROM masters""")
        records = cursor.fetchall()
        cursor.close()

    for i in records:
        choose_master_keyboard = types.InlineKeyboardMarkup()
        choose_master_keyboard.add(types.InlineKeyboardButton(text="Подробнее", callback_data=cbd_choose_master.new(1, int(i[0]))))
        choose_master_keyboard.add(types.InlineKeyboardButton(text="Записаться", callback_data=cbd_choose_master.new(2, int(i[0]))))
        mes = f"{i[2]} {i[1]}\nМастер по маникюру"

        filename = 'files/master' + str(i[0]) + '.jpg'
        photo = InputFile(filename)
        await bot.send_photo(chat_id=message.chat.id, photo=photo)

        await message.answer(mes, reply_markup=choose_master_keyboard)



@dp.callback_query_handler(cbd_choose_master.filter())
async def send_master_info_or_sche(call: types.CallbackQuery, callback_data: dict):
    sc = callback_data["sc"]
    master_id = int(callback_data["master_id"])
    if sc == '1':
        with con:
            cursor = con.cursor()

            cursor.execute("""SELECT info FROM masters WHERE master_id=?""", (master_id, ))
            records = cursor.fetchall()
            cursor.close()

        choose_master_keyboard = types.InlineKeyboardMarkup()
        choose_master_keyboard.add(types.InlineKeyboardButton(text="Записаться", callback_data=cbd_choose_master.new(2, master_id)))

        filename = 'files/master' + str(master_id) + '.jpg'
        photo = InputFile(filename)
        await bot.send_photo(chat_id=call.message.chat.id, photo=photo)
        await call.message.answer(records[0][0], reply_markup=choose_master_keyboard)
    else:
        mystr = '_0_' + str(master_id)
        calendar, step = DetailedTelegramCalendar(min_date=datetime.date.today(), max_date=datetime.date(2024, 5, 15),
                                                  locale='ru', extra=mystr).build()

        await call.message.answer(
            f"Выберите год",
            reply_markup=calendar)





cbd_choose_service = CallbackData('service_keyboard', 'service_name')
@dp.message_handler(lambda message: message.text == "Услуги")
async def send_services(message: types.Message):
    service_keyboard = types.InlineKeyboardMarkup()
    services = ["Маникюр", "Педикюр","Наращивание"]
    for i in services:
        service_keyboard.add(types.InlineKeyboardButton(text=i, callback_data=cbd_choose_service.new(i)))
    await message.answer("Доступные услуги:", reply_markup=service_keyboard)


@dp.callback_query_handler(text="услуги")
async def send_services1(call: types.CallbackQuery):
    service_keyboard = types.InlineKeyboardMarkup()
    services = ["Маникюр", "Педикюр","Наращивание"]
    for i in services:
        service_keyboard.add(types.InlineKeyboardButton(text=i, callback_data=cbd_choose_service.new(i)))
    await call.message.answer("Доступные услуги:", reply_markup=service_keyboard)




cbd_my_appontments = CallbackData('my_app_keyboard', 'id', 'time_id', 'num_z')
@dp.message_handler(lambda message: message.text == "Мои записи")
async def send_my_appointments(message: types.Message):

    with con:
        cursor = con.cursor()

        cursor.execute("""SELECT c.id, c.time_id, s.begin, s.date, m.name, m.surname, se.name, se.categoty, se.price FROM clientsSh c JOIN schedule s ON c.time_id = s.time_id JOIN masters m ON m.master_id = s.master_id LEFT OUTER JOIN services se ON s.service_id = se.service_id""")
        records = cursor.fetchall()
        cursor.close()
        print(records)

    if len(records) == 0:
        await bot.send_message(message.chat.id, text = "У вас нет записей")
    else:
        c = 0
        for i in records:
            c += 1
            my_app_keyboard = types.InlineKeyboardMarkup()
            my_app_keyboard.add(types.InlineKeyboardButton(text="Отменить", callback_data=cbd_my_appontments.new(i[0], i[1], c)))
            if i[-1] != None:
                MyMes = f"ЗАПИСЬ #{c}\nМастер: {i[5] + ' ' + i[4]}\nЗапись на {i[3]} в {i[2]}\nУслуга: {i[7] + ' ' +i[6].lower()}\nЦена: {i[8]}₽"
            else:
                MyMes = f"ЗАПИСЬ #{c}\nМастер: {i[5] + ' ' + i[4]}\nЗапись на {i[3]} в {i[2]}"

            await bot.send_message(message.chat.id, text=MyMes, reply_markup=my_app_keyboard)


cbd_appointment_cancelation = CallbackData('appointment_cancelation_keyboard', 'id', 'time_id')
@dp.callback_query_handler(cbd_my_appontments.filter())
async def send_confirm_appointment_cancelation(call: types.CallbackQuery, callback_data: dict):
    c = callback_data["num_z"]
    id = callback_data["id"]
    time_id = callback_data["time_id"]

    appointment_cancelation_keyboard = types.InlineKeyboardMarkup()
    appointment_cancelation_keyboard.add(types.InlineKeyboardButton(text="Да", callback_data=cbd_appointment_cancelation.new(id, time_id)))
    appointment_cancelation_keyboard.add(types.InlineKeyboardButton(text="Нет", callback_data='noToAppCancel'))

    await call.message.answer(text=f"Отменить запись #{c}", reply_markup=appointment_cancelation_keyboard)



@dp.callback_query_handler(cbd_appointment_cancelation.filter())
async def send_full_appointment_cancelation(call: types.CallbackQuery, callback_data: dict):
    id = int(callback_data["id"])
    time_id = int(callback_data["time_id"])

    with con:
        cursor = con.cursor()
        cursor.execute(
            """DELETE FROM clientsSh WHERE id = ? """, (id, ))
        con.commit()

        cursor = con.cursor()
        cursor.execute(
            """ UPDATE schedule SET free = 1, service_id = ? WHERE time_id = ? """, (None, time_id))
        con.commit()
        cursor.execute(
            """SELECT * from clientsSh """)
        cursor.fetchall()
        print(cursor.fetchall())

    await call.message.answer(text="Запись отменена")



cbd_choose_exact_service = CallbackData('choosing_service_keyboard', 'service_name', "service_category")
@dp.callback_query_handler(cbd_choose_service.filter())
async def send_service_categories(call: types.CallbackQuery, callback_data: dict):
    service = callback_data["service_name"]
    with con:
        cursor = con.cursor()
        cursor.execute("""SELECT name, price FROM services WHERE categoty=?""", (service,))

        records = cursor.fetchall()
        cursor.close()
    choosing_services_keyboard = types.InlineKeyboardMarkup()
    message = ""
    for i in records:
        message += i[0] + ": " + str(i[1]) + '₽\n'
        choosing_services_keyboard.add(types.InlineKeyboardButton(text=i[0], callback_data=cbd_choose_exact_service.new(i[0], service)))
    choosing_services_keyboard.add(types.InlineKeyboardButton(text="Назад", callback_data="услуги"))
    await call.message.answer(message, reply_markup=choosing_services_keyboard)


cbd_choose_service_date = CallbackData('calendar_for_service', 'service_name', 'service_category', 'calendar')
@dp.callback_query_handler(cbd_choose_exact_service.filter())
async def send_service_calendar(call: types.CallbackQuery, callback_data: dict):

    with con:
        cursor = con.cursor()
        cursor.execute("""SELECT service_id FROM services WHERE categoty=? AND name=?""", (callback_data["service_category"],callback_data["service_name"]))

        records = cursor.fetchall()
        cursor.close()
    mystr = '_' + str(records[0][0]) + '_0'
    calendar, step = DetailedTelegramCalendar(min_date=datetime.date.today(), max_date=datetime.date(2024, 5, 15),
                                              locale='ru', extra=mystr).build()

    await call.message.answer(
        f"Выберите год",
        reply_markup=calendar)








@dp.callback_query_handler(text="NOTHING")
async def send_not_approved(call: types.CallbackQuery):
    await call.message.answer("Окей, запись не подтверждена")



@dp.callback_query_handler(text="noToAppCancel")
async def send_cancel2(call: types.CallbackQuery):
    await call.message.answer("Ок!")



@dp.message_handler()
async def echo(message: types.Message):
    await message.answer("Извините! Я не знаю такой команды!")



if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)




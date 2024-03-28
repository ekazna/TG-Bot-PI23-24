############### что осталось от создания БД (не запускать!!!!)

import sqlite3 as sl
con = sl.connect('tbot.db')
with con:
    cursor = con.cursor()

    siq = """INSERT INTO schedule(time_id, date, begin, free, master_id)
                                     VALUES
                                    (10, '2023-12-29', '18:30', 1 , 1);"""
    count = cursor.execute(siq)
    con.commit()
    siq = """INSERT INTO schedule(time_id, date, begin, free, master_id)
                                         VALUES
                                        (11, '2023-12-29', '19:35', 1 , 1);"""
    count = cursor.execute(siq)
    con.commit()
    #records = cursor.fetchall()
    #print("Всего строк:  ", len(records))
    #print("Вывод каждой строки")
    #for row in records:
        #print(row)

    cursor.close()




'''
with con:
    cur = con.cursor()
    cur.execute("CREATE TABLE clients(client_id, name, surname, phone, nick)")
    cur.execute("CREATE TABLE masters(master_id, name, surname, phone, nick, info)")
    cur.execute("CREATE TABLE services(service_id, name, categoty, price, length)")
    cur.execute("CREATE TABLE schedule(time_id, begin, end, free, master_id, service_id,date,  FOREIGN KEY(master_id) REFERENCES masters(master_id), FOREIGN KEY(service_id) REFERENCES services(service_id))")
    cur.execute("CREATE TABLE clientsSh(id, time_id, client_id, FOREIGN KEY(time_id) REFERENCES schedule(time_id), FOREIGN KEY(client_id) REFERENCES clients(client_id))")
'''
'''
cursor = con.cursor()
    siq = """INSERT INTO clients(client_id, name, surname, phone, nick)
                              VALUES
                              (1, 'Ekaterina', 'Znamenskaya', '+79166794540', 'ekazna');"""
    count = cursor.execute(siq)
    siq = """INSERT INTO masters(master_id, name, surname, phone, nick, info)
                                  VALUES
                                  (1, 'Анна', 'Иванова', '+79166794541', 'dar', 'Меня зовут Иванова Анна и я - мастер ногтевого сервиса.\nОпыт работы более 10 лет\nУслуги:\n - Аппаратный маникюр\n - Снятие гель лака\n - Классический маникюр\n - Французский маникюр');"""
    count = cursor.execute(siq)
    siq = """INSERT INTO masters(master_id, name, surname, phone, nick, info)
                                  VALUES
                                  (2, 'Дарья', 'Волкова', '+79166794542', 'dari', 'Описание Даши');"""
    count = cursor.execute(siq)
    siq = """INSERT INTO services(service_id, name, categoty, price, length)
                                      VALUES
                                      (1, 'Без покрытия', 'Маникюр', 800, 40);"""
    count = cursor.execute(siq)
    siq = """INSERT INTO services(service_id, name, categoty, price, length)
                                          VALUES
                                          (2, 'Лак', 'Маникюр', 1000, 80);"""
    count = cursor.execute(siq)
    siq = """INSERT INTO services(service_id, name, categoty, price, length)
                                          VALUES
                                          (3, 'Гель-лак', 'Маникюр', 2000, 100);"""
    count = cursor.execute(siq)





    con.commit()
    cursor.close()
'''
'''
siq = """INSERT INTO schedule(time_id, date, begin, free, master_id)
                                 VALUES
                                (1, '2023-12-28', '15:30', 1 , 1);"""
    count = cursor.execute(siq)
    siq = """INSERT INTO schedule(time_id, date, begin, free, master_id)
                                     VALUES
                                    (2, '2023-12-28', '16:00', 1 , 1);"""
    count = cursor.execute(siq)
    siq = """INSERT INTO schedule(time_id, date, begin, free, master_id)
                                     VALUES
                                    (3, '2023-12-28', '17:45', 1 , 1);"""
    count = cursor.execute(siq)
    siq = """INSERT INTO schedule(time_id, date, begin, free, master_id)
                                         VALUES
                                        (4, '2023-12-29', '11:00', 1 , 2);"""
    count = cursor.execute(siq)
    siq = """INSERT INTO schedule(time_id, date, begin, free, master_id)
                                             VALUES
                                            (5, '2023-12-29', '12:00', 1 , 1);"""
    count = cursor.execute(siq)
    siq = """INSERT INTO schedule(time_id, date, begin, free, master_id)
                                         VALUES
                                        (6, '2023-12-29', '13:00', 1 , 1);"""
    count = cursor.execute(siq)
    siq = """INSERT INTO schedule(time_id, date, begin, free, master_id)
                                         VALUES
                                        (7, '2023-12-29', '15:00', 1 , 1);"""
    count = cursor.execute(siq)

    siq = """INSERT INTO schedule(time_id, date, begin, free, master_id)
                                             VALUES
                                            (8, '2023-12-29', '18:30', 1 , 2);"""
    count = cursor.execute(siq)
    siq = """INSERT INTO schedule(time_id, date, begin, free, master_id)
                                             VALUES
                                            (9, '2023-12-29', '20:00', 1 , 2);"""
    count = cursor.execute(siq)
    
    
    
    
    sqlite_select_query = """INSERT INTO services(service_id, name, categoty, price, length)
                                      VALUES
                                      (4, 'Эстет', 'Педикюр', 1500, 50);"""
    cursor.execute(sqlite_select_query)
    sqlite_select_query = """INSERT INTO services(service_id, name, categoty, price, length)
                                          VALUES
                                          (5, '1 клетка', 'Наращивание', 3000, 60);"""
    cursor.execute(sqlite_select_query)
    sqlite_select_query = """INSERT INTO services(service_id, name, categoty, price, length)
                                          VALUES
                                          (6, 'Френч', 'Маникюр', 1900, 35);"""
    cursor.execute(sqlite_select_query)
    sqlite_select_query = """INSERT INTO services(service_id, name, categoty, price, length)
                                          VALUES
                                          (7, 'Реставрация', 'Педикюр', 500, 90);"""
    cursor.execute(sqlite_select_query)
    sqlite_select_query = """INSERT INTO services(service_id, name, categoty, price, length)
                                          VALUES
                                          (8, '2 клетки', 'Наращивание', 3500, 70);"""
    cursor.execute(sqlite_select_query)
    sqlite_select_query = """INSERT INTO services(service_id, name, categoty, price, length)
                                          VALUES
                                          (9, 'Арт', 'Маникюр', 2500, 30);"""
    cursor.execute(sqlite_select_query)
'''
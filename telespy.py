from config import api_id, api_hash
from pyrogram import Client, errors
from pyrogram.types.input_media import InputPhoneContact
import sys
import asyncio
import time
from datetime import datetime, timedelta
import os 
import csv
import pandas as pd
from random import choice
from string import ascii_letters

#генерация случайного имени для текущей сессии
name_session = ''.join(choice(ascii_letters) for i in range(5)) + '_' + datetime.now().strftime('%H-%M')

app = Client(
    name_session,
    api_id=api_id,
    api_hash=api_hash
)

"""
Функция получает имя пользователя по номеру телефона
return: имя пользователя telegram или None
"""
async def get_user_name(phone_number):
    try:
        add_phone = await app.add_contacts(
                            [
                                InputPhoneContact(phone_number, "Foo")
                            ]
                        )
        contacts = await app.get_contacts()
        if contacts:
            username = contacts[0].username
            await app.delete_contacts([username])
            print('Получен ник {} от телефона {}'.format(username, phone_number))
            return username
        else:
            return None
    except AttributeError:
        return None

"""
Функция получает онлайн статус пользователя telegram
return: последний статус:
    - “online”, пользователь в сети прямо сейчас. 
    - "offline”, пользователь в оффлайне. 
    - "recently”, пользователь со скрытым статусом, который был онлайн между 1 секундой и 2-3 днями назад. 
    - “within_week”, пользователь со скрытым статусом, который был онлайн между 2-3 и 7 днями назад. 
    - “within_month”, пользователь со скрытым статусом, который был онлайн между 6-7 и месяцем назад. 
    - "long_time_ago”, заблокированный пользователь или пользователь со скрытым статусом, который был онлайн более месяца назад.
"""
async def get_status_user(username):
    status = await app.get_users(username)
    status = status['status']
    return status

"""
Функция формирует csv файлы с метками времени пользователей
Например:
timestamp,online
1605393931.625457,False
1605393936.767714,False
1605393941.859685,True
"""
async def write_csv_timestamp(dict_data, username, keys, path):
    filename = path + '\\' + '{}_time_status.csv'.format(username)
    check_file = os.path.exists(filename)
    if check_file:
        with open(filename, 'a', encoding='utf-8', newline='') as csv_file:
            writer = csv.DictWriter(csv_file, keys, delimiter=',')
            flag_csv_empty = os.stat(filename).st_size == 0
            if flag_csv_empty:
                writer.writeheader()
            if dict_data['timestamp'] != None:
                writer.writerows([dict_data])
    else:
        with open(filename, 'w', encoding='utf-8', newline='') as csv_file:
            writer = csv.DictWriter(csv_file, keys, delimiter=',')
            flag_csv_empty = os.stat(filename).st_size == 0
            if flag_csv_empty:
                writer.writeheader()
            if dict_data['timestamp'] != None:
                writer.writerows([dict_data])

"""
Функция формирует csv файлы с промежутками онлайн статуса пользователей и временем нахождения в сети
Например:
entry,exit,session_duration
14-11-2020 22:45:41,14-11-2020 22:45:46,5.0
14-11-2020 22:46:17,14-11-2020 22:46:37,20.0
14-11-2020 22:52:48,14-11-2020 22:53:03,15.0
"""
async def write_csv_online_status(dict_data, username, keys, path):
    filename = path + '\\' + '{}_online.csv'.format(username)
    check_file = os.path.exists(filename)
    if check_file:
        with open(filename, 'a', encoding='utf-8', newline='') as csv_file:
            writer = csv.DictWriter(csv_file, keys, delimiter=',')
            flag_csv_empty = os.stat(filename).st_size == 0
            if flag_csv_empty:
                writer.writeheader()
            if dict_data['entry'] != None:
                writer.writerows([dict_data])
    else:
        with open(filename, 'w', encoding='utf-8', newline='') as csv_file:
            writer = csv.DictWriter(csv_file, keys, delimiter=',')
            flag_csv_empty = os.stat(filename).st_size == 0
            if flag_csv_empty:
                writer.writeheader()
            if dict_data['entry'] != None:
                writer.writerows([dict_data])

"""
Функция формирует csv файлы с одновременным нахождением в онлайне
Например:
.......
"""
async def write_csv_intersect(dict_data, keys, path, username1, username2):
    filename = path + '\\' + 'intersect_{}_+_{}.csv'.format(username1, username2)
    check_file = os.path.exists(filename)
    try:
        df = pd.read_csv(filename, sep=',')
        if not any(df.intersec_start == dict_data['intersec_start']):
            #print(any(df1.entry == dict_status['entry']))
            with open(filename, 'a', encoding='utf-8', newline='') as csv_file:
                writer = csv.DictWriter(csv_file, keys, delimiter=',')
                writer.writerows([dict_data])
                print("Появилось новое пересечение онлайна!")
                print(dict_data)
        del df
    except FileNotFoundError:
        with open(filename, 'a', encoding='utf-8', newline='') as csv_file:
            writer = csv.DictWriter(csv_file, keys, delimiter=',')
            flag_csv_empty = os.stat(filename).st_size == 0
            if flag_csv_empty:
                writer.writeheader()
            if dict_data['intersec_start'] != None:
                writer.writerows([dict_data])

"""
Функция преобразовывает csv файлы с метками времени пользователей в csv файлы с промежутками онлайн статуса пользователей и временем нахождения в сети
"""
async def parse_csv_time_status(username, path):
    dict_status = {
            'entry' : None,
            'exit' : None,
            'session_duration' : None
        }
    while True:
        filename = path + '\\' + '{}_time_status.csv'.format(username)
        check_file = os.path.exists(filename)
        keys = ['entry', 'exit', 'session_duration']
        if check_file:
            df = pd.read_csv(filename, sep=',')
            df.columns = ['timestamp', 'online']
            count_true = False
            for index in range(len(df.index)):
                if (df.loc[index, 'online'] == True) and count_true == False:
                    count_true = True
                    dict_status['entry'] = datetime.fromtimestamp(df.loc[index, "timestamp"]).strftime('%d-%m-%Y %H:%M:%S')
                if count_true and (df.loc[index, 'online'] == False):
                    count_true = False
                    dict_status['exit'] = datetime.fromtimestamp(df.loc[index, "timestamp"]).strftime('%d-%m-%Y %H:%M:%S')
                    session_duration = time.mktime(datetime.strptime(dict_status['exit'], '%d-%m-%Y %H:%M:%S').timetuple()) - time.mktime(datetime.strptime(dict_status['entry'], '%d-%m-%Y %H:%M:%S').timetuple())
                if dict_status['entry'] and dict_status['exit']:
                    dict_status['session_duration'] = session_duration
                    # print(username)
                    # print(dict_status)
                    try:
                        df1 = pd.read_csv(path + '\\' + '{}_online.csv'.format(username), sep=',')
                        if not any(df1.entry == dict_status['entry']):
                            print("{} был в сети {} сек. с {} по {}".format(username, dict_status['session_duration'],dict_status['entry'], dict_status['exit']))
                            await write_csv_online_status(dict_status, username, keys, path)
                        del df1
                    except FileNotFoundError:
                        await write_csv_online_status(dict_status, username, keys, path)
                    dict_status = {
                        'entry' : None,
                        'exit' : None,
                        'session_duration' : None
                    }
            del df
        else:
            await write_csv_online_status(dict_status, username, keys, path)
        await asyncio.sleep(6)


"""
Функция находит пересечения дат онлайн статусов пользователей в csv файлах с промежутками онлайн статуса и временем нахождения в сети
"""
async def parce_csv_intersection(username1, username2, path):
    while True:
        df1 = pd.read_csv(path + '\\' + '{}_online.csv'.format(username1), sep=',')
        df2 = pd.read_csv(path + '\\' + '{}_online.csv'.format(username2), sep=',')
        if len(df1.index) > len(df2.index):
            await find_intesection(df1, df2, path, username1, username2)          
        else:
            await find_intesection(df2, df1, path, username1, username2)
        del df1
        del df2
        await asyncio.sleep(10)

"""
Функция находит пересечения дат
return дата начала пересечения, дата конца пересечения
"""
async def has_overlap(A_start, A_end, B_start, B_end):
    latest_start = max(A_start, B_start)
    earliest_end = min(A_end, B_end)
    if latest_start <= earliest_end:
        return latest_start, earliest_end

"""
Функция создаёт словарь с датами, которые пересекаются и общим временем пересечения
return словарь, например:
{'intersec_start': '14-11-2020 22:46:17', 'intersec_end': '14-11-2020 22:46:37', 'session_duration': 20.0}
"""
async def make_dict_overlap(overlaps_date_start, overlaps_date_end):
    session_duration = time.mktime(datetime.strptime(overlaps_date_end, '%d-%m-%Y %H:%M:%S').timetuple()) - time.mktime(datetime.strptime(overlaps_date_start, '%d-%m-%Y %H:%M:%S').timetuple())
    if session_duration > 0:
        dict_overlap = {
            'intersec_start' : overlaps_date_start,
            'intersec_end' : overlaps_date_end,
            'session_duration' : session_duration
        }
        return dict_overlap
    else:
        return None

"""
Функция ищет пересечения по датам в двух датафреймах
return словарь, например:
{'intersec_start': '14-11-2020 22:46:17', 'intersec_end': '14-11-2020 22:46:37', 'session_duration': 20.0}
"""
async def find_intesection(df1, df2, path, username1, username2):
    for index_df1 in range(len(df1.index)):
        date_entry_1 = df1.loc[index_df1, 'entry']
        date_exit_1 = df1.loc[index_df1, 'exit']
        for index_df2 in range(len(df2.index)):
            date_entry_2 = df2.loc[index_df2, 'entry']
            date_exit_2 = df2.loc[index_df2, 'exit']
            overlaps_date = await has_overlap(date_entry_1, date_exit_1, date_entry_2, date_exit_2)
            if overlaps_date:
                dict_overlap = await make_dict_overlap(overlaps_date[0], overlaps_date[1])
                if dict_overlap:
                    keys = ['intersec_start', 'intersec_end', 'session_duration']
                    await write_csv_intersect(dict_overlap, keys, path, username1, username2)

"""
Функция вычисляет вероятность знакомства 2х пользователей
"""
async def chance_contact(path, username1, username2):
    while True:
        filename = path + '\\' + 'intersect_{}_+_{}.csv'.format(username1, username2)
        check_file = os.path.exists(filename)
        if check_file:
            df = pd.read_csv(filename, sep=',')
            #выборка за последние 24 часа
            hours_24 = timedelta(hours=24)
            last_24_hours = datetime.strptime(df['intersec_end'].iloc[-1], '%d-%m-%Y %H:%M:%S') - hours_24
            df['intersec_start'] = pd.to_datetime(df['intersec_start'], format='%d-%m-%Y %H:%M:%S')
            mask = (df['intersec_start'] >= last_24_hours)
            df = df.loc[mask]
            general_session_duration = df['session_duration'].sum() / 60
            count_intersect = df.shape[0]
            print('Общее время совместного онлайна за последние сутки: {:4.2f} м. Количество совместных пересечений в онлайне за последние сутки: {}'.format(general_session_duration, count_intersect))
            chance_dating = (general_session_duration * 0.6 + count_intersect * 0.4)
            if chance_dating > 100:
                chance_dating /= 10
            print('Вероятность знакомства пользователей {} и {} равна {:4.2f}%'.format(username1, username2, chance_dating))
            if chance_dating > 40:
                str_chance_dating = 'Вероятнее всего пользователи {} и {} знакомы друг с другом!'.format(username1, username2)
            else:
                str_chance_dating = 'Вероятнее всего пользователи {} и {} не знакомы друг с другом!'.format(username1, username2)
            print(str_chance_dating)
        else:
            pass
        await asyncio.sleep(20)

"""
Функция для постоянного мониторинга онлайн статуса пользователей telegram
"""
async def status_user_monitor(username, path):
    keys = ['timestamp', 'online']
    dict_timestamp_status = {
        'timestamp' : None,
        'online' : None
    }
    while True:
        now_time = datetime.now()
        status = await get_status_user(username)
        print('{} {} - {}'.format(now_time.strftime("%d-%m-%Y %H:%M:%S"), username, status))
        if status == 'online':
            dict_timestamp_status['timestamp'] = now_time.timestamp()
            dict_timestamp_status['online'] = True
            await write_csv_timestamp(dict_timestamp_status, username, keys, path)
        elif status == 'offline':
            dict_timestamp_status['timestamp'] = now_time.timestamp()
            dict_timestamp_status['online'] = False
            await write_csv_timestamp(dict_timestamp_status, username, keys, path)
        await asyncio.sleep(5)

"""
Функция конвертирует date python в timestamp javascript, так как JS использует миллисекунды, а python секунды
"""
def convert_tsPY_to_tsJS(date_python):
    timestamp_python = time.mktime(datetime.strptime(date_python, '%d-%m-%Y %H:%M:%S').timetuple())
    timestamp_js = int(timestamp_python) * 1000
    return timestamp_js

"""
Функция подготавливает данные для построения графиков в HighCharts
return словарь, например:
{'start': '1606603171000', 'intersec_end': '1606603176000', 'name': "Оффлайн", 'color' : '#ee5555'}
"""
def data_for_build_graph(csv_name):
    summary = None
    str_chance_dating = None
    path_file = csv_name
    if 'intersect' in path_file:
        column_entry = 'intersec_start'
        column_exit = 'intersec_end'

        username1 = path_file.split('_+_')[0][path_file.split('_+_')[0].rfind('\\') + 1:]
        username2 = path_file.split('_+_')[1][:path_file.split('_+_')[1].rfind('\\')]
        #подсчёт вероятность знакомства
        df = pd.read_csv(path_file, sep=',')
        #выборка за последние 24 часа
        hours_24 = timedelta(hours=24)
        last_24_hours = datetime.strptime(df['intersec_end'].iloc[-1], '%d-%m-%Y %H:%M:%S') - hours_24
        df['intersec_start'] = pd.to_datetime(df['intersec_start'], format='%d-%m-%Y %H:%M:%S')
        mask = (df['intersec_start'] >= last_24_hours)
        df = df.loc[mask]
        general_session_duration = df['session_duration'].sum() / 60
        count_intersect = df.shape[0]
        summary = 'Общее время совместного онлайна за последние сутки: {:4.2f} м. \n Количество совместных пересечений в онлайне за последние сутки: {}'.format(general_session_duration, count_intersect)
        chance_dating = (general_session_duration * 0.6 + count_intersect * 0.4)
        if chance_dating > 100:
            chance_dating /= 10
        if chance_dating > 40:
            str_chance_dating = 'Вероятность знакомства пользователей {} и {} равна {:4.2f}% \n Вероятнее всего пользователи знакомы друг с другом!'.format(username1, username2, chance_dating)
        else:
            str_chance_dating = 'Вероятность знакомства пользователей {} и {} равна {:4.2f}% \n Вероятнее всего пользователи не знакомы друг с другом!'.format(username1, username2, chance_dating)
        #print(summary)
        #print(str_chance_dating)
    else:
        column_entry = 'entry'
        column_exit = 'exit'
    df = pd.read_csv(path_file, sep=',')
    data_time_js = []
    for index_df in range(len(df.index)):
        date_entry = df.loc[index_df, column_entry]
        date_exit = df.loc[index_df, column_exit]
        session_duration = df.loc[index_df, 'session_duration']
        timestamp_js_start_online = convert_tsPY_to_tsJS(date_entry)
        timestamp_js_end_online = convert_tsPY_to_tsJS(date_exit)
        if index_df == 0:
            timestamp_js_start_offline = int(((timestamp_js_start_online / 1000) - 5) * 1000)
            timestamp_js_end_offline = int(((timestamp_js_start_online / 1000) - 5) * 1000)
        else:
            timestamp_js_start_offline = int(((convert_tsPY_to_tsJS(df.loc[index_df - 1, column_exit]) / 1000) + 1) * 1000)
            timestamp_js_end_offline = int(((convert_tsPY_to_tsJS(df.loc[index_df, column_entry]) / 1000) - 1) * 1000)
        dict_start_end_timestamp_js_online = {
            'start' : timestamp_js_start_online,
            'end' : timestamp_js_end_online,
            'name' : 'Онлайн',
            'color' : '#88ee55'
        }
        dict_start_end_timestamp_js_offline = {
            'start' : timestamp_js_start_offline,
            'end' : timestamp_js_end_offline,
            'name' : 'Оффлайн',
            'color' : '#ee5555'
        }
        data_time_js.append(dict_start_end_timestamp_js_online)
        data_time_js.append(dict_start_end_timestamp_js_offline)

    #добавляем оффлайн после конца файла 
    timestamp_js_end_online = convert_tsPY_to_tsJS(df.tail(1)[column_exit].values[0])
    timestamp_js_start_offline = int(((timestamp_js_end_online / 1000) + 1) * 1000)
    timestamp_js_end_offline = int(((timestamp_js_end_online / 1000) + 5) * 1000) # TODO: для онлайн мониторинга и для загрузки - время наверное должно быть разное
    dict_start_end_timestamp_js_offline = {
            'start' : timestamp_js_start_offline,
            'end' : timestamp_js_end_offline,
            'name' : 'Оффлайн',
            'color' : '#ee5555'
        }
    data_time_js.append(dict_start_end_timestamp_js_offline)
    return data_time_js, summary, str_chance_dating

def menu():
    print("--------------Мониторинг активности 2х пользователей в Telegram--------------")
    while True:
        print("Что вы знаете о людях?")
        print("1. Номера телефонов")
        print("2. Ники в Telegram")
        print("3. Выход")
        input_check = input("Выберите пункт: ")
        if input_check == '1' or input_check == '2' or input_check == '3':
            return(input_check)
        else:
            print("Введите корректный пункт меню!")

async def check_phone_number():
    while True:
        phone_number_user = input('Введите номер телефона пользователя без +:\n')
        try:
            phone_number_user = int(phone_number_user)
            username = await get_user_name(str(phone_number_user))
            if username == None:
                print("Номера телефона ещё нет в telegram или пользователь сменил настройки конфиденциальности! Введите другой номер телефона!")
            else:
                return(username)
        except ValueError:
            print("Введите корректный номер телефона!")

async def check_first_user_status(loop, username):
    status = await get_status_user(username)
    if status == 'online' or status == 'offline':
        print('Онлайн статус пользователя {} получен успешно!'.format(username))
        return True
    else:
        print('Онлайн статус получить не удалось! Пользователь ограничил настройки конфиденциальности.')
        print('Выход из программы...')
        loop.stop()

async def check_tg_username():
    while True:
        name_user = input('Введите имя пользователя в telegram:\n')
        try:
            user = await app.get_users(name_user)
            print('Пользователь {} есть в Telegram!'.format(name_user))
            return(name_user)
        except errors.UsernameNotOccupied:
            print('Пользователя {} нет в Telegram! Введите другой никнейм!'.format(name_user))
        except errors.UsernameInvalid:
            print('Введено некоорректное имя пользователя!')
        except:
            print('Непредвиденная ошибка, попробуйте ввести другое имя пользователя.')

async def get_info_users(loop, name_func):
    print('-----------------------------')
    print('Информация о 1м пользователе:')
    username1 = await name_func()
    print('Попытка получить онлайн статус пользователя {}...'.format(username1))
    user_status1 = await check_first_user_status(loop, username1)
    if user_status1:
        print('-----------------------------')
        print('Информация о 2м пользователе:')
        username2 = await name_func()
        print('Попытка получить онлайн статус пользователя {}...'.format(username2))
        user_status2 = await check_first_user_status(loop, username2)
        print('-----------------------------')
        return username1, username2, user_status1, user_status2
    else:
        return None, None, None, None

def start_monitoring(loop, username1, username2):
    print('Мониторим... (для завершения программы нажмите сочетания клавиш ctrl + C)')
    path = os.getcwd() + '\\' + '{}_+_{}'.format(username1, username2)
    if not os.path.isdir(path):
        os.mkdir(path)
        print("Создана директория с результатами мониторинга - " + path)          
    #Cоздание задач для параллельного мониторинга и сбора информации
    loop.create_task(status_user_monitor(username1, path))
    loop.create_task(status_user_monitor(username2, path))
    loop.create_task(parse_csv_time_status(username1, path))
    loop.create_task(parse_csv_time_status(username2, path))
    loop.create_task(parce_csv_intersection(username1, username2, path))
    loop.create_task(chance_contact(path, username1, username2))

async def main(loop):
    await app.start()
    item_menu = int(menu())
    if item_menu == 1:
        username1, username2, user_status1, user_status2 = await get_info_users(loop, check_phone_number)
        if user_status1 and user_status2:
            start_monitoring(loop, username1, username2)
        #phone_number1 = "79126916010"
        #phone_number2 = "79827919063"
    elif item_menu == 2:
        username1, username2, user_status1, user_status2 = await get_info_users(loop, check_tg_username)
        if user_status1 and user_status2:
            start_monitoring(loop, username1, username2)
    elif item_menu == 3:
        print('Выход из программы...')
        loop.stop()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(main(loop))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        print('Завершение программы...')
        loop.stop()

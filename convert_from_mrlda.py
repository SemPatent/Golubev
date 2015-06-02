#!/bin/env python
import postgresql.driver as pg_driver
from sys import argv

# функция загрузки данных из файла
def loadText(filepath):
    f = open(filepath, 'r')
    text = f.readlines()
    f.close()
    return text

# функция извлечения данных из alpha файла
def importAlphaParam(filepath):
    # создаём пустой словарь
    d = {}
    # загружаем текст файла
    data = loadText('./' + filepath)
    # цикл по всем строкам загруженного файла
    for line in data:
        # разделяем строку на токены
        name = line.split()
        # если количество токенов не равно 2, то
        if len(name) != 2:
            # переходим к следующей строке
            continue
        # если первый токен Key
        if name[0] == 'Key:':
            # запоминаем его значение
            key = int(name[1])
            # print('> loaded record {} '.format(key), end='')
        # если Value
        elif name[0] == 'Value:':
            # записываем данные в словарь
            d[key] = float(name[1])
            # print('with value {}'.format(name[1]))
    # возвращаем загруженный словарь
    return d

# функция извлечения данных из beta файла
def importBetaParam(filepath):
    # создаём пустой словарь
    d = {}
    # загружаем текст файла
    data = loadText('./' + filepath)
    # цикл по всем строкам загруженного файла
    for line in data:
        # разделяем строку на токены
        name = line.split()
        # если количество токенов меньше 3, то
        if len(name) < 3:
            # переходим к следующей строке
            continue
        # если первый токен Key
        if name[0] == 'Key:':
            # запоминаем наши значения
            key = name[1] + name[2]
            # print('> loaded record {} '.format(key), end='')
        # если Value
        elif name[0] == 'Value:':
            # создаём пустой список
            d[key] = []
            # цикл по всем токенам после 1-го
            for i in range(1, len(name)):
                # разделяем строку по '='
                keys = name[i].split('=')
                # old code
                # if keys[0][0] == '{':
                #     a = int(keys[0][1:])
                # else:
                #     a = int(keys[0])
                # извлекаем данные
                b = float(keys[1][:-1])
                # d[key].append({a: b})
                # добавляем в список
                d[key].append(b)
            # print('with values {}'.format(d[key]))
    # возвращаем загруженный словарь
    return d

# упрощенная версия для работы с БД
class DBSender:
    db = None       # структура для обращения к БД
    user = ''       # пользователь
    password = ''   # пароль
    host = ''       # хост
    port = 0        # порт
    database = ''   # имя БД
    # функция инициализации
    def __init__(self, user='test', password='test', host='127.0.0.1', port=5432, db='testdb'):
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.database = db
    # функция подключения к БД
    def connect(self):
        self.db = pg_driver.connect(user=self.user, password=self.password,
            host=self.host, port=self.port, database=self.database)
    # функция добавления информации по патентам
    def insertPatents(self, alpha, beta):
        emp = self.db.prepare("INSERT INTO should_accept_log VALUES ($1, $2, $3, $4, $5, $6, $7)")
        for count, item in enumerate(beta):
            id, key = item[1:-1].split(',')
            emp.load_rows([(count, int(id), int(id), 1, alpha[int(id)], float(key), beta[item])])
    # функция закрытия БД
    def close(self):
        self.db.close()

# точка входа в программу
if __name__ == '__main__':
    # проверяем кол-во введённых аргументов
    if len(argv) < 3:
        print('usage: {} <alpha-file> <beta-file>'.format(argv[0]))
    else:
        # создаём класс для работы с БД
        db = DBSender('test', 'test', '127.0.0.1', 5432, 'testdb')
        # подключаемся к БД
        db.connect()
        try:
            # извлекаем данные из alpha файла
            alpha = importAlphaParam(argv[1])
            # и бета файла
            beta = importBetaParam(argv[2])
        finally:
            # добавляем данные в БД
            db.insertPatents(alpha, beta)
        # закрываем БД
        db.close()

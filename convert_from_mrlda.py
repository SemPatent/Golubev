#!/bin/env python
import postgresql.driver as pg_driver
from sys import argv

def load_text(filepath):
    f = open(filepath, 'r')
    text = f.readlines()
    f.close()
    return text

def import_alpha_param(filepath):
    d = {}
    data = load_text('./' + filepath)
    for line in data:
        name = line.split()
        if len(name) != 2:
            continue
        if name[0] == 'Key:':
            key = int(name[1])
            # print('> loaded record {} '.format(key), end='')
        elif name[0] == 'Value:':
            d[key] = float(name[1])
            # print('with value {}'.format(name[1]))
    return d

def import_beta_param(filepath):
    d = {}
    data = load_text('./' + filepath)
    for line in data:
        name = line.split()
        if len(name) < 3:
            continue
        if name[0] == 'Key:':
            key = name[1] + name[2]
            # print('> loaded record {} '.format(key), end='')
        elif name[0] == 'Value:':
            d[key] = []
            for i in range(1, len(name)):
                keys = name[i].split('=')
                if keys[0][0] == '{':
                    a = int(keys[0][1:])
                else:
                    a = int(keys[0])
                b = float(keys[1][:-1])
                # d[key].append({a: b})
                d[key].append(b)
            # print('with values {}'.format(d[key]))
    return d

class DBSender:
    db = None
    def connect(self):
        self.db = pg_driver.connect(user='test', password='test',
            host='127.0.0.1', database='testdb', port=5432)
    def insertPatents(self, alpha, beta):
        emp = self.db.prepare("INSERT INTO should_accept_log VALUES ($1, $2, $3, $4, $5, $6, $7)")
        count = 1
        for x in beta:
            id, key = x[1:-1].split(',')
            emp.load_rows([(count, int(id), int(id), 1, alpha[int(id)], float(key), beta[x])])
            count += 1
    def close(self):
        self.db.close()

if __name__ == '__main__':
    if len(argv) < 3:
        print('usage: {} <alpha-file> <beta-file>'.format(argv[0]))
    else:
        db = DBSender()
        db.connect()
        try:
            alpha = import_alpha_param(argv[1])
            beta = import_beta_param(argv[2])
        finally:
            db.insertPatents(alpha, beta)
        db.close()

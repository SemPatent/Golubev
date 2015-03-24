#!/bin/env python
from xml.etree.ElementTree import ElementTree
import postgresql.driver as pg_driver
from datetime import datetime
from os import listdir
from sys import argv
from re import sub

regex_str = '[^a-zA-Zа-яА-Я ]'

def sub_list(obj):
    text = ''
    for x in obj:
        if x.text != None:
            text += x.text
        if x.tag != None:
            text += sub_list(x)
    return text

class PatentParser:
    lang = ''
    title = ''
    title_en = ''
    classification = ''
    country = ''
    doc_number = ''
    kind = ''
    app_date = ''
    date = ''
    date_publ = ''
    applicant = []
    abstract = ''
    description = ''
    claims = ''
    reference = []
    dom = None
    def loadFile(self, filename):
        self.dom = ElementTree()
        self.dom.parse(filename)
        tag = self.dom.find('.').attrib['lang']
        if tag == 'RU':
            self.getRusInfo()
        elif tag == 'EN':
            self.getEngInfo()
        return tag
    def getRusInfo(self):
        a = self.dom.find('.').attrib
        self.doc_number = a['number']
        self.app_date = a['applicationDate']
        self.date = self.date_publ = a['date']
        self.country = a['country']
        self.lang = a['lang']
        self.kind = a['kind']
        self.title = self.dom.find('Title').text.capitalize()
        self.title_en = self.dom.find('TitleEng').text.capitalize()
        a = self.dom.find('classificationipcmain').attrib
        self.classification =  '{}{}{}{}{}'.format(a['section'], a['class'], a['subclass'],
            a['main-group'], a['subgroup']).upper()
        for root in self.dom.findall('Authors'):
            for child in root:
                self.applicant.append(child.attrib['Name'])
        self.description = self.dom.find('Description').text
        self.abstract = self.dom.find('Abstract').text
        for root in self.dom.findall('Claims'):
            for child in root:
                self.claims += child.text
        for root in self.dom.findall('RelatesPatents'):
            for child in root:
                self.reference.append(child.attrib['number'])
        for root in self.dom.findall('RelatesForeignPatents'):
            for child in root:
                self.reference.append(child.attrib['number'])
    def getEngInfo(self):
        temp = self.dom.find('.').attrib
        for key in temp:
            if key == 'lang':
                self.lang = temp[key]
            elif key == 'country':
                self.country = temp[key]
            elif key == 'date-publ':
                self.date_publ = temp[key]
        self.title = self.title_en = self.dom.find('*/invention-title').text
        self.classification = self.dom.find('*/classification-ipc/main-classification').text
        for child in list(self.dom.find('*/publication-reference/document-id')):
            tag = child.tag
            if tag == 'doc-number':
                self.doc_number = child.text
            elif tag == 'date':
                self.date = child.text
            elif tag == 'kind':
                self.kind = child.text
        self.abstract = sub_list(self.dom.findall('abstract'))
        self.description = sub_list(self.dom.findall('description'))
        self.claims = sub_list(self.dom.findall('claims'))
        for root in list(self.dom.findall('*/parties/applicants/applicant')):
            for child in root:
                if child.tag == 'addressbook':
                    names = ''
                    for x in child:
                        if x.tag == 'last-name' or x.tag == 'first-name':
                            names += ' ' + x.text
                    self.applicant.append(names[1:])
        for ref in self.dom.findall('*/references-cited/citation/patcit/document-id/doc-number'):
            self.reference.append(ref.text)
    def __str__(self):
        text = 'lang = {}\ntitle = {}\nclass = {}\ncountry = {}\ndoc = {}\n'.format(self.lang,
            self.title, self.classification, self.country, self.doc_number)
        text += 'kind = {}\ndate = {}\npubl = {}\n'.format(self.kind, self.date, self.date_publ)
        text += 'abstract = {}..\n'.format(self.abstract[:32])
        text += 'description = {}..\n'.format(self.description[:32])
        text += 'claims = {}..\n'.format(self.claims[:32])
        text += 'applicant = '
        for p in self.applicant:
            text += p + ', '
        text += '\nreference = '
        for p in self.reference:
            text += '\'' + p + '\', '
        return text

class DBSender:
    db = None
    def connect(self):
        self.db = pg_driver.connect(user='test', password='test',
            host='127.0.0.1', database='testdb', port=5432)
    def createTables(self, filename):
        table_format = ''
        f = open(filename, 'r')
        for s in f.readlines():
            table_format += s
        f.close()
        self.db.execute(table_format)
    def insertPatent(self, id, patent):
        emp = self.db.prepare(
            "INSERT INTO documents VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)")
        emp.load_rows([
            (id, patent.lang, patent.doc_number, datetime.strptime(patent.date, '%Y%m%d'),
                patent.lang, patent.title, patent.classification[:3], patent.classification,
                patent.title_en, patent.kind, patent.applicant)
        ])
        emp = self.db.prepare("INSERT INTO query_requests VALUES ($1, $2, $3, $4, $5, $6, $7, $8)")
        emp.load_rows([
            (id, patent.abstract, patent.description, patent.claims, patent.classification,
                patent.lang, datetime.strptime(patent.date, '%Y%m%d'), patent.reference)
        ])
    def close(self):
        self.db.close()

def scanDirectory(path, outfile):
    db = DBSender()
    db.connect()
    patent = PatentParser()
    db.createTables('./table.sql')
    directory = listdir(path)
    output = open('./' + outfile, 'w')
    for filename in directory:
        print('{:010} READ FILE: {}'.format(count, filename))
        patent.loadFile(path + '/' + filename)
        db.insertPatent(count, patent)
        text = '{} {} {}'.format(patent.abstract, patent.description, patent.claims)
        text = sub(regex_str, '', text.lower())
        text = sub('( +)', ' ', text)
        output.write('{}\t{}\n'.format(filename, text))
    output.close()
    db.close()

if __name__ == '__main__':
    if len(argv) < 3:
        print('usage: {} <directory-with-patent-files> <mrlda-input-file>'.format(argv[0]))
    else:
        scanDirectory(argv[1], argv[2])

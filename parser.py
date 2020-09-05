# -*- coding: utf-8 -*-

from docx import Document
import json
from cellparser import find_parity, find_teacher, find_type, find_exercise, find_room, find_remotely
import re
import glob

for file_name in list(glob.glob(r'docx\*.docx')):
    # Open the .docx file
    document = Document(file_name)
    schedule = {}
    print(file_name)
    k = i = 0

    for ta, table in enumerate(document.tables):
        print(ta)
        data_t2 = []
        data_t = []
        data = []

        keys = None
        # print(len(table.rows), len(table.columns))
        for i, row in enumerate(table.rows):
            text = (cell.text.strip() for cell in row.cells)
            text2 = list(text)
            data.append(text2)
            # Establish the mapping based on the first row
            # headers; these will become the keys of our dictionary
            '''if i == 0:
                keys = tuple(text)
                continue

            # Construct a dictionary for this row, mapping
            # keys to values for this row
            row_data = dict(zip(keys, text))
            data.append(row_data)'''

        while len(data[-1]) != len(data[-2]):
            data[-1].append(data[-1][-1])
        data_t = list(map(list, zip(*data)))
        data_t2 = data_t.copy()
        rasp = {}
        groups = []
        k = 2
        if not groups:
            data_t2 = data_t.copy()
            for i, el in enumerate(data[1][2:]):
                el = re.sub('[\n\r\t]', '', el)
                group = re.search('\s*([0-9]+[а-я]?(?:[(][а-я0-9]+[)])?)\s*', el, re.I)
                if not group or group.group(0).strip() in groups:
                    data_t2.remove(data_t[i + 2])
                else:
                    groups.append(group.group(0).strip().lower())
        # print(data)

        print(groups)
        # print(groups, file=logfile)

        data = list(zip(*data_t2))

        num = 0
        day = 0
        pr = True

        for group in groups:
            schedule[group] = {'1': {'1': [], '2': [], '3': [], '4': [], '5': []},
                               '2': {'1': [], '2': [], '3': [], '4': [], '5': []},
                               '3': {'1': [], '2': [], '3': [], '4': [], '5': []},
                               '4': {'1': [], '2': [], '3': [], '4': [], '5': []},
                               '5': {'1': [], '2': [], '3': [], '4': [], '5': []},
                               '6': {'1': [], '2': [], '3': [], '4': [], '5': []},
                               '7': {'1': [], '2': [], '3': [], '4': [], '5': []}}
        last = '9301110'
        while k < len(data):
            time = data[k][1]
            time = re.sub("\D", '', time).lstrip('0')
            if time != last:
                num += 1
            if num > 3:
                num = 0
                day += 1
            last = time

            for i, group in enumerate(groups):

                cell = data[k][2 + i]
                exercise = room = parity = None
                teachers = []
                types = []
                cell1 = None
                while cell1 != cell:
                    cell1 = cell
                    for spaces in range(4, 0, -1):
                        shift = 0
                        for m in re.finditer('(?:([а-я])[\s]{%d}){3,}' % spaces, cell, re.I):
                            new_str = re.sub(r'\s', '', m.group())
                            cell = cell[:m.start() - shift] + new_str + cell[m.end() - shift:]
                            shift = m.end() - m.start() - len(new_str)
                cell = re.sub(r'[\n\r\t]|13-30-16-45', ' ', cell)
                cell = re.sub(r'[.]+', '.', cell)
                cell = re.sub(r'\s+', ' ', cell).strip()
                cells = cell

                if len(cell) > 0:
                    #print(cell)
                    remotely, cell = find_remotely(cell)
                    parity, cell = find_parity(cell)
                    #print("четность", parity)
                    types, cell = find_type(cell)
                    #print("тип", types)
                    exercise, cell = find_exercise(cell)
                    teachers, cell = find_teacher(cell)
                    #print("учитель", teachers)
                    #print("предмет", exercise)
                    if remotely:
                        room="Дистанционно"
                    else:
                        room = find_room(cell)
                    #print("ауд", room)




                # print(data[k][2+i])
                exer = {}
                if exercise == '.':
                    exercise = None
                exer['source'] = data[k][2 + i]
                if room and len(room) > 22:
                    types = ['error']
                    exer['source'] = data[k][2 + i]
                    # print()
                    # print( exercise, teachers, room)
                    # room = exercise = teachers = None
                if exercise or parity or teachers or types or room:
                    exer['parity'] = parity
                    exer['teachers'] = teachers
                    exer['types'] = types
                    exer['title'] = exercise
                    exer['room'] = room

                    already_has = False
                    for ex in schedule[group][str(day + 1)][str(num + 1)]:
                        if ex['parity'] == parity:
                            already_has = True
                    if not already_has:
                        schedule[group][str(day + 1)][str(num + 1)].append(exer)

            k += 1

    for i in schedule.keys():
        json.dump(schedule[i], sort_keys=True, indent=2, ensure_ascii=False,
                  fp=open('json\%s.json' % i.replace('/', '-'), 'w', encoding='utf8'))
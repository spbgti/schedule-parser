# -*- coding: utf-8 -*-
"""
Created on Sat Sep 10 22:12:36 2016

@author: kotvb_000
"""
import requests
import json
import glob

url_api = r'https://spbgti-tools-schedule.herokuapp.com/api/'
#url_api = r'http://127.0.0.1:8000/api/'

def get_group_id(group_name):
    get_group = requests.get(url_api + 'groups/' + group_name)
    if get_group.status_code == 200:
        group_id = get_group.json()['group_id']
    elif get_group.status_code == 404:
        create_group = requests.post(url_api + 'groups', headers={'content-type': 'application/json'},
                                     data=json.dumps({'number': group_name}))
        if create_group.status_code == 201:
            group_id = create_group.json()['group_id']
        else:
            raise ValueError(create_group)
    else:
        raise ValueError(get_group)
    return group_id


def get_schedule_id(group_name, year, semester):
    get_schedule = requests.get(url_api + 'schedules/group/%s/year/%s/semester/%s' % (group_name, year, semester))
    if get_schedule.status_code == 200:
        schedule_id = get_schedule.json()['schedule_id']
    elif get_schedule.status_code == 404:
        create_schedule = requests.post(url_api + 'schedules', headers={'content-type': 'application/json'},
                                        data=json.dumps({'group_id': group_id, 'year': year, 'semester': semester}))
        if create_schedule.status_code == 201:
            schedule_id = create_schedule.json()['schedule_id']
        else:
            raise ValueError(create_schedule)
    else:
        raise ValueError(get_schedule)
    return schedule_id


def get_teacher_id(teacher_name):
    get_teacher = requests.get(url_api + 'teachers/%s' % teacher_name)
    if get_teacher.status_code == 200:
        teacher_id = get_teacher.json()['teacher_id']
    elif get_teacher.status_code == 404:
        create_teacher = requests.post(url_api + 'teachers', headers={'content-type': 'application/json'},
                                       data=json.dumps({'name': teacher_name}))
        if create_teacher.status_code == 201:
            teacher_id = create_teacher.json()['teacher_id']
        else:
            raise ValueError(create_teacher)
    else:
        raise ValueError(get_teacher)
    return teacher_id


def get_location_id(location_name):
    get = requests.get(url_api + 'locations/%s' % location_name)
    if get.status_code == 200:
        location_id = get.json()['location_id']
    elif get.status_code == 404:
        create = requests.post(url_api + 'locations', headers={'content-type': 'application/json'},
                               data=json.dumps({'name': location_name}))
        if create.status_code == 201:
            location_id = create.json()['location_id']
        else:
            raise ValueError(create)
    else:
        raise ValueError(get)
    return location_id


def get_room_id(room_name):
    get_room = requests.get(url_api + 'rooms/%s' % room_name)
    if get_room.status_code == 200:
        room_id = get_room.json()['room_id']
    elif get_room.status_code == 404:
        create_room = requests.post(url_api + 'rooms', headers={'content-type': 'application/json'}, data=json.dumps(
            {'name': room_name, 'location_id': get_location_id('Главный корпус')}))
        if create_room.status_code == 201:
            room_id = create_room.json()['room_id']
        else:
            raise ValueError(create_room)
    else:
        raise ValueError(get_room)
    return room_id


def create_exercise(day, pair, parity, teachers_id, types, title, room_id, schedule_id):
    exercise = requests.post(
        url_api + 'exercises',
        headers={'content-type': 'application/json'},
        data=json.dumps({
            'room_id': room_id,
            'parity': parity,
            'schedule_id': schedule_id,
            'teachers': teachers_id,
            'type': ', '.join(types),
            'name': title,
            'day': day,
            'pair': pair
        })
    )
    if exercise.status_code == 201:
        return exercise.json()['exercise_id']
    else:
        raise ValueError(exercise)


def update_exercise(exercise_id, day, pair, parity, teachers_id, types, title, room_id, schedule_id):
    exercise = requests.put(
        url_api + 'exercises/id/%d' % exercise_id,
        headers={'content-type': 'application/json'},
        data=json.dumps({
            'room_id': room_id,
            'parity': parity,
            'schedule_id': schedule_id,
            'teachers': teachers_id,
            'type': ', '.join(types),
            'name': title,
            'day': day,
            'pair': pair
        })
    )
    if exercise.status_code == 200:
        print(exercise.json())
        return exercise.json()['exercise_id']
    else:
        raise ValueError(exercise)


for file_name in glob.glob(r'json\*.json'):
    try:
        group_name = file_name.split('\\')[1].split('.')[0]
        group_id = get_group_id(group_name)

        semester = '1'
        year = '2020'
        schedule_id = get_schedule_id(group_name, year, semester)
        print(group_name, group_id, schedule_id)
        schedule = json.load(open(file_name, 'r', encoding='utf8'))
        for day in range(1, 8):
            for num in range(1, 6):
                pairs = schedule[str(day)][str(num)]

                for pair in pairs:
                    teachers_id = []
                    room_id = get_room_id('на кафедре')
                    if not 'error' in pair['types']:
                        for teacher in pair['teachers']:
                            teachers_id.append(get_teacher_id(teacher))
                        if pair['room']:
                            room_id = get_room_id(pair['room'])

                    else:
                        pair['title'] = ' '
                    # print(day, num, pair['parity'])
                    exercise = requests.get(url_api + 'exercises/schedule/%d/day/%d/pair/%d/parity/%s' % (
                    schedule_id, day, num, pair['parity'] or ''))

                    if exercise.status_code == 404:
                        create_exercise(day, num, pair['parity'], teachers_id, pair['types'], pair['title'], room_id,
                                        schedule_id)
                    elif exercise.status_code == 200:
                        new_exercise = {
                            'exercise_id': exercise.json()['exercise_id'],
                            'room_id': room_id,
                            'parity': str(pair['parity']) if pair['parity'] is not None else pair['parity'],
                            'schedule_id': schedule_id,
                            'teachers': teachers_id,
                            'type': ', '.join(pair['types']),
                            'name': pair['title'],
                            'day': str(day),
                            'pair': str(num)
                        }
                        if exercise.json() != new_exercise:
                            # print('перезапись', exercise.json(), new_exercise)
                            update_exercise(exercise.json()['exercise_id'], day, num, pair['parity'], teachers_id,
                                            pair['types'], pair['title'], room_id, schedule_id)
                        else:
                            print('ничего не поменялось')
                            # update_exercise()
                    else:
                        raise ValueError(exercise)

    except ValueError as e:
        print(e.args[0].url, e.args[0].status_code, e.args[0].text, e.args[0].request.body)
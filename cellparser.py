import re

def find_parity(cell):
    parity_res = re.search(r'(?:(?:(?P<odd>нечетн)|(?P<even>четн))[.\s]+)', cell, re.I)
    if parity_res:
        if parity_res.group('odd'):
            parity = 2
        elif parity_res.group('even'):
            parity = 1
        return parity, cell[parity_res.end():]
    else:
        return None, cell


def find_exercise(cell):
    # exercise = re.match(r'(?:(?:[а-я](?:-[а-я]+)?)|[\s]|(?:[(][а-я ]+[)])?)+', cell, re.I)
    # exercise = re.match(r'((?:[а-я]+(?:\s|-[а-я]+)?)+[(][а-я\s]+[)])?', cell, re.I)
    # print(cell, exercise)
    exercise = re.match(r'((?:[(][а-я ]+[)]|\s|[а-я]+-[а-я]+|[а-я]+[, .]*)*)', cell, re.I)
    if exercise:
        return exercise.group(0).upper().strip(), cell[exercise.end():]
    else:
        return "error, requires manual verification", ""


def find_teacher(cell):
    teachers = []
    if len(cell) != 0:
        first = re.search(r'[а-я]', cell, re.I)
        if first:
            cell = cell[first.start():]
        else:
            return teachers, cell.strip()
        shift = 0
        for m in re.finditer(
                r'(?:(асс|доц|проф|(?:ст[. ]пр))[.]?)?[ ]*(?P<n1>[а-я-]+)[ ]+(?P<n2>[а-я])[. ]+(?P<n3>[а-я])[. ,$]?', cell,
                re.I):
            if m:
                teachers.append('%s %s.%s.' % (m.group('n1').title(), m.group('n2').title(), m.group('n3').title()))
                cell = cell[:m.start() - shift] + cell[m.end() - shift:]
                shift += m.end() - m.start()
    return teachers, cell.strip()


def find_type(cell):
    types = []
    if len(cell) != 0:
        shift = 0
        for m in re.finditer(r'(?:(?<![а-я])(?P<type>лек|практ|лаб|к[ ]?[./][ ]?[рп])[a-я]*)[.,]{0,2}', cell, re.I):
            if m:
                types.append(m.group('type').replace(' ', '').lower())
                cell = cell[:m.start() - shift] + cell[m.end() - shift:]
                shift += m.end() - m.start()
    return types, cell.strip()


def find_room(cell):
    if len(cell) != 0:
        first = re.search(r'[а-я0-9]', cell, re.I)
        if first:
            cell = cell[first.start():]
        else:
            return re.sub(r'\s+', ' ', cell).strip()
        room = re.sub(r'(ауд([а-я]+|[. ])?)|(каф([а-я]+|[. ])?)|на', '', cell, flags=re.I)
        room = re.sub(r'\s+', ' ', room).strip(' .,')
        return room if len(room) > 0 else None
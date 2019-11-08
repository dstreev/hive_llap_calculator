def left(field, length):
    diff = length - len(str(field))
    return str(field) + " " * diff


def center(field, length):
    diff = length - len(str(field))
    return " " * (diff / 2) + str(field) + " " * (length - len(str(field)) - (diff / 2))


def right(field, length):
    diff = length - len(str(field))
    return " " * diff + str(field)


def pprinttable(rows, fields):
    output = buildtable(rows, fields)
    for line in output:
        print line


def buildtable(rows, fields):
    str_list = []

    if len(rows) > 0:
        # headers = HEADER._fields
        # headers = HEADER
        lens = []
        for field in fields:
            lens.append(len(field[1]))

        for row in rows:
            inc = 0
            for field in fields:
                if isinstance(row[field[0]], (int, float, long)):
                    if lens[inc] < 16:
                        lens[inc] = 16
                elif isinstance(row[field[0]], (list, tuple)):
                    size = 2
                    for i in range(len(row[field[0]])):
                        size += len(row[field[0]][i]) + 3
                    if size > lens[inc]:
                        lens[inc] = size
                else:
                    if row[field[0]] is not None and (len(row[field[0]]) > lens[inc]):
                        lens[inc] = len(row[field[0]])
                inc += 1

        headerRowSeparator = ""
        headerRow = ""
        for loc in range(len(fields)):
            headerRowSeparator = headerRowSeparator + "|" + "=" * (lens[loc]+1)
            headerRow = headerRow + "| " + center([fields[loc][1]], lens[loc])

        headerRowSeparator = headerRowSeparator + "|"
        headerRow = headerRow + "|"

        str_list.append(headerRowSeparator)
        # print headerRowSeparator
        str_list.append(headerRow)
        # print headerRow
        str_list.append(headerRowSeparator)
        # print headerRowSeparator

        for row in rows:
            inc = 0
            recordRow = ""
            for field in fields:
                if isinstance(row[field[0]], int) or isinstance(row[field[0]], float) or isinstance(row[field[0]], long):
                    recordRow = recordRow + "| " + right(row[field[0]], lens[inc])
                else:
                    recordRow = recordRow + "| " + left(row[field[0]], lens[inc])
                inc += 1
            recordRow = recordRow + "|"

            str_list.append(recordRow)
            # print recordRow

        str_list.append(headerRowSeparator)
        # print headerRowSeparator
    return str_list

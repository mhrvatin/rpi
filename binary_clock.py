def parse_decimal_time(hour, minute, second):
    time = [hour, minute, second]

    return decimal_to_binary(time)

def decimal_to_binary(time_array):
    ret = []

    for elem in time_array:
        if elem >= 10:
            for i in range(0,2):
                ret.append("{0:04b}".format(int(str(elem)[i:i + 1])))
        else:
            ret.append('0000')
            ret.append("{0:04b}".format(elem))

    return ret

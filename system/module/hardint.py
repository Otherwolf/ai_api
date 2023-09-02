import re


# Оставить одни числа
def only_digitals(str):
   return re.sub("\D", "", str)


# Преобразование строки в int, даже если строка без чисел!
def hardint(s):
    res = 0
    if isinstance(s, str):
        s_digital = only_digitals(s)
        if s_digital:
            res = int(s_digital)
    elif isinstance(s, (float, int)):
        res = int(s)
    return res

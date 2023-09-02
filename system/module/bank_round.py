import sys
from math import ceil, fabs


def amount_epsilon(amount: float) -> float:
    return amount + (sys.float_info.epsilon if amount >= 0 else -sys.float_info.epsilon)


def bank_round(amount: float, n: int) -> float:
    return round(amount_epsilon(amount), n)


def bank_round_up(amount: float) -> float:
    return float(ceil(amount_epsilon(amount)))


def f_cmp(a: float, b: float):
    return fabs(a-b) <= sys.float_info.epsilon

# import decimal
# # a = 8.0107
# # b = 0.056
#
# a = 1
# b = 0.4549
# unit_price = decimal.Decimal(str(a))
# quantity = decimal.Decimal(str(b))
# price = unit_price * quantity
# cents = decimal.Decimal('.01')
# money = price.quantize(cents, decimal.ROUND_HALF_UP)
# c = a * b
# print(c)
# print(round(c,2))
# print(money)

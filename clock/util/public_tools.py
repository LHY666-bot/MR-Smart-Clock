import random
import datetime
from entity import organizations as o

# 随机生成长度为 len 的数字
def randomNumber(len):
    first = str(random.randint(1, 9))
    last = "".join(random.sample("1234567890", len - 1))
    return first + last

# 随机生成与特征码长度相等的数字
def randomCode():
    return randomNumber(o.CODE_LEN)

# 校验时间格式
def valid_time(str):
    try:
        datetime.datetime.strptime(str, "%H:%M:%S")
        return True
    except:
        return False
        

# 校验年月格式
def valid_year_month(str):
    try:
        datetime.datetime.strptime(str, "%Y-%m")
        return True
    except:
        return False

# 校验日期格式
def valid_date(date):
    try:
        datetime.datetime.strptime(date, "%Y-%m-%d")
        return True
    except:
        return False
# 员工类
class Employee:
    def __init__(self, id, name, code):
        self.name = name    # 员工姓名
        self.id = id         # 员工编号
        self.code = code     # 员工的特征码
# 全局变量
LOCK_RECORD = dict()      # 打卡记录字典，格式为 {姓名: [时间1, 时间2,...]}
EMPLOYEES = list()        # 全体员工列表
MAX_ID = 0                 # 目前可用的最大 ID
CODE_LEN = 6               # 特征码的默认长度
WORK_TIME = ""             # 上班时间
CLOSING_TIME = ""          # 下班时间
USERS = dict()             # 管理员账号密码字典

# 添加新员工
def add(e: Employee):
    EMPLOYEES.append(e)

# 删除指定 ID 的员工记录
def remove(id):
    for emp in EMPLOYEES:
        if str(id) == str(emp.id):
            EMPLOYEES.remove(emp)               # 员工列表中删除员工
            if emp.name in LOCK_RECORD.keys():  # 如果存在该员工的打卡记录
                del LOCK_RECORD[emp.name]      # 删除该员工的打卡记录
            break

# 获取新员工的 ID
def get_new_id():
    global MAX_ID        # 声明使用全局变量
    MAX_ID += 1          # 当前最大的 ID + 1
    return MAX_ID
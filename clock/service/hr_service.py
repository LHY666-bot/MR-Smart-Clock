from entity import organizations as o
from util import public_tools as tool
from util import io_tools as io
import datetime
import calendar

def load_emp_data():
    io.checking_data_files()
    io.load_users()
    io.load_lock_record()
    io.load_employee_info()
    io.load_employee_pic()

def add_new_employee(name):
    code = tool.randomCode()
    newEmp = o.Employee(o.get_new_id(), name, code)
    o.add(newEmp)
    io.save_employee_all()
    return code

def remove_employee(id):
    tool.remove_pics(id)
    o.remove(id)
    io.save_employee_all()
    io.save_lock_record()

def add_lock_record(name):
    record = o.LOCK_RECORD
    now_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if name in record.keys():
        r_list = record[name]
        if len(r_list) == 0:
            r_list = list()
        r_list.append(now_time)
    else:
        r_list = list()
        r_list.append(now_time)
        record[name] = r_list
    io.save_lock_record()

def get_employee_report():
    report = list()
    report = "################################################\n"
    report += "员工名单如下所示:\n"
    i = 0
    for emp in o.EMPLOYEES:
        report += "(" + str(emp.id) + ")" + emp.name + "\t"
        i += 1
        if i == 4:
            report += "\n"
            i = 0
    report = report.strip()
    report += "\n################################################"
    return report

def check_id(id):
    for emp in o.EMPLOYEES:
        if str(id) == str(emp.id):
            return True
    return False

def get_name_with_code(code):
    for emp in o.EMPLOYEES:
        if str(code) == str(emp.code):
            return emp.name

def get_code_with_id(id):
    for emp in o.EMPLOYEES:
        if str(id) == str(emp.id):
            return emp.code
    return None

def valid_user(username, password):
    if username in o.USERS.keys():
        if o.USERS[username] == password:
            return True
    return False

def get_today_report():
    date = datetime.datetime.now().strftime("%Y-%m-%d")
    get_day_report(str(date))

def get_day_report(date):
    io.load_work_time_config()
    emp_count = len(o.EMPLOYEES)
    absent_list = []
    late_list = []
    left_early = []
    
    for emp in o.EMPLOYEES:
        is_absent = True
        is_late = False
        is_left_early = False
        
        if emp.name in o.LOCK_RECORD.keys():
            emp_lock_list = o.LOCK_RECORD.get(emp.name)
            for lock_time_str in emp_lock_list:
                if date in lock_time_str:
                    is_absent = False
                    lock_time = datetime.datetime.strptime(lock_time_str, "%Y-%m-%d %H:%M:%S").time()
                    work_time = datetime.datetime.strptime(o.WORK_TIME, "%H:%M:%S").time()
                    closing_time = datetime.datetime.strptime(o.CLOSING_TIME, "%H:%M:%S").time()
                    
                    if lock_time > work_time:
                        is_late = True
                    if lock_time < closing_time and lock_time > datetime.datetime.strptime("12:00:00", "%H:%M:%S").time():
                        is_left_early = True
        
        if is_absent:
            absent_list.append(emp.name)
        elif is_late:
            late_list.append(emp.name)
        elif is_left_early:
            left_early.append(emp.name)
    
    print("---------" + date + "---------")
    print("应到人数: " + str(emp_count))
    print("缺席人数: " + str(len(absent_list)))
    absent_name = ""
    if len(absent_list) == 0:
        absent_name = "(空)"
    else:
        for name in absent_list:
            absent_name += name + " "
    print("缺席名单: " + absent_name)
    print("迟到人数: " + str(len(late_list)))
    late_name = ""
    if len(late_list) == 0:
        late_name = "(空)"
    else:
        for name in late_list:
            late_name += name + " "
    print("迟到名单: " + str(late_name))
    print("早退人数: " + str(len(left_early)))
    early_name = ""
    if len(left_early) == 0:
        early_name = "(空)"
    else:
        for name in left_early:
            early_name += name + " "
    print("早退名单: " + early_name)

def get_month_report(month):
    io.load_work_time_config()
    date = datetime.datetime.strptime(month, "%Y-%m")
    monthRange = calendar.monthrange(date.year, date.month)[1]
    month_first_day = datetime.date(date.year, date.month, 1)
    month_last_day = datetime.date(date.year, date.month, monthRange)

    clock_in = "I"
    clock_out = "O"
    late = "L"
    left_early = "E"
    absent = "A"

    lock_report = dict()

    for emp in o.EMPLOYEES:
        emp_lock_data = []
        if emp.name in o.LOCK_RECORD.keys():
            emp_lock_list = o.LOCK_RECORD.get(emp.name)
            index_day = month_first_day
            while index_day <= month_last_day:
                is_absent = True
                earliest_time = datetime.datetime.strptime(str(index_day) + " 00:00:00", "%Y-%m-%d %H:%M:%S")
                noon_time = datetime.datetime.strptime(str(index_day) + " 12:00:00", "%Y-%m-%d %H:%M:%S")
                latest_time = datetime.datetime.strptime(str(index_day) + " 23:59:59", "%Y-%m-%d %H:%M:%S")
                work_time = datetime.datetime.strptime(str(index_day) + " " + o.WORK_TIME, "%Y-%m-%d %H:%M:%S")
                closing_time = datetime.datetime.strptime(str(index_day) + " " + o.CLOSING_TIME, "%Y-%m-%d %H:%M:%S")
                emp_today_data = ""

                for lock_time_str in emp_lock_list:
                    lock_time = datetime.datetime.strptime(lock_time_str, "%Y-%m-%d %H:%M:%S")
                    if earliest_time < lock_time < latest_time:
                        is_absent = False
                        if lock_time <= work_time:
                            emp_today_data += clock_in
                        elif lock_time >= closing_time:
                            emp_today_data += clock_out
                        elif work_time < lock_time <= noon_time:
                            emp_today_data += late
                        elif noon_time < lock_time < closing_time:
                            emp_today_data += left_early
                if is_absent:
                    emp_today_data = absent
                emp_lock_data.append(emp_today_data)
                index_day = index_day + datetime.timedelta(days=1)
        else:
            index_day = month_first_day
            while index_day <= month_last_day:
                emp_lock_data.append(absent)
                index_day = index_day + datetime.timedelta(days=1)
        lock_report[emp.name] = emp_lock_data

    report = "\"姓名 / 日期\""
    index_day = month_first_day
    while index_day <= month_last_day:
        report += ",\"" + str(index_day) + "\""
        index_day = index_day + datetime.timedelta(days=1)
    report += "\n"

    for emp in lock_report.keys():
        report += "\"" + emp + "\""
        data_list = lock_report.get(emp)
        for data in data_list:
            text = ""
            if absent == data:
                text = "【缺席】"
            elif clock_in in data and clock_out in data:
                text = ""
            else:
                if late in data and clock_in not in data:
                    text += "【迟到】"
                if left_early in data and clock_out not in data:
                    text += "【早退】"
                if clock_out not in data and left_early not in data:
                    text += "【下班未打卡】"
                if clock_in not in data and late not in data:
                    text += "【上班未打卡】"
            report += ",\"" + text + "\""
        report += "\n"

    title_date = month_first_day.strftime("%Y年%m月")
    file_name = title_date + "考勤月报"
    io.create_CSV(file_name, report)

def get_pre_month_report():
    today = datetime.date.today()
    pre_month_first_day = datetime.date(today.year, today.month - 1, 1)
    pre_month = pre_month_first_day.strftime("%Y-%m")
    get_month_report(pre_month)

def save_work_time(work_time, close_time):
    o.WORK_TIME = work_time
    o.CLOSING_TIME = close_time
    io.save_work_time_config()

def get_record_all():
    result = "打卡记录:\n"
    for name, records in o.LOCK_RECORD.items():
        result += name + ": " + ", ".join(records) + "\n"
    if len(o.LOCK_RECORD) == 0:
        result += "(空)"
    return result
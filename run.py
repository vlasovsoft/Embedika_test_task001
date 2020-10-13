import datetime
import pandas as pd
import json
from flask import Flask, request, render_template
import os.path
from functools import wraps
import inspect

#-------------------------

CATALOG_PATH = ''   
DATA_GOV_RU_PATH = CATALOG_PATH + 'data-20200817T1010-structure-20200817T1010.csv'
PRICES_IN_PERIODS = []

def cach_it(func):
    def cacher(*args):
        key_for_cach = func.__name__ + '('
        for arg in args:
          key_for_cach += str(arg) + ','
        if len(args) > 0:
            key_for_cach = key_for_cach[0:-1]
        key_for_cach  += ')'
        cached_value = find_cached_value(key_for_cach)
        if cached_value is not None:
            return cached_value
        else:
            result = func(*args)
            upload_value_to_cach(key_for_cach, result)
            return result
    return cacher

def find_cached_value(str_func_with_args):
    with open("cach.json", "r") as cach_file:
        functions_questions_and_answers = json.load(cach_file)
    if str_func_with_args in functions_questions_and_answers:
        return functions_questions_and_answers[str_func_with_args]
    else:
        return None

def upload_value_to_cach(str_func_with_args_as_key, value):
    with open("cach.json", "r") as cach_file:
        functions_questions_and_answers = json.load(cach_file)
    new_data = {str_func_with_args_as_key: value}
    functions_questions_and_answers.update(new_data)
    with open("cach.json", "w") as cach_file:
        json.dump(functions_questions_and_answers, cach_file)
        
    
def log_it(func):
    @wraps(func)
    def logger():
        start_time = datetime.datetime.now()
        result = func()
        execution_time_in_microseconds = (datetime.datetime.now() - start_time).microseconds
        log_str = str(start_time.date()) + ' in ' + str(start_time.time()) + ' function: "' + func.__name__ + '()" was performed for ' + str(execution_time_in_microseconds) + ' microseconds'
        update_log(log_str)
        return result
    return logger
    

def update_log(log_str):
    if not os.path.exists('log.txt'):
        file = open("log.txt", "w")
    else:
        file = open("log.txt", "a")
    file.writelines([log_str, '<br>', '\n'])
    file.close()


def log_for_front_end():
    result_str = 'log: <br>'
    with open("log.txt", "r") as log_file:
        contents = log_file.readlines()
    contents.reverse()
    for line in contents:
        result_str += line
    return result_str


def adapt_date(rus_utf8_date_str):
    def convert_rus_utf8_date_to_str_point_separated_date(rus_date):
        rus_utf8_months = {'01':'янв', '02':'фев', '03':'мар', '04':'апр', '05':'май', '06':'июн', '07':'июл', '08':'авг', '09':'сен', '10':'окт', '11':'ноя','12':'дек'}
        for str_number_of_month in rus_utf8_months:
            str_point_separated_date = rus_utf8_date_str.replace(rus_utf8_months[str_number_of_month], str_number_of_month)
            if str_point_separated_date != rus_utf8_date_str:
                str_date_without_points = str_point_separated_date.replace('.', '')
                return str_date_without_points

    str_date = convert_rus_utf8_date_to_str_point_separated_date(rus_utf8_date_str)
    year = 2000 + int(str_date[4:6]); month = int(str_date[2:4]); day = int(str_date[0:2])
    datetime_date = datetime.datetime(year,month,day).date()
    return datetime_date


def min_possible_date():
    return PRICES_IN_PERIODS[0]['start_date']

def max_possible_date():
    return PRICES_IN_PERIODS[-1]['end_date']


def make_prices_in_periods_objects_from_data_gov_ru_data_file(path):
    data_frame = pd.read_csv(path, encoding='UTF8')
    data_frame_as_list = []
    for column_name in data_frame.to_dict().keys():
        data_frame_as_list.append(data_frame.to_dict()[column_name]) 
    for i in range(0, len(data_frame_as_list[0])):
        price_in_period = {}
        price_in_period['start_date'] = adapt_date(data_frame_as_list[0][i])
        price_in_period['end_date'] = adapt_date(data_frame_as_list[1][i])
        price_in_period['average_price'] = float(data_frame_as_list[2][i].replace(',','.'))
        PRICES_IN_PERIODS.append(price_in_period)
    return PRICES_IN_PERIODS

def get_date_from_front_end(yyyy_mm_dd):
     return  datetime.datetime.strptime(yyyy_mm_dd, '%Y-%m-%d').date()


def prices_in_part_of_periods(start_of_period, end_of_period):
    #data is sorted by date from file
    i = 0
    start_index = 0; end_index = len(PRICES_IN_PERIODS) + 1
    for i in range(len(PRICES_IN_PERIODS)):
        if PRICES_IN_PERIODS[i]['start_date'] <= start_of_period <= PRICES_IN_PERIODS[i]['end_date']:
            start_index = i
        if PRICES_IN_PERIODS[i]['start_date'] <= end_of_period <= PRICES_IN_PERIODS[i]['end_date']:
            end_index = i+1
    return PRICES_IN_PERIODS[start_index:end_index]

@cach_it
def average_price_for_period(start_of_period, end_of_period): 
    part_of_price_in_periods = prices_in_part_of_periods(start_of_period, end_of_period)
    sum = 0
    for price_in_period in part_of_price_in_periods:
        sum += price_in_period['average_price']
    return sum / len(part_of_price_in_periods)
            

@cach_it
def json_min_and_max_average_prices_for_period(start_of_period, end_of_period):
    min_average_price, max_average_price = 0, 0
    part_of_price_in_periods = prices_in_part_of_periods(start_of_period, end_of_period)
    if len(part_of_price_in_periods) > 0:
        min_average_price = max_average_price = part_of_price_in_periods[0]['average_price'] 
    for i in range(1, len(part_of_price_in_periods)):
        if min_average_price > part_of_price_in_periods[i]['average_price']:
            min_average_price = part_of_price_in_periods[i]['average_price']
        if max_average_price < part_of_price_in_periods[i]['average_price']:
            max_average_price = part_of_price_in_periods[i]['average_price']
    json_data = {
        'min': min_average_price,
        'max': max_average_price
    }
    return json.dumps(json_data)


@cach_it
def json_min_max_and_average_average_prices_for_period(start_of_period, end_of_period):
    min_and_max_dict = json.loads(json_min_and_max_average_prices_for_period(start_of_period, end_of_period))
    average_price_dict = {'average': average_price_for_period(start_of_period, end_of_period)}
    min_and_max_dict.update(average_price_dict)
    min_max_and_average = min_and_max_dict
    return json.dumps(min_max_and_average)

@cach_it   
def json_total_lines_from_data_gov_ru():
    json_data = {'total entries': len(PRICES_IN_PERIODS)}
    return json.dumps(json_data)

@cach_it
def price_for_date(date):
    for price_in_period in PRICES_IN_PERIODS:
        if price_in_period['start_date'] <= date <= price_in_period['end_date']:
            return price_in_period['average_price']
    return .0


def start_process():
    PRICES_IN_PERIODS = make_prices_in_periods_objects_from_data_gov_ru_data_file(DATA_GOV_RU_PATH)
    if not os.path.exists('cach.json'):
        file = open("cach.json", "w")
        file.writelines('{}')
        file.close()
        
#---------------

app = Flask(__name__, template_folder='.', static_folder='static')

@app.route('/')
@log_it
def route_home():
    return render_template('index.html')

@app.route('/min_date')
@log_it
def route_min_date():
    str_min_date = str(min_possible_date())[0:10]
    return str_min_date

@app.route('/max_date')
@log_it
def route_max_date():
    str_max_date = str(max_possible_date())[0:10]
    return str_max_date


@app.route('/price_for_date')
@log_it
def route_price_for_date():
    str_date = request.args['start_date']
    date = get_date_from_front_end(str_date)
    price = price_for_date(date)
    return str(price)


@app.route('/average_price_for_period')
@log_it
def route_average_price_for_period():
    start_date = get_date_from_front_end(request.args['start_date'])
    end_date = get_date_from_front_end(request.args['end_date'])
    average_price = average_price_for_period(start_date, end_date)
    return str(average_price)


@app.route('/json_min_max_for_period')
@log_it
def route_json_min_max_for_period():
    start_date = get_date_from_front_end(request.args['start_date'])
    end_date = get_date_from_front_end(request.args['end_date'])
    json_min_and_max = json_min_and_max_average_prices_for_period(start_date, end_date)
    return str(json_min_and_max)


@app.route('/json_total_entries')
@log_it
def route_json_total_entries():
    json_total_entries = json_total_lines_from_data_gov_ru()
    return str(json_total_entries)


@app.route('/json_min_max_and_average_for_period')
@log_it
def route_json_min_max_and_average_for_period():
    start_date = get_date_from_front_end(request.args['start_date'])
    end_date = get_date_from_front_end(request.args['end_date'])
    json_min_max_and_average = json_min_max_and_average_average_prices_for_period(start_date, end_date)
    return str(json_min_max_and_average)

@app.route('/log')
@log_it
def route_log():
    return log_for_front_end()

 

if __name__ == '__main__':
    start_process()
    app.run()



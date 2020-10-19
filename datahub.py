import pandas as pd
import datetime

CATALOG_PATH = 'input_data/'   
DATA_GOV_RU_PATH = CATALOG_PATH + 'data-20200817T1010-structure-20200817T1010.csv'

class DataHub(object):
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance
    

    def get_date_from_front_end(self, yyyy_mm_dd):
        return  datetime.datetime.strptime(yyyy_mm_dd, '%Y-%m-%d').date()

    
    def get_prices_in_periods(self):
        if not hasattr(self, 'prices_in_periods'):
            self.prices_in_periods = self.make_prices_in_periods_objects(DATA_GOV_RU_PATH)
        return self.prices_in_periods

    
    def make_prices_in_periods_objects(self,path):
        data_frame = pd.read_csv(path, encoding='UTF8')
        data_frame_as_list = []
        self.prices_in_periods = []
        for column_name in data_frame.to_dict().keys():
            data_frame_as_list.append(data_frame.to_dict()[column_name]) 
        for i in range(0, len(data_frame_as_list[0])):
            price_in_period = {}
            price_in_period['start_date'] = self.adapt_date(data_frame_as_list[0][i])
            price_in_period['end_date'] = self.adapt_date(data_frame_as_list[1][i])
            price_in_period['average_price'] = float(data_frame_as_list[2][i].replace(',','.'))
            self.prices_in_periods.append(price_in_period)
        return self.prices_in_periods


    def min_date(self):
        return self.get_prices_in_periods()[0]['start_date']
    

    def max_date(self):
        return self.get_prices_in_periods()[-1]['end_date']
    

    def adapt_date(self, utf8_date_str):
        def parse_utf8_date(rus_date):
            rus_utf8_months = {'01':'янв', '02':'фев', '03':'мар', '04':'апр', '05':'май', '06':'июн', '07':'июл', '08':'авг', '09':'сен', '10':'окт', '11':'ноя','12':'дек'}
            for str_number_of_month in rus_utf8_months:
                str_point_separated_date = utf8_date_str.replace(rus_utf8_months[str_number_of_month], str_number_of_month)
                if str_point_separated_date != utf8_date_str:
                    str_date_without_points = str_point_separated_date.replace('.', '')
                    return str_date_without_points
    
        str_date = parse_utf8_date(utf8_date_str)
        year = 2000 + int(str_date[4:6]); month = int(str_date[2:4]); day = int(str_date[0:2])
        datetime_date = datetime.datetime(year,month,day).date()
        return datetime_date

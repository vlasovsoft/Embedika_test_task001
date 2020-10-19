from decorator import *
from datahub import *



class BackEnd():

    def date_is_correct(date):
        
        return DataHub().min_date() <= date <= DataHub().max_date()

    def get_date_error_msg():
        if not hasattr(BackEnd, 'date_error_msg'):
            BackEnd.date_error_msg = 'INPUT DATA ERROR!:  date(s) must be between ' + str(DataHub().min_date()) + ' and '  + str(DataHub().max_date())
        return BackEnd.date_error_msg


    def get_period_error_msg():
        if not hasattr(BackEnd, 'period_error_msg'):
            BackEnd.period_error_msg = 'INPUT DATA ERROR!: start date must be < end date of period'
        return BackEnd.period_error_msg

    
             
    
    def prices_in_part_of_periods(start_of_period, end_of_period):
        #data is sorted by date from file
        i = 0
        prices_in_periods = DataHub().get_prices_in_periods()
        start_index = 0; end_index = len(prices_in_periods) + 1
        for i in range(len(prices_in_periods)):
            if prices_in_periods[i]['start_date'] <= start_of_period <= prices_in_periods[i]['end_date']:
                start_index = i
            if prices_in_periods[i]['start_date'] <= end_of_period <= prices_in_periods[i]['end_date']:
                end_index = i+1
        return prices_in_periods[start_index:end_index]

    @Decorator.cach_it
    def avg_price_for_period(start_of_period, end_of_period):
        if not (BackEnd.date_is_correct(start_of_period) and BackEnd.date_is_correct(end_of_period)):
            return BackEnd.get_date_error_msg()
        if start_of_period > end_of_period:
            return BackEnd.get_period_error_msg()
        part_of_price_in_periods = BackEnd.prices_in_part_of_periods(start_of_period, end_of_period)
        sum = 0
        for price_in_period in part_of_price_in_periods:
            sum += price_in_period['average_price']
        return sum / len(part_of_price_in_periods)
            

    @Decorator.cach_it
    def json_min_and_max_prices_for_period(start_of_period, end_of_period):
        if not (BackEnd.date_is_correct(start_of_period) and BackEnd.date_is_correct(end_of_period)):
            return BackEnd.get_date_error_msg()
        if start_of_period > end_of_period:
            return BackEnd.get_period_error_msg()
        min_average_price, max_average_price = 0, 0
        part_of_price_in_periods = BackEnd.prices_in_part_of_periods(start_of_period, end_of_period)
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


    @Decorator.cach_it
    def json_min_max_and_average_for_period(start_of_period, end_of_period):
        if not (BackEnd.date_is_correct(start_of_period) and BackEnd.date_is_correct(end_of_period)):
            return BackEnd.get_date_error_msg()
        if start_of_period > end_of_period:
            return BackEnd.get_period_error_msg()
        min_and_max_dict = json.loads(BackEnd.json_min_and_max_prices_for_period(start_of_period, end_of_period))
        average_price_dict = {'average': BackEnd.avg_price_for_period(start_of_period, end_of_period)}
        min_and_max_dict.update(average_price_dict)
        min_max_and_average = min_and_max_dict
        return json.dumps(min_max_and_average)

    @Decorator.cach_it   
    def json_total_lines_from_data_gov_ru():
        json_data = {'total entries': len(DataHub().get_prices_in_periods())}
        return json.dumps(json_data)

    @Decorator.cach_it
    def price_for_date(date):

        if BackEnd.date_is_correct(date):
            for price_in_period in DataHub().get_prices_in_periods():
                if price_in_period['start_date'] <= date <= price_in_period['end_date']:
                    return price_in_period['average_price']
        return BackEnd.get_date_error_msg()

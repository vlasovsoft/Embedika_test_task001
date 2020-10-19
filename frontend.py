from flask import Flask, request, render_template
import inspect
from backend import *
from datahub import *
from decorator import *


class FrontEnd():

    app = Flask(__name__, template_folder='.', static_folder='static')
    data_hub = DataHub()

    @app.route('/')
    @Decorator.log_it
    def route_home():
        return render_template('index.html')

    @app.route('/min_date')
    @Decorator.log_it
    def route_min_date():
        str_min_date = str(FrontEnd.data_hub.min_date())[0:10]
        return str_min_date

    @app.route('/max_date')
    @Decorator.log_it
    def route_max_date():
        str_max_date = str(FrontEnd.data_hub.max_date())[0:10]
        return str_max_date


    @app.route('/price_for_date')
    @Decorator.log_it
    def route_price_for_date():
        str_date = request.args['start_date']
        date = FrontEnd.data_hub.get_date_from_front_end(str_date)
        price = BackEnd.price_for_date(date)
        return str(price)


    @app.route('/avg_price_for_period')
    @Decorator.log_it
    def route_avg_price_for_period():
        start_date = FrontEnd.data_hub.get_date_from_front_end(request.args['start_date'])
        end_date = FrontEnd.data_hub.get_date_from_front_end(request.args['end_date'])
        average_price = BackEnd.avg_price_for_period(start_date, end_date)
        return str(average_price)


    @app.route('/json_min_max_for_period')
    @Decorator.log_it
    def route_json_min_max_for_period():
        start_date = FrontEnd.data_hub.get_date_from_front_end(request.args['start_date'])
        end_date = FrontEnd.data_hub.get_date_from_front_end(request.args['end_date'])
        json_min_and_max = BackEnd.json_min_and_max_prices_for_period(start_date, end_date)
        return str(json_min_and_max)


    @app.route('/json_total_entries')
    @Decorator.log_it
    def route_json_total_entries():
        json_total_lines = BackEnd.json_total_lines_from_data_gov_ru()
        return str(json_total_lines)


    @app.route('/json_min_max_and_average_for_period')
    @Decorator.log_it
    def route_json_min_max_and_average_for_period():
        start_date = FrontEnd.data_hub.get_date_from_front_end(request.args['start_date'])
        end_date = FrontEnd.data_hub.get_date_from_front_end(request.args['end_date'])
        json_min_max_and_average = BackEnd.json_min_max_and_average_for_period(start_date, end_date)
        return str(json_min_max_and_average)

    @app.route('/log')
    @Decorator.log_it
    def route_log():
        return FileManager.get_log()

 
    def do_web():
        FrontEnd.app.run()



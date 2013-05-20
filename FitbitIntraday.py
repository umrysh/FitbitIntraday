
import cookielib
from datetime import datetime, timedelta
import os
from urllib import urlencode
import urllib2


class FitbitIntraday:
    '''
    FitbitIntraday is a class for retrieving the 1/5 minute intraday data from
    the fitbit.com website. For all other data requests you should use the
    official fitbit API: http://dev.fitbit.com/

    This utility will login as the user using the supplied credentials then it
    can be used to scrape and store the raw xml responses containing the user
    data. Supported data types are: steps, calories, floors, and time_active.
    '''

    def __init__(self):
        self.cookiej = cookielib.CookieJar()
        cookie_processor = urllib2.HTTPCookieProcessor(self.cookiej)
        self.opener = urllib2.build_opener(cookie_processor)
        urllib2.install_opener(self.opener)  # Yay violating encapsulation

        self.chart_types = {
            'steps': ('intradaySteps', 'column2d'),
            'calories': ('intradayCaloriesBurned', 'column2d'),
            'floors': ('intradayAltitude', 'column2d'),
            'time_active': ('activitiesBreakdown', 'pie')
        }

    def login(self, email, password):
        auth_url = 'https://www.fitbit.com/login'
        payload = {
            'login': 'Log In',
            'includeWorkflow': '',
            'loginRedirect': 'redirect',
            'email': email,
            'password': password
        }
        encoded_data = urlencode(payload)
        request_object = urllib2.Request(auth_url, encoded_data)

        #Request the url with our posted login. We now have session cookies
        response = urllib2.urlopen(request_object)
        return response

    def fetch_chart_data(self, data_type, chart_date):
        delta = timedelta(days=1)
        from_date = datetime.strftime(chart_date, "%Y-%m-%d")
        to_date = datetime.strftime(chart_date + delta, "%Y-%m-%d")

        request_string_parts = [
            'http://www.fitbit.com/graph/getGraphData?type=',
            self.chart_types[data_type][0],
            '&version=amchart&dateFrom=',
            from_date,
            '&dateTo=',
            to_date,
            '&chart_type=',
            self.chart_types[data_type][1]
        ]

        request_string = ''.join(request_string_parts)
        request = urllib2.Request(request_string)
        response = urllib2.urlopen(request)

        return response

    def fetch_range_to_folder(self, data_type, path, from_date, to_date):
        delta = timedelta(days=1)
        current_day = from_date
        typed_path = path + '\\' + data_type + '\\'

        if not os.path.exists(typed_path):
            os.makedirs(typed_path)

        while(current_day <= to_date):
            day_string = datetime.strftime(current_day, "%Y_%m_%d.xml")
            file_handle = open(typed_path + day_string, 'w')
            chart_data = self.fetch_chart_data(data_type, current_day)
            file_handle.write(chart_data.read())
            file_handle.close()
            current_day += delta

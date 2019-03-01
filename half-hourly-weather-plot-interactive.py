import requests
from bs4 import BeautifulSoup
from bokeh.plotting import figure
from bokeh.io import show

# select a palette
from bokeh.palettes import Dark2_5 as palette
# itertools handles the cycling
import itertools

class BOM_plots:
    def __init__(self,city_list):
        if type(city_list) is str:
            city_list = [city_list]
        self.all_data = {str(city): self.BOM_data(city) for city in city_list}

    def __call__(self,city_list):
        if type(city_list) is str:
            city_list = [city_list]
        for city in city_list:
            self.all_data[city] = self.BOM_data(city)


    class BOM_data:
        def __init__(self,city):
            self.city = city.lower()
            self.time_labels, self.halfhourly_temps = self.get_weather_data()
            # self.daily_max = self.get_forecasted_max()

        def get_weather_data(self):
            city_codes = {
                'adelaide': ['IDS60901', '94648'],
                'brisbane': ['IDQ60901', '94576'],
                'canberra': ['IDN60903', '94926'],
                'darwin': ['IDD60901', '94120'],
                'hobart': ['IDT60901', '94970'],
                'melbourne': ['IDV60801', '95936'],
                'perth': ['IDW60901', '94608'],
                'sydney': ['IDN60901', '95765']
            }

            city = city_codes[self.city]
            data = requests.get('http://www.bom.gov.au/products/' + city[0] + '/' +city[0] + '.' + city[1]  + '.shtml')

            soup = BeautifulSoup(data.text,'html.parser')

            todays_weather = soup.find('table',{'id': 't1'})
            tbody = todays_weather.find('tbody')

            time_data = []
            temp_data = []
            # extract all the time data for today so far
            for tr in tbody.find_all('tr',{'class': 'rowleftcolumn'}):
                time_data.append(tr.find_all('td', {'headers': 't1-datetime'})[0].text[3:])
                temp_data.append(float(tr.find_all('td', {'headers': 't1-tmp'})[0].text))

            return time_data[::-1], temp_data[::-1]

        def get_forecasted_max(self):
            data = requests.get('http://www.bom.gov.au')
            soup = BeautifulSoup(data.text, 'html.parser')

            todays_forecasts = soup.find('div', {'id': 'today_refresh'})
            city_forecast = todays_forecasts.find('a', {'title': self.city.capitalize() + ' forecast'})
            forecasted_max = int(city_forecast.find('span', {'class': 'max'}).text[:-1])
            return forecasted_max


    def plot(self):
        hours_in_day = 24
        # Create a blank figure with labels
        p = figure(plot_width=600, plot_height=600,
                      title='Australian Temperature Plot',
                      x_axis_label='Local Time', y_axis_label='Temperature \u2103',
                      x_range=(0, 2 * hours_in_day), y_range=(0, 50))

        # create x-axis labels
        x_labels = self.make_x_labels()

        # create iterator from the colour palette so can loop through the colours
        colours = itertools.cycle(palette)

        # add each city's graph to the plot
        for (city, city_class), colour in zip(self.all_data.items(),colours):
            x_values = [elem for elem in range(len(city_class.halfhourly_temps))]
            p.xaxis.major_label_overrides = {key: time for key, time in zip(range(len(x_labels)),x_labels)}
            # p.line([24,34], [city_class.daily_max, city_class.daily_max], line_width = 2, line_color = colour, line_dash = 'dashed',legend = 'Forecasted max')
            p.line(x_values, city_class.halfhourly_temps, line_width = 2, legend = city.capitalize() + ' temperature', line_color = colour)

        p.xgrid.minor_grid_line_color = 'lightgrey'
        p.ygrid.minor_grid_line_color = 'lightgrey'
        p.xgrid.minor_grid_line_alpha = 1
        p.ygrid.minor_grid_line_alpha = 1
        p.legend.click_policy = "hide"

        p.legend.location = "top_left"

        show(p)

    def make_x_labels(self):
        hours_in_day = 24
        nums = [elem + 1 for elem in range(int(hours_in_day/2))]
        nums = nums[-1:] + nums[:-1]
        nums = [item for item in nums for i in range(2)]

        labels = [str(elem) + ':30' if i%2 else str(elem) + ':00' for i,elem in enumerate(nums)]
        labels = labels + labels
        labels = [elem + 'am' if i<int(hours_in_day) else elem + 'pm' for i,elem in enumerate(labels)]

        return labels

if __name__ == '__main__':
    today = BOM_plots('brisbane')
    today.plot()
    # today('sydney')
    # today(['melbourne','canberra'])
    # today.plot()
    # print(today.halfhourly_temps)
    # today.initialise_plot()
    # show(today.graph)
    # today.plot()

# http://www.bom.gov.au/australia/majorcities.shtml
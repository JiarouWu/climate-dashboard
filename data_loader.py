import pandas as pd

def load_and_clean_data():
    weather = pd.read_csv("https://data.giss.nasa.gov/gistemp/tabledata_v4/NH.Ts+dSST.csv",
                          skiprows=1,
                          na_values="***")

    month_columns = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                     'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    weather_selected = weather[['Year'] + month_columns].copy()

    tidyweather = weather_selected.melt(id_vars=['Year'],
                                        value_vars=month_columns,
                                        var_name='month',
                                        value_name='delta')

    tidyweather['date'] = pd.to_datetime(tidyweather['Year'].astype(str) + '-' + tidyweather['month'] + '-01',
                                         format='%Y-%b-%d',
                                         errors='coerce')
    tidyweather['month_name'] = tidyweather['date'].dt.strftime('%b')
    tidyweather['year'] = tidyweather['date'].dt.year
    
    tidyweather = tidyweather.dropna(subset=['delta', 'date'])

    comparison = tidyweather[tidyweather['Year'] >= 1881].copy()

    def get_interval(year):
        if 1881 <= year <= 1920:
            return "1881-1920"
        elif 1921 <= year <= 1950:
            return "1921-1950"
        elif 1951 <= year <= 1980:
            return "1951-1980"
        elif 1981 <= year <= 2010:
            return "1981-2010"
        else:
            return "2011-present"

    comparison['interval'] = comparison['Year'].apply(get_interval)
    comparison['interval'] = pd.Categorical(comparison['interval'],
                                            categories=['1881-1920', '1921-1950', '1951-1980',
                                                        '1981-2010', '2011-present'],
                                            ordered=True)

    return tidyweather, comparison

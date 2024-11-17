from enum import Enum
import json
import requests
from datetime import datetime

STATCAN_URL = 'https://www150.statcan.gc.ca/t1/wds/rest/getDataFromCubePidCoordAndLatestNPeriods'
GOMPERTZ_MAX = 150 # maximum age possible by the gompertz equation

'''
    CLASS CONSTANTS
'''
class Gender(Enum):
    MALE = 'male'
    FEMALE = 'female'
    BOTH = 'both'
    
class Time(Enum):
    SHORT = 'short'
    MED = 'med'
    LONG = 'long'
    
class dataPIDs(Enum):
    # Life Expectancy PID
    LIFEEXP = 13100837
    # Inflation PID
    INFLATION = 18100259
    # Investment Returns PID
    BONDYIELDS = 10100139
    
class dataCoords(Enum):
    # Life Expectancy Coordinates
    LIFEEXP_BOTH = '1.1.1.8.0.0.0.0.0.0' # Canada, age 0, both sexes, Life expectancy
    LIFEEXP_MALE = '1.1.2.8.0.0.0.0.0.0' # Canada, age 0, both sexes, Life expectancy
    LIFEEXP_FEMALE = '1.1.3.8.0.0.0.0.0.0' # Canada, age 0, both sexes, Life expectancy
    # Inflation Coordinates
    INFLATION = '1.1.95.0.0.0.0.0.0.0' # Canada, CPI-Common measure of inflation
    # Investment Returns Coordinates
    BONDYIELDS_LOW_L = '1.13.0.0.0.0.0.0.0.0'
    BONDYIELDS_LOW_H = '1.14.0.0.0.0.0.0.0.0'
    BONDYIELDS_MED_L = '1.15.0.0.0.0.0.0.0.0'
    BONDYIELDS_MED_H = '1.16.0.0.0.0.0.0.0.0'
    BONDYIELDS_HIGH_L = '1.17.0.0.0.0.0.0.0.0'
    BONDYIELDS_HIGH_H = '1.18.0.0.0.0.0.0.0.0'
    
class HealthFactors:
    def __init__(self, smoking=False, obesity=False, chronic_conditions=0, physical_activity_level=2):
        """
        Initialize health factors that affect life expectancy
        
        smoking (bool): Whether the person smokes
        obesity (bool): Whether the person is obese (BMI > 30)
        chronic_conditions (int): Number of chronic health conditions
        physical_activity_level (int): 1-3 (1=low, 2=moderate, 3=high)
        
        """
        self.smoking = smoking
        self.obesity = obesity
        self.chronic_conditions = chronic_conditions
        self.physical_activity_level = min(max(physical_activity_level, 1), 3)
        
    def calculate_health_impact(self):
        '''Calculate the impact of health factors on life expectancy'''
        impact = 0
        
        # simplified values
        if self.smoking:
            impact -= 10  # Average reduction in life expectancy for smokers
        if self.obesity:
            impact -= 5   # Average reduction for obesity
        impact -= self.chronic_conditions * 2  # Each chronic condition reduces life expectancy
        
        # Physical activity benefit
        activity_benefit = {1: 0, 2: 2, 3: 4}  # Years added based on activity level
        impact += activity_benefit[self.physical_activity_level]
        
        return impact
    

'''
    GLOBAL FUNCTIONS
'''

def getJSONFromURL(url, pid, coordinate, period):
    payload = [{'productId': pid,
            'coordinate': coordinate,
            'latestN': period}]
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
    
    # call getDataFromVectorAndLatestNPeriods to get the amount of data points via metadata
    # POST insead of GET because we are sending data
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f'Error: {response.status_code}')
        print(response.text)
        return None
    

def get_bond_data(time: Time, days_back=7306): 
        dates_low = []
        values_low = []
        dates_high = []
        values_high = []
    
        low_data = None
        high_data = None
    
        if time == Time.SHORT:
            low_data = getJSONFromURL(STATCAN_URL, dataPIDs.BONDYIELDS.value, dataCoords.BONDYIELDS_LOW_L.value, days_back)
            high_data = getJSONFromURL(STATCAN_URL, dataPIDs.BONDYIELDS.value, dataCoords.BONDYIELDS_LOW_H.value, days_back)
        elif time == Time.MED:
            low_data = getJSONFromURL(STATCAN_URL, dataPIDs.BONDYIELDS.value, dataCoords.BONDYIELDS_MED_L.value, days_back)
            high_data = getJSONFromURL(STATCAN_URL, dataPIDs.BONDYIELDS.value, dataCoords.BONDYIELDS_MED_H.value, days_back)
        else:
            low_data = getJSONFromURL(STATCAN_URL, dataPIDs.BONDYIELDS.value, dataCoords.BONDYIELDS_HIGH_L.value, days_back)
            high_data = getJSONFromURL(STATCAN_URL, dataPIDs.BONDYIELDS.value, dataCoords.BONDYIELDS_HIGH_H.value, days_back)
    
        for vec in low_data[0]['object']['vectorDataPoint']:
            if vec['value'] is not None:
                date = vec['refPer']
                value = vec['value']
                numpy_date = datetime.strptime(date, '%Y-%m-%d')
                #  skip COVID
                if (2020 <= numpy_date.year <= 2022):
                    continue
                numpy_date = numpy_date.timestamp()
                dates_low.append(numpy_date)
                values_low.append(float(value))
            
        for vec in high_data[0]['object']['vectorDataPoint']:
            if vec['value'] is not None:
                date = vec['refPer']
                value = vec['value']
                numpy_date = datetime.strptime(date, '%Y-%m-%d')
                #  skip COVID
                if (2020 <= numpy_date.year <= 2022):
                    continue
                numpy_date = numpy_date.timestamp()
                dates_high.append(numpy_date)
                values_high.append(float(value))
        
        return dates_low, values_low, dates_high, values_high
    
def get_life_expectancy_data(gender: Gender, years_back=20):
    ''' Get life expectancy data for specified gender '''
    if gender == Gender.MALE:
        coord = dataCoords.LIFEEXP_MALE.value
    elif gender == Gender.FEMALE:
        coord = dataCoords.LIFEEXP_FEMALE.value
    else:
        coord = dataCoords.LIFEEXP_BOTH.value
        
    data = getJSONFromURL(STATCAN_URL, dataPIDs.LIFEEXP.value, coord, years_back)
    
    dates = []
    values = []
    
    for vec in data[0]['object']['vectorDataPoint']:
        date = vec['refPer']
        value = vec['value']
        numpy_date = datetime.strptime(date, '%Y-%m-%d').year
        dates.append(numpy_date)
        values.append(float(value))
        
    return dates, values

def get_inflation_data(months_back = 240): 
    data = getJSONFromURL(STATCAN_URL, dataPIDs.INFLATION.value, dataCoords.INFLATION.value, months_back)
    
    dates = []
    values = []
    for vec in data[0]['object']['vectorDataPoint']:
        if vec['value'] is not None:
            date = vec['refPer']
            value = vec['value']
            numpy_date = datetime.strptime(date, '%Y-%m-%d')
            #  skip COVID
            if (2020 <= numpy_date.year <= 2022):
                continue
            numpy_date = numpy_date.timestamp()
            dates.append(numpy_date)
            values.append(float(value))
        
    return dates, values
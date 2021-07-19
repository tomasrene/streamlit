import pandas as pd
import numpy as np
import markov
import shapley

class AttributionModel:
    def __init__(self, data, window=30, touchpoints=8):
        self.data = self.formatting(data)
        self.window = window
        self.touchpoints = touchpoints
    
    def markov(self, markov_order = 1):
        """
        Calculate conversions for each channel based on Markov chains and removal effect.

        Parameters
        ----------
        markov_order = int, default=1
            The order of Markov wanted to apply. Between 1 and 4 for computability reasons.

        Return
        ------
        attribution_markov: dataFrame
            dataFrame with channels as index and conversions attributed as column.

        """

        if markov_order not in [1,2,3,4]: # Validate markov order
            print("Invalid markov order")
            return

        attribution_markov = markov.main(self.data)

        return attribution_markov

    def shapley(self):
        """
        Calculate conversions for each channel based on Shapley value.

        Return
        ------
        attribution_markov: dataFrame
            dataFrame with channels as index and conversions attributed as column.
        """

        attribution_shapley = shapley.main(self.data) # Calculate Shapley value

        return attribution_shapley

    def formatting(self,data):
        '''
        Validates input, assigns column names and factorize user dimension.
        
        Parameters
        ----------
        data: dataFrame or list
            Touchpoint data ordered by time with user and channel dimensions and boolean conversion (in that order).

        Return
        ------
        data: dataFrame
            dataFrame with columns labeled.

        '''

        columns = ['user','channel','conversion']
        
        if isinstance(data,list):
            data = pd.DataFrame(data, columns=columns)
        if isinstance(data,pd.DataFrame):
            data.columns = columns
        else:
            print("Input data error, neither list nor dataFrame")
            
        data['user'] = pd.factorize(data['user'])[0] # Convert to numeric
        
        return data

data = pd.read_csv("../data_basic.csv")
test = AttributionModel(data)
print("\nShapley")
shapley = test.shapley()
print(shapley)
print("\nMarkov")
markov = test.markov()
print(markov)
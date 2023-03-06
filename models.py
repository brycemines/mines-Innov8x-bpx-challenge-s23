import random 
import pandas as pd 
import numpy as np
import statsmodels.api as sm

def model_random(df, t_pred):
    # free feel to use data earlier than df.timestamp.min()
    # however, your model SHOULD NOT USE ANY DATA AFTER "t_pred"
    # if hatch "open" should return integer 1
    # if hacth "close" should return integer 0    

    #implement this
    '''
    # Fit an ARIMA model to the time series data
    model = sm.tsa.ARIMA(time_series_data, order=(p, d, q))
    results = model.fit()

    # Perform a likelihood ratio test on the residual errors
    _, p_value, _, _ = sm.stats.diagnostic.het_goldfeldquandt(results.resid, results.model.exog)

    # If the p-value is less than the desired significance level, there is a changepoint
    if p_value < alpha:
    print("Changepoint detected")
    else:
    print("No changepoint detected")
    '''
    #p is the order of auto

    model = sm.tsa.ARIMA(df, order = (p, q, d))

    prob_open = random.random()

    return [random.choice([0, 1]), prob_open]

def model_ground_truth(df, t_pred):

    # manually created groud truth for time series, you may create your own groud truth label for a different time series
    # the model should classify hatch as "open" a couple of hours after the pressure drops, return integer 1
    # the model should classify hacth as "close" a couple of hours after the pressure rises, return integer 0    

    t_open = pd.to_datetime('2022-07-16 18:00:00')
    t_clos = pd.to_datetime('2022-08-26 00:00:00')

    if t_pred <= t_open or t_pred >= t_clos:
        status = 0
    else:
        status = 1
    
    
    return status


def search_for_open_hatch_random(df, facility_id):

    assert 'timestamp' in df
    

    num_of_open_hatch_events = random.choice([0, 1, 2]) # replace random choice with your model

    events = []
    if num_of_open_hatch_events>0:
        for i in range(num_of_open_hatch_events):
            open_hatch_event_seq = i + 1
            t_choices = random.choices(df.timestamp.unique(), k=2)

            # because it was random time from the random model, the hatch open time needs to happen between hatch close time, assuming the time series captured hatch open and close events
            t_hacth_open = min(t_choices) 
            t_hacth_clos = max(t_choices)
            prob_has_open_hatch_event = random.random()
            events.append([facility_id, num_of_open_hatch_events, open_hatch_event_seq, t_hacth_open, t_hacth_clos, prob_has_open_hatch_event])

    return events

def model_predict_open_hatch():
    # your model for challenge 2
    return 

def search_for_open_hatch():

    
    """
    # your model for challenge 3
    replace your own model here that searches whether a time series include open/close hatch events

    """

    return 
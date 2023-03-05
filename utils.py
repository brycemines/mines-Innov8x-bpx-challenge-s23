# utility library to keep main notebook or python file clean
# for each class or function, write detailed docstring for readability

from plotly.subplots import make_subplots
import plotly.express as px
import pandas as pd

def plot_ts_open_hatch(dfi=None, fac_id=None, t_drone_open_hatch=None, plot_dir=None):
    """ 
    plotting function to plot time series of one single facility
    dfi: pd.DataFrame with two columns, one is timestamp, one is pressure_osi
    t_drone_open_hatch: datetime or string in a format that could be converted to datetime
    fac_id: facility id
    fac_name: facility name
    plot_dir: directory to save the figure
    """ 
    assert isinstance(dfi, pd.DataFrame)
    assert 'timestamp' in dfi
    assert 'pressure_osi' in dfi

    fig = px.scatter(dfi, x='timestamp', y='pressure_osi')

    if t_drone_open_hatch is not None:
        assert pd.to_datetime(t_drone_open_hatch), 'needs to in a format convertable to datetime'
        t_drone_open_hatch = pd.to_datetime(t_drone_open_hatch)
        fig.add_traces(px.line(x=[t_drone_open_hatch, t_drone_open_hatch], y=[dfi.pressure_osi.min(), dfi.pressure_osi.max()], color_discrete_sequence=['red']).data)

    fig.update_layout(height=900, width=1600, title=f'Facility ID: {fac_id}, hatch open: {t_drone_open_hatch}', xaxis_title='DateTime', yaxis_title='Pressure, OSI', font=dict(size=18))

    if plot_dir is not None: fig.write_image(f'{plot_dir}/{fac_id}.png', engine='orca')
    
    return fig


def plot_prediction_validation(df, df_pred, facility_id):

    fig = make_subplots(rows=3, cols=1, shared_xaxes=True)

    # plot pressure with drone detected open hatch time
    fig_ts = plot_ts_open_hatch(dfi=df, fac_id=facility_id)

    fig.add_trace(fig_ts.data[0], row=1, col=1)

    # plot groud truth bar chart
    fig_truth = px.bar(df_pred, x='TimeStamp', y='Status_Truth')
    fig.add_trace(fig_truth.data[0], row=2, col=1)

    # plot model results bar chart
    fig_pred = px.bar(df_pred, x='TimeStamp', y='Status_Predicted')
    fig.add_trace(fig_pred.data[0], row=3, col=1)

    fig.update_xaxes(title_text='TimeStamp', row=3, col=1)
    fig.update_yaxes(title_text = 'Tank Header Pressure', row=1, col=1)
    fig.update_yaxes(title_text = 'Status: Ground Truth', row=2, col=1)
    fig.update_yaxes(title_text = 'Status: Model Prediction', row=3, col=1)

    fig.update_layout(title_text= f'Model predicted hatch status vs groud truth {facility_id}', height=900, width=1600, font=dict(size=16))

    return fig


from datetime import timedelta

def summary(drone = None, form = None, thp = None, workorder = None, id = None):
    #we need to make the in-range thp data and get the drone detection time

    # sort time series data by facility id
    df_thp_facility = thp[thp.FACILITY_ID==id]

    # sort drone data by facility id
    df_drone_facility = drone[drone.FACILITY_ID==id]

    # sort workorder data by facility id
    df_workorder_facility = workorder[workorder.facility_id == id]

    # sort form data by facility id
    df_form_facility = form[form.FACILITY_ID==id]
    df_form_facility.SubmitDate = pd.to_datetime(df_form_facility.SubmitDate)

    arr_thp_at_drone = {}
    temp = []
    for i in range(df_drone_facility.DTM.nunique()):
        df_drone_facility.iloc[i]
        t_drone_open_hatch = df_drone_facility.DTM.iloc[i] # in this case, only one open hatch event detected for this facility
        t_drone_open_hatch = pd.to_datetime(t_drone_open_hatch)

        t_strt = t_drone_open_hatch - timedelta(days=30)
        t_stop = t_drone_open_hatch + timedelta(days=30)

        t_df_thp = df_thp_facility[df_thp_facility.timestamp.between(t_strt, t_stop)]
        if not t_df_thp.empty:
            temp.append(t_df_thp)

        # get work order data for facility

        # filter rows containing key word 'hatch', keyword could be 'thief' or misspelled words
        df_workorder_facility = df_workorder_facility[(df_workorder_facility.workOrderDescription.fillna('').str.lower().str.contains('hatch'))
                        | ((df_workorder_facility.workOrderResolutionDescription.fillna('').str.lower().str.contains('hatch')))
        ]

        # filter rows with dates within drone detected open hatch date
        df_workorder_facility.created_date = pd.to_datetime(df_workorder_facility.created_date)
        df_workorder_facility.workOrderActualsStartDate = pd.to_datetime(df_workorder_facility.workOrderActualsStartDate)
        df_workorder_facility.workOrderActualsEndDate = pd.to_datetime(df_workorder_facility.workOrderActualsEndDate)

        df_workorder_facility = df_workorder_facility[
            df_workorder_facility.created_date.between(t_strt, t_stop)
            | df_workorder_facility.workOrderActualsStartDate.between(t_strt, t_stop)
            | df_workorder_facility.workOrderActualsEndDate.between(t_strt, t_stop)
        ]
        temp.append(df_workorder_facility)

        df_form_facility = df_form_facility[df_drone_facility.SubmitDate.between(t_strt, t_stop)]
        temp.append(df_drone_facility)

        arr_thp_at_drone[t_drone_open_hatch] = temp
        temp = []

    if len(arr_thp_at_drone) == 0:
        return (id, 'invalid')
    
    return arr_thp_at_drone
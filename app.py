from statsmodels.tsa.seasonal import seasonal_decompose
import streamlit as st
from PIL import Image
import pandas as pd
from datetime import datetime
from PIL import Image
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.graph_objs as go
from plotly import subplots
import plotly.express as px

plotly_config = {
    'displaylogo': False
}

#Logo
logo = './static/logo-Porsche.png'
favicon = './static/porsche.ico'

def plot_seasonal_decomposition(result):
    trace1 = go.Scatter(
        x=result.observed.index,
        y=result.observed
    )

    trace2 = go.Scatter(
        x=result.trend.index,
        y=result.trend,
        xaxis='x2',
        yaxis='y2'
    )

    trace3 = go.Scatter(
        x=result.seasonal.index,
        y=result.seasonal,
        xaxis='x3',
        yaxis='y3'
    )

    trace4 = go.Scatter(
        x=result.resid.index,
        y=result.resid,
        xaxis='x4',
        yaxis='y4'
    )


    fig = subplots.make_subplots(
        rows=4,
        cols=1,
        print_grid=False
    )

    fig.append_trace(trace1, 1, 1)
    fig.append_trace(trace2, 2, 1)
    fig.append_trace(trace3, 3, 1)
    fig.append_trace(trace4, 4, 1)

    fig['layout'].update(
        showlegend=False,
        height=600,
        yaxis=dict(title="Observed"),
        yaxis2=dict(title="Trend"),
        yaxis3=dict(title="Seasonal"),
        yaxis4=dict(title="Residual"),
        xaxis4=dict(title="Month")
    )
    return fig


def display_line_plot(final_df):
    
    ''' Function to display Line Chart '''

    sns.set(rc={'figure.figsize':(15, 5)})
    ax = sns.lineplot(x='Period', y='Cars_Sold', data=final_df.reset_index(), marker='o', hue='Forecast_Model')
    ax.set(title='Porsche Sales Forecasting')

    # label points on the plot
    for x, y in zip(final_df['Period'], final_df['Cars_Sold']):
         plt.text(x = x, # x-coordinate position of data label
         y = y, # y-coordinate position of data label, adjusted to be 150 below the data point
         s = '{:.0f}'.format(y), # data label, formatted to ignore decimals
         color = 'black') # set colour of line

    return

def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def streamlit_interface(df_history, df_forecast, dmd_history, model_info):
    
    """
      Function for Streamlit Interface
    """
    # Switch Off Warning
    st.set_option('deprecation.showPyplotGlobalUse', False)


    # Page Setup
    st.set_page_config(
    page_title="Porsche Sales Forecasting",
    page_icon=favicon,
    layout="centered",
    initial_sidebar_state="auto")  

    # Load CSS
    local_css("./static/style.css")

    # Remove Made With Streamlit Footer
    st.markdown('<style> #MainMenu {visibility: hidden;} footer {visibility: hidden;}</style>',
                unsafe_allow_html=True)

    # Load  Logo
    st.image('./static/porsche.png', width = 100)

    # Load Application Name
    st.title('Porsche Sales Forecasting')

    # Increase widrh of sidebar
    st.markdown(
                """
                <style>
                [data-testid="stSidebar"][aria-expanded="true"] > div:first-child {
                    width: 500px;
                }
                [data-testid="stSidebar"][aria-expanded="false"] > div:first-child {
                    width: 500px;
                    margin-left: -500px;
                }
                </style>
                """,
                unsafe_allow_html=True,
                )   

    # Foreacasing Option
    fcst_option = st.selectbox('Select Forecasting Criteria',('Porsche_All_Models', 'Porsche_Panamera', 'Porsche_Cayenne', 'Porsche_Boxster', 'Porsche_Macan', 'Porsche_Taycan'))

    st.write('Select three known variables:')
    option_1 = st.checkbox('Facebook_Prophet')
    option_2 = st.checkbox('ARIMA')
    option_3 = st.checkbox('Moving_Average(3 Months)')

    if st.button('Forecast') :
        if (option_1 == False and option_2 == False and option_3 == False):
            st.error('Please Select an Algorithm!')
        else:
            final_df = df_history[df_history.Model == fcst_option]
            just_fcst = pd.DataFrame()

            if option_1:
                reqd_fsct_df = df_forecast[(df_forecast.Model== fcst_option) & (df_forecast.Forecast_Model== 'FaceBook_Prophet')]
                final_df = final_df.append(reqd_fsct_df)
                just_fcst = just_fcst.append(reqd_fsct_df)
            
            if option_2:
                reqd_fsct_df = df_forecast[(df_forecast.Model== fcst_option) & (df_forecast.Forecast_Model== 'ARIMA')]
                final_df = final_df.append(reqd_fsct_df)
                just_fcst = just_fcst.append(reqd_fsct_df)

            if option_3:
                reqd_fsct_df = df_forecast[(df_forecast.Model== fcst_option) & (df_forecast.Forecast_Model== 'Moving_Average')]
                final_df = final_df.append(reqd_fsct_df)
                just_fcst = just_fcst.append(reqd_fsct_df)

            st.header('Sales Forecast')
            st.pyplot(display_line_plot(final_df))
            
            just_fcst['Period'] = pd.to_datetime(just_fcst['Period']).dt.tz_localize(None)
            just_fcst['Period'] = just_fcst['Period'].astype(str)
            st.write(just_fcst)

            
            st.header('Best Forecast Model:')
            if fcst_option == 'Porsche_All_Models':
                st.write('ARIMA (0, 0, 2)')
            else:
                st.write('ARIMA (1, 0, 0)')    

            st.sidebar.header('Demand History')
            st.sidebar.write(dmd_history[dmd_history.Model == fcst_option].transpose())

            if option_2:
                st.sidebar.header('Model Information(ARIMA)')
                st.sidebar.write(model_info[model_info.Model == fcst_option].transpose())
            
            st.header('Sales History Decomposition')
            result_add = seasonal_decompose(df_history['Cars_Sold'], model='additive', period=12)
            st.plotly_chart(plot_seasonal_decomposition(result_add), config=plotly_config)

            

if __name__ == "__main__":
    
    # # Optum Data
    df_history  = pd.read_excel('./data/Porsche_Demand_Forecasting.xlsx', sheet_name='Sales_History')
    df_forecast = pd.read_excel('./data/Porsche_Demand_Forecasting.xlsx', sheet_name='Sales_Forecast')
    dmd_history = pd.read_excel('./data/Porsche_Demand_Forecasting.xlsx', sheet_name='Demand_History')
    model_info  = pd.read_excel('./data/Porsche_Demand_Forecasting.xlsx', sheet_name ='Model_Info')
    streamlit_interface(df_history, df_forecast, dmd_history, model_info)
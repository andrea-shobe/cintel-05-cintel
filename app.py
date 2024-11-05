from shiny import reactive, render
from shiny.express import ui
import random
from datetime import datetime
from collections import deque
import pandas as pd
import plotly.express as px
from shinywidgets import render_plotly
from scipy import stats

# https://fontawesome.com/v4/cheatsheet/
from faicons import icon_svg

UPDATE_INTERVAL_SECS: int = 3

DEQUE_SIZE: int = 5
reactive_value_wrapper = reactive.value(deque(maxlen=DEQUE_SIZE))

@reactive.calc()
def reactive_calc_combined():
    # Invalidate this calculation every UPDATE_INTERVAL_SECS to trigger updates
    reactive.invalidate_later(UPDATE_INTERVAL_SECS)

    # Data generation logic
    temp_value = round(random.uniform(-18, -16), 1)
    timestamp_value = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_date_time = {"temp":temp_value, "timestamp":timestamp_value}

    # get the deque and append the new entry
    reactive_value_wrapper.get().append(new_date_time)

    # Get a snapshot of the current deque for any further processing
    deque_snapshot = reactive_value_wrapper.get()

    # For Display: Convert deque to DataFrame for display
    df = pd.DataFrame(deque_snapshot)

    # For Display: Get the latest dictionary entry
    latest_dictionary_entry = new_date_time

    # Return a tuple with everything we need
    # Every time we call this function, we'll get all these values
    return deque_snapshot, df, latest_dictionary_entry




#TITLE-------------------------------------------------------------------------------------------
ui.page_opts(title="Weather Aware:  Your Live Updates", fillable=True)

#SIDEBAR----------------------------------------------------------------------------------------
with ui.sidebar(open="open"):
    

    ui.h1("Antarctic Explorer", class_="text-center")
    ui.p("A demonstration of real-time temperature readings in Antarctica.",
        class_="text-center",)
    ui.hr()
    ui.h6("Links:")
    ui.a(
        "GitHub Source",
        href="https://github.com/andrea-shobe/cintel-05-cintel",
        target="_blank",)
    ui.a("GitHub App",href="https://github.com/andrea-shobe/cintel-05-cintel/blob/main/app.py",
        target="_blank",)
    ui.a("PyShiny", href="https://shiny.posit.co/py/", target="_blank")
    ui.a("PyShiny Express",href="hhttps://shiny.posit.co/blog/posts/shiny-express/",
        target="_blank",)

#MAIN PANEL--------------------------------------------------------------------------------------------

#Coumns 1 with Current temp and live temperature readings-----------------------------------
with ui.layout_columns():
    #CURRENT TEMPERATURE------------------------------------------------------------------------------
    with ui.value_box(
        showcase=icon_svg("snowflake"),
        theme="bg-gradient-pink-blue",height=50):
        "Current Temperature"
        @render.text
        def display_temp():
            """Get the latest reading and return a temperature string"""
            deque_snapshot, df, latest_dictionary_entry = reactive_calc_combined()
            return f"{latest_dictionary_entry['temp']} C"

        "Colder Than Usual"

    

  
    #CURRENT DATE AND TIME-----------------------------------------------------------------------------
    with ui.value_box(
        showcase=icon_svg("clock"),
        theme="bg-gradient-blue-purple",height=50):
        "Current Date and Time"

        @render.text
        def display_time():
            """Get the latest reading and return a timestamp string"""
            deque_snapshot, df, latest_dictionary_entry = reactive_calc_combined()
            return f"{latest_dictionary_entry['timestamp']}"

#NAVCARD----------------------------
with ui.navset_card_tab(id="tab"):
    with ui.nav_panel("Live Temperature Readings"):
        @render.data_frame
        def display_df():
            """Get the latest reading and return a dataframe with current readings"""
            deque_snapshot, df, latest_dictionary_entry = reactive_calc_combined()
            pd.set_option('display.width', None)        # Use maximum width
            return render.DataGrid( df,width="100%", height=400)

    with ui.nav_panel("Current Chart with Trend"):
        @render_plotly
        def display_plot():
            # Fetch from the reactive calc function
            deque_snapshot, df, latest_dictionary_entry = reactive_calc_combined()

            # Ensure the DataFrame is not empty before plotting
            if not df.empty:
                # Convert the 'timestamp' column to datetime for better plotting
                df["timestamp"] = pd.to_datetime(df["timestamp"])

        
            fig = px.scatter(df,
            x="timestamp",
            y="temp",
            title="Temperature Readings with Regression Line",
            labels={"temp": "Temperature (°C)", "timestamp": "Time"},
            color_discrete_sequence=["orange"] )
            
          

            # For x let's generate a sequence of integers from 0 to len(df)
            sequence = range(len(df))
            x_vals = list(sequence)
            y_vals = df["temp"]

            slope, intercept, r_value, p_value, std_err = stats.linregress(x_vals, y_vals)
            df['best_fit_line'] = [slope * x + intercept for x in x_vals]

            # Add the regression line to the figure
            fig.add_scatter(x=df["timestamp"], y=df['best_fit_line'], mode='lines', name='Regression Line')

            #update layout as neeted to customize further
            fig.update_layout(xaxis_title="Time", yaxis_title="Temperature (°C)")
            fig.update_layout(height=300)
    
            return fig
        



    

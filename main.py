from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home():
    from pandas_datareader import data
    import datetime
    from bokeh.plotting import figure, show, output_file
    from bokeh.models import Range1d
    from bokeh.embed import components
    from bokeh.resources import CDN

    #Establishing dates for usage
    #NOTE: The earliest data available through pandas_datareader is from 1970 - 1 - 1
    start = datetime.datetime(1970, 1, 1)
    present = datetime.date.today()

    #Acquiring stock data from Yahoo Finance for Scotiabank
    dataF = data.DataReader("BNS.TO", "yahoo", start, present)

    #Adding column indicating increase or decrease
    def incOrDec(closing, opening):
        stock = ""
        if opening < closing:
            stock = "Increase"
        elif closing < opening:
            stock = "Decrease"
        else:
            stock = "Equal"
        return stock

    dataF["Status"] = [incOrDec(closing, opening) for closing, opening in zip(dataF.Close, dataF.Open)]
    dataF["Mid"] = (dataF.Open + dataF.Close) / 2
    dataF["Height"] = abs(dataF.Close - dataF.Open)

    #Converting 12 hours to ms
    hours = 12 * 60 * 60 * 1000 

    #Initializing Bokeh chart
    plot = figure(x_axis_type = "datetime", width = 1800, height = 600, x_axis_label = "Date",
    y_axis_label = "Stock Value", sizing_mode = "scale_width")
    plot.grid.grid_line_alpha = 0.3
    plot.title.text_font_size = '15pt'
    plot.xaxis.axis_label_text_font_size = "12pt"
    plot.yaxis.axis_label_text_font_size = "12pt"
    plot.title.text = "Scotiabank Stocks Candlestick Chart"

    #Finding the last day of any month
    date = datetime.datetime(dataF.index[-1].year, dataF.index[-1].month, 1)
    next_month = date.replace(day = 28) + datetime.timedelta(days = 4)
    lastDayOfMonth = next_month - datetime.timedelta(days = next_month.day)

    #Finding range of stock data for the month
    year = str(dataF.index[-1].year)
    month = str(dataF.index[-1].month)

    rngLow = dataF.loc[f"{year}-{month}-1" : f"{year}-{month}-{lastDayOfMonth.day}", "Low"]
    rngHigh = dataF.loc[f"{year}-{month}-1" : f"{year}-{month}-{lastDayOfMonth.day}", "High"]

    #Starting graph at first day of latest month to last day of month
    plot.y_range = Range1d(min(rngLow) - 0.1, max(rngHigh) + 0.1)
    plot.x_range = Range1d(datetime.datetime(dataF.index[-1].year, dataF.index[-1].month, 1), 
    datetime.datetime(dataF.index[-1].year, dataF.index[-1].month, lastDayOfMonth.day))

    #Stock high and low line plot
    plot.segment(dataF.index, dataF.High, dataF.index, dataF.Low, color = "black")

    #Stock rises plot
    plot.rect(x = dataF.index[dataF.Status == "Increase"], y = dataF.Mid[dataF.Status == "Increase"], width = hours, 
    height = dataF.Height[dataF.Status == "Increase"], color = "#19c902")

    #Stock falls plot
    plot.rect(x = dataF.index[dataF.Status == "Decrease"], y = dataF.Mid[dataF.Status == "Decrease"], width = hours, 
    height = dataF.Height[dataF.Status == "Decrease"], color = "#db3125")

    #Stock equal plot
    plot.rect(x = dataF.index[dataF.Status == "Equal"], y = dataF.Mid[dataF.Status == "Equal"], width = hours, 
    height = dataF.Height[dataF.Status == "Equal"], color = "black")

    script, div = components(plot)
    cdnJS = CDN.js_files[0]

    return render_template("home.html", script = script, div = div, cdnJS = cdnJS)
if (__name__ == "__main__"):
    app.run(debug = True)
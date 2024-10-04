import yfinance as yf
import chainlit as cl
import plotly

query_stock_price_def = {
    "name": "query_stock_price",
    "description": "Queries the latest stock price information for a given stock symbol.",
    "parameters": {
      "type": "object",
      "properties": {
        "symbol": {
          "type": "string",
          "description": "The stock symbol to query (e.g., 'AAPL' for Apple Inc.)"
        },
        "period": {
          "type": "string",
          "description": "The time period for which to retrieve stock data (e.g., '1d' for one day, '1mo' for one month)"
        }
      },
      "required": ["symbol", "period"]
    }
}

async def query_stock_price_handler(symbol, period):
    """
    Queries the latest stock price information for a given stock symbol.
    """
    try:
        stock = yf.Ticker(symbol)
        hist = stock.history(period=period)
        if hist.empty:
            return {"error": "No data found for the given symbol."}
        return hist.to_json()
 
    except Exception as e:
        return {"error": str(e)}

query_stock_price = (query_stock_price_def, query_stock_price_handler)

draw_plotly_chart_def = {
    "name": "draw_plotly_chart",
    "description": "Draws a Plotly chart based on the provided JSON figure and displays it with an accompanying message.",
    "parameters": {
      "type": "object",
      "properties": {
        "message": {
          "type": "string",
          "description": "The message to display alongside the chart"
        },
        "plotly_json_fig": {
          "type": "string",
          "description": "A JSON string representing the Plotly figure to be drawn"
        }
      },
      "required": ["message", "plotly_json_fig"]
    }
}

async def draw_plotly_chart_handler(message: str, plotly_json_fig):
    fig = plotly.io.from_json(plotly_json_fig)
    elements = [cl.Plotly(name="chart", figure=fig, display="inline")]

    await cl.Message(content=message, elements=elements).send()
    
draw_plotly_chart = (draw_plotly_chart_def, draw_plotly_chart_handler)


tools = [query_stock_price, draw_plotly_chart]
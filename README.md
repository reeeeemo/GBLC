# GBLC (Government Life Bond Calculator)
GBLC is a simple web application (accessed in the About section, or [here](https://gblc.vercel.app/) that calculates your total (inflation-adjusted) return when investing in Canadian government bonds.

GBLC also shows you a graph of the **predicted short, medium, and long term rates**. It also shows the best rate to **increase your return**.

# How does this app work?
It takes your gender (optional), age, and initial investment and calculates (based on 20 past years of data):
- Predicted life expectancy (via Polynomial Regression)
- Predicted rate of return for short, medium, and long term bond rates (via a Targeted Monte-Carlo simulation)
- Predicted inflation (via Targeted Monte-Carlo simulation)

All of this data used to predict is gathered with API requests to [Statistics Canada](https://www.statcan.gc.ca/en/start)


This app then tracks the route that would make you the most money, and gives you the final, inflation adjusted return, as well as a graph of the route you would take.

**PLEASE DO NOT USE OR APPLY THIS DATA IN REAL-LIFE SCENARIOS, IT WAS MADE FOR THE PURPOSES OF SHOWING OFF PROGRAMMING KNOWLEDGE**
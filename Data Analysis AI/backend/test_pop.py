import pandas as pd
from main import populate_chart_data

df = pd.DataFrame({"rating": [4.5, 4.0, 3.5], "pages": [300, 250, 400]})

config = {
    "chartType": "ScatterChart",
    "data": [
        ["rating", "pages"],
        ["$rating", "$pages"]
    ]
}

try:
    res = populate_chart_data(config, df)
    print("SUCCESS:")
    print(res)
except Exception as e:
    import traceback
    traceback.print_exc()

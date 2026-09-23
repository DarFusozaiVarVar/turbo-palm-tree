import numpy as np
import pandas as pd

#Create the series 
s = pd.Series([1, 5, 3, np.nan, 6, 8])

#Create DataFrame
f = pd.DataFrame([1, 0], [0, 1])

#Create DataFrame with named columns
dates = pd.date_range("20130101", periods=6)
f = pd.DataFrame(np.random.randn(6, 4), index=dates, columns=list("ABCD"))
print(f)
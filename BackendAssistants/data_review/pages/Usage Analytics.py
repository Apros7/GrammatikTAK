import json
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter
from datetime import datetime, timedelta
from matplotlib.ticker import MaxNLocator

st.header("All text processed on the backend:")

with open("/Users/lucasvilsen/Desktop/GrammatikTAK/BackendAssistants/datastore/Backend-alltext.json", "r") as json_file:
    alltext = json.load(json_file)

df_alltext = pd.DataFrame(alltext)
st.dataframe(df_alltext)

st.header("Usage Analytics")
all_times = df_alltext["time"].to_list()
counts = Counter([time[:10] for time in all_times if time != "unknown"])
times = list(counts.keys())
values = list(counts.values())

date_format = '%Y-%m-%d'
times = [datetime.strptime(date, date_format) for date in times]

min_date = min(times)
max_date = max(times)

all_dates = [min_date + timedelta(days=i) for i in range((max_date - min_date).days + 1)]
all_dates = [date.strftime(date_format) for date in all_dates]

expanded_times = all_dates
expanded_values = [values[times.index(date)] if date in times else 0 for date in all_dates]

fig, ax = plt.subplots(figsize=(10, 6))
ax.bar(times, values)
ax.yaxis.set_major_locator(MaxNLocator(integer=True))

plt.xticks(rotation=20)
plt.xlabel('Date')
plt.ylabel('Occurrences')
plt.tight_layout()

st.pyplot(fig)
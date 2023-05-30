import time
import json
import matplotlib as plt
import os
from collections import Counter
from datetime import datetime

os.chdir("/Users/lucasvilsen/Desktop/GrammatikTAK/")
data = json.load(open("BackendAssistants/data_review_site/datastore/Backend-alltext.json"))
timestamps = [data[i]["time"] for i in range(len(data))]
true_timestamps = [timestamp for timestamp in timestamps if timestamp != "unknown"]

dates = [timestamp[:8] for timestamp in true_timestamps]
date_counts = Counter(dates)
sorted_dates, counts = zip(*sorted(date_counts.items()))

plt.plot(sorted_dates, counts, marker='o')
plt.xlabel('Date')
plt.ylabel('Number of Users')
plt.title('Number of Users per Day')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
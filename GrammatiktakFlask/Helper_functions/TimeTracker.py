import time

class TimeTracker():
    def __init__(self):
        self.time = time.time()
        self.time2 = time.time()
        self.time_dict = {}
        self.time_dict2 = {}
        self.excess_time = {}
        self.excess_index = 1
    
    def track(self, key):
        if key in self.time_dict.keys():
            self.time_dict[key] += time.time()-self.time
        else:
            self.time_dict[key] = time.time()-self.time
        self.time = time.time()
    
    def track2(self, key):
        if key in self.time_dict2.keys():
            self.time_dict2[key] += time.time()-self.time2
        else:
            self.time_dict2[key] = time.time()-self.time2
        self.time2 = time.time()

    def __call__(self, bound=.5):
        time_taken = ["HIGH" if value > bound else "LOW " for value in self.time_dict.values()]
        print(*zip(time_taken, [item for item in self.time_dict.items()]), sep="\n")
        print("Full Function", *[item for item in self.time_dict2.items()], sep="\n")
        print("Excess time:", *[item for item in self.excess_time.items()], sep="\n")
    
    def complete_reset(self):
        self.time = time.time()
        self.time2 = time.time()

    def reset(self, string=None):
        self.excess_time[f"reset{self.excess_index}({string})"] = time.time()-self.time
        self.excess_index += 1
        self.time = time.time()
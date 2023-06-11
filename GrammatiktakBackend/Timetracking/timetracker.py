import time

# this is used to track time of different functions in a script

def check_inactive(func):
    def wrapper(self, *args, **kwargs):
        if self.inactive:
            return
        return func(self, *args, **kwargs)
    return wrapper

class TimeTracker():
    def __init__(self):
        self.time = time.time()
        self.time2 = time.time()
        self.time_dict = {}
        self.time_dict2 = {}
        self.excess_time = {}
        self.excess_index = 1
        self.inactive = False

    # there are two tracks that can run at the same time
    # this is used to track time of different functions in a script
    # call .track("key for naming the function to track")
    @check_inactive
    def track(self, key):
        if key in self.time_dict.keys():
            self.time_dict[key] += time.time()-self.time
        else:
            self.time_dict[key] = time.time()-self.time
        self.time = time.time()
    
    @check_inactive
    def track2(self, key):
        if key in self.time_dict2.keys():
            self.time_dict2[key] += time.time()-self.time2
        else:
            self.time_dict2[key] = time.time()-self.time2
        self.time2 = time.time()

    # will print information on call
    # bound can be specified to determine when a time is considered high
    @check_inactive
    def __call__(self, bound=.5):
        time_taken = ["HIGH" if value > bound else "LOW " for value in self.time_dict.values()]
        print(*[f"{bound}: Took {round(time, 5)} \t sec for {module}." for bound, (module, time) in zip(time_taken, [item for item in self.time_dict.items()])], sep="\n")
        print("Full Function", *[item for item in self.time_dict2.items()], sep="\n")
        print("Excess time:", *[item for item in self.excess_time.items()], sep="\n")
    
    # reset the time tracker without keeping count of missed time
    @check_inactive
    def complete_reset(self):
        self.time = time.time()
        self.time2 = time.time()

    # reset the time tracker and keep count of missed time. Reason can be specified
    @check_inactive
    def reset(self, string=None):
        self.excess_time[f"reset{self.excess_index}({string})"] = time.time()-self.time
        self.excess_index += 1
        self.time = time.time()
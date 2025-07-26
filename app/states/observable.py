from collections import defaultdict

class Observable:
    def __init__(self):
        self._observers = defaultdict(list)

    def add_observer(self, target, observer_callback):
        if observer_callback not in self._observers[target]:
            self._observers[target].append(observer_callback)
    
    def remove_observer(self, target, observer_callback):
        if observer_callback in self._observers[target]:
            self._observers[target].remove(observer_callback)

    def notify_observers(self, target):
        for observer in self._observers[target]:
            observer() # Pass the new value to the observer
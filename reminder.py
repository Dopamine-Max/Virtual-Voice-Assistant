import winsound
from win10toast import ToastNotifier

def timer (reminder, seconds):
    notificator = ToastNotifier()
    notificator.show_toast("Reminder", f"Alarm will go off in {seconds} Seconds.",duration= seconds)
    notificator.show_toast("Reminder", reminder)
    
    #alarm
    frequency=2500
    duration=1000
    winsound.Beep (frequency, duration)

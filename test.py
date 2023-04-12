import schedule
import datetime
import time

def my_event():
    print("Событие сработало!")
 # Установка времени срабатывания события
event_time = datetime.time(2, 41, 0)
 # Установка функции, которая будет вызываться при срабатывании события
schedule.every().day.at(str(event_time)).do(my_event)
 # Бесконечный цикл, который будет проверять, сработало ли событие
while True:
    schedule.run_pending()
    time.sleep(1)
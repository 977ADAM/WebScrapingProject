import schedule
import time
import datetime
import os

def your_task():
    print(f"✅ Задача выполнена в {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    os.system("python demo.py")
    print("Выполняю полезную работу...")

# Запускать каждую минуту
schedule.every(1).minutes.do(your_task)

# Запустить сразу при старте
print(f"🚀 Скрипт запущен в {datetime.datetime.now().strftime('%H:%M:%S')}")
your_task()

print("⏰ Ожидание выполнения каждую минуту...")
print("Нажмите Ctrl+C для остановки")

try:
    while True:
        schedule.run_pending()
        time.sleep(1)
except KeyboardInterrupt:
    print("\n🛑 Скрипт остановлен")
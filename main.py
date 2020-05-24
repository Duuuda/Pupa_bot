import os
import signal

from Vk_bot import Bot


def process_lock():
    if os.path.exists("bot.pid"):
        with open("bot.pid", "r+") as file:
            running_pid = file.read()

            if running_pid.isdigit():
                running_pid = int(running_pid)

                try:
                    os.kill(running_pid, signal.SIGTERM)
                except OSError:
                    pass

            file.seek(0)
            file.truncate()

            file.write(str(os.getpid()))
    else:
        with open("bot.pid", "w") as file:
            file.write(str(os.getpid()))


def main():
    process_lock()

    if os.path.exists("block.pid"):
        print("Запуск прерван из-за блокировки")
        return

    with open('bot.setting', 'r', encoding='UTF-8') as file:
        data = file.read()

    data = data.split('\n')

    Bot(data[0], data[1], data[2])


if __name__ == "__main__":
    main()

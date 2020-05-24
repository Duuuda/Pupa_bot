import os
import signal


def restart():
    if os.path.exists("block.pid"):
        os.remove("block.pid")

    if os.path.exists("bot.pid"):
        with open("bot.pid", "r") as file:
            pid = file.read()

            if pid.isdigit():
                pid = int(pid)

                try:
                    os.kill(pid, signal.SIGTERM)
                except OSError:
                    pass

        os.remove("bot.pid")


if __name__ == "__main__":
    restart()

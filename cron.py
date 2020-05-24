import os
import main


if os.path.exists("bot.pid"):
    with open("bot.pid", "r") as file:
        running_pid = file.read()

        if running_pid.isdigit():
            running_pid = int(running_pid)

            try:
                os.kill(running_pid, 0)
            except OSError:
                main.main()

        else:
            main.main()
else:
    main.main()

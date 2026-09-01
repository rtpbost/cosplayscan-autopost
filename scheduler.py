import os
import time
from datetime import datetime
from zoneinfo import ZoneInfo

TIMEZONE = os.getenv(
    "TIMEZONE",
    "Asia/Jakarta"
)

POST_TIMES = os.getenv(
    "POST_TIMES",
    "08:00,16:00,00:00"
)

CHECK_INTERVAL = 20


def get_schedule():
    return {
        value.strip()
        for value in POST_TIMES.split(",")
        if value.strip()
    }


def run_scheduler(job):
    timezone = ZoneInfo(TIMEZONE)
    schedule = get_schedule()

    print("Scheduler aktif")
    print("Timezone :", TIMEZONE)
    print("Jadwal   :", sorted(schedule))

    last_run_key = None

    while True:
        now = datetime.now(timezone)

        current_time = now.strftime("%H:%M")
        current_date = now.strftime("%Y-%m-%d")

        run_key = f"{current_date}-{current_time}"

        if (
            current_time in schedule
            and run_key != last_run_key
        ):
            print(
                f"\n[{now.isoformat()}] "
                f"Waktunya posting."
            )

            try:
                job()
            except Exception as error:
                print(
                    "POSTING ERROR:",
                    repr(error)
                )

            last_run_key = run_key

        time.sleep(CHECK_INTERVAL)

import os
import threading
import schedule
import time
# from .sync import fallback_to_default



def scheduler_fallback_to_default():
    from .sync import fallback_to_default
    # schedule.every(60).seconds.do(fallback_to_default)
    while True:
        schedule.run_pending()
        time.sleep(1)

# Ensure the scheduler only starts in the main process
if os.environ.get("RUN_MAIN") == "true":
    thread = threading.Thread(target=scheduler_fallback_to_default, daemon=True)
    thread.start()


def run_scheduler():
    from .sync import sync_databases
    # schedule.every(120).seconds.do(sync_databases)
    while True:
        schedule.run_pending()
        time.sleep(1)

# Ensure the scheduler only starts in the main process
if os.environ.get("RUN_MAIN") == "true":
    thread = threading.Thread(target=run_scheduler, daemon=True)
    thread.start()
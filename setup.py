import os
import platform
import shutil
import subprocess
import time
import zipfile
from datetime import datetime
from threading import Thread

import sqlbullshit

filepath = os.path.abspath(os.path.dirname(__file__))


day = 60 * 60 * 24

std = ""


def in_wsl() -> bool:
    if os.name == "nt":
        return False
    else:
        return "microsoft-standard" in platform.uname().release


def updatedb(added: str):
    sql = sqlbullshit.sql(f"{filepath}/data.db", "user")
    collums = sql.collums()
    if added not in collums:
        sql.addcollum(added, "TEXT")


def compresslogs():
    """Find all logs in the /commandlogs directory more than 3 days old and use subprocess.run(["zpaq", "add", f"./{t}.zpaq", f"./{t}.zip"],
    stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT) on it"""
    while True:
        if in_wsl() is False:
            dt = datetime.now()
            t = dt.strftime("%d-%b-%y_%H-%M-%S")
            # Get a list of all the logs in the /commandlogs directory
            logs = os.listdir(f"{filepath}/commandlogs")
            # For each log in the logs directory
            for log in logs:
                # If the log is more than 3 days old
                if (
                    os.path.getmtime(f"{filepath}/commandlogs/{log}")
                    < time.time() - 3 * day
                ):
                    # If the log is already paqed, leave it
                    if log.endswith(".zpaq"):
                        continue
                    # ZPAQ it with subprocess
                    subprocess.run(
                        ["zpaq", "add", f"./{log}.zpaq", f"./{log}"],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.STDOUT,
                    )
                    # Move the file to the backups folder
                    shutil.move(
                        f"{filepath}/{t}.zpaq", fr"/{filepath}/commandlogs/{t}.zpaq"
                    )
        time.sleep(day / 2)


def backup():
    # Run the backup loop only if we are on linux
    isbeta = in_wsl()
    if isbeta is False:
        while True:
            # Read the database file as binary
            with open(f"{filepath}/data.db", "rb") as db:
                # Save the raw datetime
                dt = datetime.now()
                # Convert it into something we can read
                t = dt.strftime("%d-%b-%y_%H-%M-%S")
                # Convert the copied db to a zip file
                with zipfile.ZipFile(fr"{filepath}/{t}.zip", mode="x") as archive:
                    archive.writestr(f"{t}.db", db.read())
                # Attempt to compress the zip file with ZPAQ
                try:
                    # ZPAQ it with subprocess
                    subprocess.run(
                        ["zpaq", "add", f"./{t}.zpaq", f"./{t}.zip"],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.STDOUT,
                    )
                    # Delete the zip file
                    subprocess.run(["rm", f"./{t}.zip"])
                    # Move the file to the backups folder
                    shutil.move(
                        f"{filepath}/{t}.zpaq", fr"/{filepath}/backups/{t}.zpaq"
                    )
                # If it doesn't work, keep the zip file
                except OSError:
                    shutil.move(f"{filepath}/{t}.zip",
                                fr"/{filepath}/backups/{t}.zip")
            time.sleep(day)
    print("Backup loop not run on the non-linux system")


def begin():
    return
    threads = [
        Thread(target=backup, name="Database backup"),
        Thread(target=compresslogs, name="Log compression"),
        Thread(target=updatedb, name="Database collumn update", args=("inv",)),
    ]

    for x in threads:
        x.start()

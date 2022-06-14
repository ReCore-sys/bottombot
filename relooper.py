import os
import shutil
import time
import zipfile
import sqlite3
from threading import Thread
from datetime import datetime

filepath = os.path.abspath(os.path.dirname(__file__))

day = 60*60*24


def backup():
    getos = os.name
    if getos == "posix":
        while True:
            with open(f"{filepath}/data.db", "rb") as db:
                dt = datetime.now()
                t = dt.strftime("%d-%b-%y_%H-%M-%S")
                with zipfile.ZipFile(fr"{filepath}/{t}.zip", mode='x') as archive:
                    archive.writestr(f"{t}.db", db.read())
                shutil.move(f"{filepath}/{t}.zip",
                            fr"/{filepath}/backups/{t}.zip")
            time.sleep(day)


def begin():
    threads = list()
    thr1 = Thread(target=backup, name="Database backup")
    threads.append(thr1)

    for x in threads:
        x.start()

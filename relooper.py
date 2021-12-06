import os
import shutil
import time
import zipfile
from datetime import datetime
from threading import Thread

import sqlbullshit

filepath = os.path.abspath(os.path.dirname(__file__))

sql = sqlbullshit.sql(f"{filepath}/data.db", "user")

day = 60 * 60 * 24


def updatedb(added: str):
    collums = sql.get_collums()
    if added not in collums:
        sql.add_column(added)


def backup():
    getos = os.name
    if getos == "posix":
        while True:
            with open(f"{filepath}/data.db", "rb") as db:
                dt = datetime.now()
                t = dt.strftime("%d-%b-%y_%H-%M-%S")
                with zipfile.ZipFile(fr"{filepath}/{t}.zip", mode="x") as archive:
                    archive.writestr(f"{t}.db", db.read())
                shutil.move(f"{filepath}/{t}.zip", fr"/{filepath}/backups/{t}.zip")
            time.sleep(day)


def begin():
    threads = list()
    thr1 = Thread(target=backup, name="Database backup")
    thr2 = Thread(target=updatedb, name="Database collumns", args=("inv",))
    threads.append(thr1)
    threads.append(thr2)

    for x in threads:
        x.start()

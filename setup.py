import os
import shutil
import time
import zipfile
import pexpect
import subprocess
from threading import Thread
from datetime import datetime

filepath = os.path.abspath(os.path.dirname(__file__))

day = 60*60*24

std = ""


def wavelink_start():
    global std
    # Start the wavelink msuic thing
    print("\nInitiating wavelink")
    # Start the .jar via subprocess and then pipe the output into the void cos no one gives a shit about it
    child = pexpect.spawn(
        f"java -jar {filepath}/Lavalink.jar")

    child.expect(
        '.*All illegal access operations will be denied in a future release.*')
    print("Lavalink started")
    time.sleep(2)
    return


def backup():
    getos = os.name
    # Run the backup loop only if we are on linux
    if getos == "posix":
        while True:
            # Read the database file as binary
            with open(f"{filepath}/data.db", "rb") as db:
                # Save the raw datetime
                dt = datetime.now()
                # Convert it into something we can read
                t = dt.strftime("%d-%b-%y_%H-%M-%S")
                # Convert the copied db to a zip file
                with zipfile.ZipFile(fr"{filepath}/{t}.zip", mode='x') as archive:
                    archive.writestr(f"{t}.db", db.read())
                # Attempt to compress the zip file with ZPAQ
                try:
                    # ZPAQ it with subprocess
                    subprocess.run(["zpaq", "add", f"./{t}.zpaq", f"./{t}.zip"],
                                   stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
                    # Delete the zip file
                    subprocess.run(["rm", f"./{t}.zip"])
                    # Move the file to the backups folder
                    shutil.move(f"{filepath}/{t}.zpaq",
                                fr"/{filepath}/backups/{t}.zpaq")
                # If it doesn't work, keep the zip file
                except:
                    shutil.move(f"{filepath}/{t}.zip",
                                fr"/{filepath}/backups/{t}.zip")
            time.sleep(day)
    print("Backup loop not run on the non-linux system")


def begin():
    threads = [Thread(target=backup, name="Database backup")
               ]

    for x in threads:
        x.start()

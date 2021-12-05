""" A Module to simplify a lot of complex SQL queries
    ----------
    ----------
    Contains the following functions:
    ----------
    `doesexist()`: Find out if the user exists
    `set()`: Sets a value
    `add()`: Adds to a value
    `take()`: Removes from a value
    `adduser()`: Adds a user
    `removeuser()`: Removes a user
    `get()`: Retrieves a value
    `getall()`: Retrieves all values for a field
    `collums()`: Lists the collums
    `addcollum()`: Adds a collum
    """

import sqlite3


class SQLerror(Exception):
    pass


class sql:
    def __init__(self, db: str = None, table: str = None):
        """A basic sql handler
        ----------
        ----------


        Parameters
        ----------
        db : str, optional
            The database file to connect to, by default None
        table : str, optional
            name of the table to manipulate, by default None
        """
        if db is None:
            raise SQLerror("No database specified")
        if table is None:
            raise SQLerror("No table specified")
        self.db = sqlite3.connect(db)
        self.cursor = self.db.cursor()
        self.table = table
        self.conversions = {"STRING": "TEXT", None: "NULL", "FLOAT": "REAL"}

    try:

        def doesexist(self, usr: int) -> bool:
            """doesexist Checks if a user exists in the db

            Parameters
            ----------
            usr : int
                The id to check for

            Returns
            -------
            bool
                True/False if they exist
            """
            self.cursor.execute(f"select * from {self.table} where id = ?", (int(usr),))
            if self.cursor.fetchone() is None:
                return False
            else:
                return True

        def set(self, amount: int, usr: int, field: str):
            """set
            \nSets the value of a field

            Parameters
            ----------
            amount : int
                The amount to set it to
            usr : int
                the userid of the target
            field : str
                The field to modify
            """
            if self.doesexist(int(usr)):
                self.cursor.execute(
                    f"update {self.table} set {field} = ? where id = ?",
                    (amount, int(usr)),
                )
                self.db.commit()
            else:
                raise SQLerror(f"User {usr} does not exist")

        def add(self, amount: int, usr: int, field: str):
            """add
            \nAdds a value to a field

            Parameters
            ----------
            amount : int
                The amount to add
            usr : int
                the userid of the target
            field : str
                The field to modify
            """
            if self.doesexist(int(usr)):
                self.cursor.execute(
                    f"update {self.table} set {field} = {field} + ? where id = ?",
                    (amount, int(usr)),
                )
                self.db.commit()
            else:
                raise SQLerror(f"User {usr} does not exist")

        def take(self, amount: int, usr: int, field: str):
            """take
            \nTakes a value from a field
            Parameters
            ----------
            amount : int
                The amount to take
            usr : int
                the userid of the target
            field : str
                The field to modify
            """
            if self.doesexist(int(usr)):
                self.cursor.execute(
                    f"update {self.table} set {field} = {field} - ? where id = ?",
                    (amount, int(usr)),
                )
                self.db.commit()
            else:
                raise SQLerror(f"User {usr} does not exist")

        def adduser(self, usr: int):
            """adduser
            \nAdds a user to the DB

            Parameters
            ----------
            usr : int
                The userid of the target
            """
            if self.doesexist(int(usr)) is False:
                self.cursor.execute(
                    f"insert into {self.table} (id) VALUES(?)", (int(usr),)
                )
                self.db.commit()
            else:
                raise SQLerror(f"User {usr} already exists")

        def removeuser(self, usr: int):
            """removeuser\n
            Removes a user from the db

            Parameters
            ----------
            usr : int
                Userid of the target
            """
            if self.doesexist(int(usr)):
                self.cursor.execute(
                    f"DELETE FROM {self.table} WHERE id = ?", (int(usr),)
                )
                self.db.commit()
            else:
                raise SQLerror(f"User {usr} does not exist")

        def collums(self) -> list:
            """collums\n
            Gets a list of all available fields in the database

            Returns
            -------
            list
                a list of the collums
            """
            self.cursor.execute(f"PRAGMA table_info({self.table})")
            res = self.cursor.fetchall()
            return [x[1] for x in res]

        def addcollum(self, field: str, datatype: str):
            """addcollum\n
            Adds a collum to the database

            Parameters
            ----------
            field : str
                The field name to add
            datatype : str
                The type of data to store

            Raises
            ------
            SQLerror
                Data type is not valid
            """
            if datatype.upper() in [
                "INT",
                "DATE",
                "TEXT",
                "STRING",
                "NULL",
                None,
                "REAL",
                "FLOAT",
            ]:
                if datatype.upper() in self.conversions:
                    datatype = self.conversions[datatype]
                self.cursor.execute(f"ALTER TABLE {self.table} ADD {field} {datatype}")
                self.db.commit()
            else:
                raise SQLerror("Invalid data type")

        def get(self, usr: int, field: str) -> int:
            """get
            \nGets a specific value from the database
            \nUse collums() to list all available fields

            Parameters
            ----------
            usr : int
                the userid to target
            field : str
                The field to search for

            Returns
            -------
            str/int/None
                The result of the search
            """
            self.cursor.execute(
                f"select {field} from {self.table} where id = ?", (int(usr),)
            )
            res = self.cursor.fetchone()
            if res is not None:
                return res[0]
            else:
                return None

        def getall(self, inp: str, **mode: str) -> list:
            """getall
            \nGets all results

            Parameters
            ----------
            inp : str/id
                The field or ID to get results for

            mode : kwarg
                Can take multiple values. If `mode` is "id", it will return all collums for that id\n
                If "field", will return all items in that collum\n
                If condition is specified, will add a `where` condition to the end of the query

            Returns
            -------
            list
                The results
            """
            if "mode" not in mode:
                mode["mode"] = "id"

            if mode["mode"] == "id":
                self.cursor.execute(f"select * from {self.table} where id = {inp}")
                res = self.cursor.fetchall()
                if res != []:
                    return res
                else:
                    return None
            else:
                if "condition" in mode:
                    self.cursor.execute(
                        f"select {inp} from {self.table} where {mode['condition']}"
                    )
                    res = self.cursor.fetchall()
                    if res != []:
                        return res
                    else:
                        return None
                elif inp not in self.collums():
                    return None
                else:
                    if "condition" in mode:
                        self.cursor.execute(
                            f"select {inp} from {self.table} where {mode['condition']}"
                        )
                        res = self.cursor.fetchall()
                        if res != []:
                            return res
                        else:
                            return None
                    else:
                        self.cursor.execute(f"select {inp} from {self.table}")
                        res = self.cursor.fetchall()
                        if res != []:
                            return res
                        else:
                            return None

    except KeyboardInterrupt:
        # If a keyboard interupt is called, close the db
        def closedb(self):
            self.db.close()

        closedb()

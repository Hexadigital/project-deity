# This file is part of Project Deity.
# Copyright 2020-2021, Frostflake (L.A.)
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.

import json
import mysql.connector
import os

# Load database config
with open("config.json", "r") as file:
    config = json.load(file)["database"]

# Establish connection to database
connection = mysql.connector.connect(host=config["host"],
                                     database=config["database"],
                                     user=config["username"],
                                     password=config["password"])
if connection.is_connected():
    db_Info = connection.get_server_info()
    print("Connected to SQL Server version", db_Info)
    cursor = connection.cursor(buffered=True)
    cursor.execute("SELECT MAX(version) as version FROM `db_versioning`;")
    record = cursor.fetchone()
    # Convert current version to int
    if record[0] is None:
        current_version = 0
    else:
        current_version = int(record[0])
    print("You're currently running schema version:", current_version)
    # Loop through version upgrades
    for sql_file in os.listdir("./database"):
        try:
            # Skip non-SQL files
            if sql_file.endswith(".sql"):
                file_version = int(sql_file.split(".sql")[0])
                print("Found schema version %s..." % file_version)
                # Only run the SQL file if it is from a later version
                if file_version > current_version:
                    with open("./database/" + sql_file, "r") as sql:
                        for result in cursor.execute(sql.read(), multi=True):
                            pass
        # TODO: Handle this better
        except RuntimeError:
            pass
    connection.commit()
    connection.close()
else:
    print("Double check your config!")

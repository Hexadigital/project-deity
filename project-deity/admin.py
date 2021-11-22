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
import psycopg2
import psycopg2.extras
import sys

from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import pyqtSlot


class AdminPanel(QtWidgets.QMainWindow):
    def __init__(self):
        super(AdminPanel, self).__init__()
        uic.loadUi('admin.ui', self)
        with open("config.json", "r") as file:
            config = json.load(file)
        self.conn = psycopg2.connect(host=config["database"]["host"],
                                     port=config["database"]["port"],
                                     user=config["database"]["username"],
                                     password=config["database"]["password"],
                                     dbname=config["database"]["database"],
                                     application_name='Admin Panel')
        self.conn.set_session(autocommit=True)
        self.cursor = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        self.current_selections = {}
        self.load_followers()
        self.load_locations()
        self.show()

    def load_followers(self):
        self.cursor.execute('''SELECT id, name FROM "project-deity".followers ORDER BY id''')
        followers = self.cursor.fetchall()
        self.followerTable.setRowCount(len(followers))
        for i in range(0, len(followers)):
            self.followerTable.setItem(i, 0, QtWidgets.QTableWidgetItem(str(followers[i]['id'])))
            self.followerTable.setItem(i, 1, QtWidgets.QTableWidgetItem(str(followers[i]['name'])))
        self.cursor.execute('''SELECT id, class_name FROM "project-deity".follower_classes ORDER BY class_name''')
        classes = self.cursor.fetchall()
        self.followerClass.addItems([x['class_name'] for x in classes])

    @pyqtSlot()
    def on_followerTable_itemSelectionChanged(self):
        selection = [x.text() for x in self.followerTable.selectedItems()]
        self.cursor.execute('''SELECT *, fc.class_name FROM "project-deity".followers f
                               LEFT JOIN "project-deity".follower_classes fc ON f.class_id = fc.id
                               WHERE f.id = %s''', (int(selection[0]), ))
        r = self.cursor.fetchone()
        self.current_selections["Follower"] = r
        self.followerName.setText(r['name'])
        self.followerClass.setCurrentIndex(self.followerClass.findText(r['class_name']))
        self.followerLevel.setText(str(r['level']))
        self.followerExperience.setText(str(r['exp']))
        self.followerRequiredExperience.setText(str(r['next_level_exp']))
        self.followerGold.setText(str(r['monies']))
        self.followerStrength.setText(str(r['strength']))
        self.followerEndurance.setText(str(r['endurance']))
        self.followerIntelligence.setText(str(r['intelligence']))
        self.followerAgility.setText(str(r['agility']))
        self.followerWillpower.setText(str(r['willpower']))
        self.followerLuck.setText(str(r['luck']))
        self.followerPoints.setText(str(r['stat_points']))
        self.followerReputation.setText(str(r['reputation']))
        self.followerDevotion.setText(str(r['devotion']))

    def load_locations(self):
        self.cursor.execute('''SELECT id, name FROM "project-deity".locations ORDER BY id''')
        locations = self.cursor.fetchall()
        self.locationTable.setRowCount(len(locations))
        for i in range(0, len(locations)):
            self.locationTable.setItem(i, 0, QtWidgets.QTableWidgetItem(str(locations[i]['id'])))
            self.locationTable.setItem(i, 1, QtWidgets.QTableWidgetItem(str(locations[i]['name'])))

    @pyqtSlot()
    def on_locationTable_itemSelectionChanged(self):
        selection = [x.text() for x in self.locationTable.selectedItems()]
        self.cursor.execute('''SELECT * FROM "project-deity".locations
                               WHERE id = %s''', (int(selection[0]), ))
        r = self.cursor.fetchone()
        self.current_selections["Location"] = r
        self.locationName.setText(r['name'])
        self.locationType.setText(r['type'])
        self.locationX.setText(str(r['x']))
        self.locationY.setText(str(r['y']))
        self.locationFloors.setText(str(r['floors']))


app = QtWidgets.QApplication(sys.argv)
window = AdminPanel()
app.exec_()

# This file is part of Project Deity.
# Copyright 2021, Frostflake (L.A.)
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

class Inventory(object):
    def __init__(self, height=5, width=5):
        self.height = height
        self.width = width
        self.capacity = height*width
        self.slots = []

    # Returns True if the inventory is full
    def is_full(self):
        return self.capacity == len(self.slots)

    # Returns False if the inventory is full, otherwise it will
    # add the item and return True.
    def add_item(self, item_object):
        if self.is_full():
            return False
        self.slots.append(item_object)
        return True

    # Returns a comma separated list of the items in the inventory
    def __str__(self):
        inventory_string = ""
        for item in self.slots:
            if item.modifier:
                inventory_string += item.modifier + " " + item.name
            else:
                inventory_string += item.name
            inventory_string += ", "
        # Remove the last delimiter
        return inventory_string[:-2]

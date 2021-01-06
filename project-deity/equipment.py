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

class Equipment(object):
    def __init__(self):
        self.equipped = {
            "Accessory": None,
            "Helmet": None,
            "Ring": None,
            "Weapon": None,
            "Armor": None,
            "Shield": None,
            "Gloves": None,
            "Legs": None,
            "Boots": None
        }

    # Returns False if the item can't be equipped,
    # Returns None if the item is equipped to an empty slot,
    # and otherwise returns the previously equipped item
    def equip_item(self, item_object):
        if item_object.class_type in self.equipped.keys():
            old_item = self.equipped[item_object.class_type]
            self.equipped[item_object.class_type] = item_object
            return old_item
        else:
            # Not an equip item
            return False

    # Returns a comma separated list of the equipment slots
    def __str__(self):
        equipment_order = ["Accessory", "Helmet", "Ring", "Weapon",
                           "Armor", "Shield", "Gloves", "Legs", "Boots"]
        equipment_string = ""
        for slot in equipment_order:
            item = self.equipped[slot]
            if item is not None:
                if item.modifier:
                    equipment_string += item.modifier + " " + item.name
                else:
                    equipment_string += item.name
                equipment_string += ", "
        if len(equipment_string) == 0:
            return equipment_string
        else:
            # Remove the last delimiter
            return equipment_string[:-2]

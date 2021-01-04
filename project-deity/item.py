# This file is part of Project Deity.
# Copyright 2020, Frostflake (L.A.)
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

class Item(object):
    def __init__(self, name, class_type, image, value, weight,
                 rarity=0, modifier=None, attributes={}):
        self.name = name
        # The class type is used for determining the way the item is handled.
        # Examples: Weapon, Potion, Chest, etc.
        self.class_type = class_type
        # The image is the file name of the item's image.
        self.image = image
        self.value = value
        self.weight = weight
        # Rarity ranges from 0-6, where 0 is a common item.
        self.rarity = rarity
        # The modifier is a title prepended to the common name.
        # Examples: Enchanted, Sharp, Jagged, etc.
        self.modifier = modifier
        # The attributes are free-form and vary depending on the class.
        # Can be used for storing a weapon's attack, or details about who
        # crafted the item, and so forth.
        self.attributes = attributes

    def get_image(self):
        return str("./images/items/" + self.image)

    # This method is used for a generic observe description.
    def __str__(self):
        if not self.modifier:
            return "You are looking at a %s. \
                    It has a market value of %s gold, \
                    and weighs %s." % (self.name, self.value, self.weight)
        else:
            return "You are looking at a %s %s. \
                    It has a market value of %s gold, and \
                    weighs %s." % (self.modifier, self.name,
                                   self.value, self.weight)

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

class Account(object):
    def __init__(self, id_num, name, bridge_info={}):
        # Internal ID
        self.id = id_num
        # The name of this deity
        self.name = name
        # A list of character IDs registered on this account
        self.characters = []
        # Optional: Information pertaining to bridged services
        self.bridge_info = {}

    def can_create_character(self):
        return len(self.characters) < 3

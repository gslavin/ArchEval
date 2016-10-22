#
# ECE49X - Senior Design
# Eric Rock, George Slavin, Avik Bag
# ArchEval
#
#

import string

class search_param:

    def __init__( self, name, values ):
        self.name = name
        self.values = values

    def __str__( self ):
        string = self.name + ': {'
        for i in self.values:
            string += str(i) + ', '

        string += '}'
        return string

    def size( self ):
        return len(self.values)


import re
import __builtin__


from pyyacp.profiler.xsd11 import SingleSubType, MultiSubType


decimal_regex=h = re.compile('(\+|-)?([0-9]+(\.[0-9]*)?|\.[0-9]+)$')
class decimal(SingleSubType):

    def __init__(self):
        super(decimal, self).__init__(subType=integer())

    def _isType(self,value):
        return decimal.is_decimal(value)

    @staticmethod
    def is_decimal(value):
        return decimal_regex.match(value)

integer_regex=re.compile('^[\-+]?[0-9]+$')
class integer(MultiSubType):

    def __init__(self):
        subtypes=[
            long()
            ,nonPositiveInteger()
            ,nonNegativeInteger()
        ]
        super(integer, self).__init__(subTypes=subtypes)

    def _isType(self,value):
        return integer.is_integer(value)

    def convert(self, value):
        return __builtin__.int(value)

    @staticmethod
    def is_integer(value):
        return  integer_regex.match(value)

class long(SingleSubType):

    def __init__(self):
        super(long, self).__init__(subType=int())

    def _isType(self,value):
        return long.is_long(value)

    @staticmethod
    def is_long(value):
        return -9223372036854775808<= value <=9223372036854775807

class int(SingleSubType):

    def __init__(self):
        super(int, self).__init__(subType=short())

    def _isType(self,value):
        return int.is_int(value)

    @staticmethod
    def is_int(value):
        return 2147483647>= value >= -2147483648

class short(SingleSubType):

    def __init__(self):
        super(short, self).__init__(subType=byte())

    def _isType(self,value):
        return short.is_short(value)

    @staticmethod
    def is_short(value):
        return 32767>= value >= -32768

class byte(SingleSubType):


    def _isType(self,value):
        return byte.is_byte(value)

    @staticmethod
    def is_byte(value):
        return 127 >= value >= -128





class negativeInteger(SingleSubType):


    def _isType(self,value):
        return negativeInteger.is_negativeInteger(value)

    @staticmethod
    def is_negativeInteger(value):
        return value <= -1

class nonPositiveInteger(SingleSubType):
    def __init__(self):
        super(nonPositiveInteger, self).__init__(subType=negativeInteger())

    def _isType(self, value):
        return nonPositiveInteger.is_nonPositiveInteger(value)

    @staticmethod
    def is_nonPositiveInteger(value):
        return value <= 0


class nonNegativeInteger(MultiSubType):

    def __init__(self):
        subtypes=[
            unsignedLong()
            ,positiveInteger()
        ]
        super(nonNegativeInteger, self).__init__(subTypes=subtypes)


    def _isType(self,value):
        return nonNegativeInteger.is_nonNegInt(value)

    @staticmethod
    def is_nonNegInt(value):
        return value >= 0




class positiveInteger(SingleSubType):


    def _isType(self,value):
        return positiveInteger.is_positiveInteger(value)

    @staticmethod
    def is_positiveInteger(value):
        return value >= 1


class unsignedLong(SingleSubType):

    def __init__(self):
        super(unsignedLong, self).__init__(subType=unsignedInt())

    def _isType(self,value):
        return unsignedLong.is_unsignedLong(value)

    @staticmethod
    def is_unsignedLong(value):
        return 18446744073709551615 >= value >= 0

class unsignedInt(SingleSubType):

    def __init__(self):
        super(unsignedInt, self).__init__(subType=unsignedShort())

    def _isType(self,value):
        return unsignedInt.is_unsignedInt(value)

    @staticmethod
    def is_unsignedInt(value):
        return 4294967295 >= value >= 0

class unsignedShort(SingleSubType):

    def __init__(self):
        super(unsignedShort, self).__init__(subType=unsignedByte())

    def _isType(self,value):
        return unsignedShort.is_unsignedShort(value)

    @staticmethod
    def is_unsignedShort(value):
        return 65535 >= value >= 0

class unsignedByte(SingleSubType):


    def _isType(self,value):
        return unsignedByte.is_unsignedByte(value)

    @staticmethod
    def is_unsignedByte(value):
        return 255 >= value >= 0
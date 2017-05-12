import re

from pyyacp.profiler.xsd11 import MultiSubType,SingleSubType
from pyyacp.profiler.xsd11.anyatomic_decimal import decimal

class anySimpleType(MultiSubType):

    def __init__(self):
        subTypes=[
            anyAtomicType()
        ]
        super(anySimpleType, self).__init__(subTypes=subTypes)

    def _isType(self, value):
        return True


class anyAtomicType(MultiSubType):

    def __init__(self):
        subTypes=[
            boolean()
            ,anyURI()
            ,base64Binary()
            ,date()
            ,dateTime()
            ,decimal()
            ,double()
            ,duration()
            ,float()
            ,gDay()
            ,gMonthDay()
            ,gMonth()
            ,gYear()
            ,gYearMonth()
            ,hexBinary()
            ,time()
            ,string()
        ]
        super(anyAtomicType, self).__init__(subTypes=subTypes)

    def _isType(self, value):
        return True

###############
# anyAtomicType
################
class boolean(SingleSubType):

    def _isType(self,value):
        return value in ['true','false','1','0']


class anyURI(SingleSubType):

    def _isType(self,value):
        return anyURI.is_iri(value)

    @staticmethod
    def is_iri(value):
        try:
            import rfc3987
            rfc3987.parse(value, rule="URI")
            return True
        except Exception as e:
            return False



class base64Binary(SingleSubType):

    def _isType(self,value):
        return base64Binary.is_base64binary(value)

    @staticmethod
    def is_base64binary(value):
        import base64
        try:
            base64.decodestring(value)
            return True
        except Exception:
            return False



date_regex=re.compile('^-?([1-9][0-9]{3,}|0[0-9]{3})-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])(Z|(\+|-)((0[0-9]|1[0-3]):[0-5][0-9]|14:00))?$')
class date(SingleSubType):


    def _isType(self, value):
        return date.is_date(value)
    @staticmethod
    def is_date(value):
        return date_regex.search(value)

class dateTime(SingleSubType):

    def __init__(self):
        super(dateTime, self).__init__(subType=dateTimeStamp())

    def _isType(self,value):
        return dateTime.is_datetime(value)

    @staticmethod
    def is_datetime(value):
        regex='^(-?(?:[1-9][0-9]*)?[0-9]{4})-(1[0-2]|0[1-9])-(3[01]|0[1-9]|[12][0-9])T(2[0-3]|[01][0-9]):([0-5][0-9]):([0-5][0-9])(\.[0-9]+)?(Z|[+-](?:2[0-3]|[01][0-9]):[0-5][0-9])?$'
        if re.search(regex, value):
            return True
        return False



class dateTimeStamp(SingleSubType):

    def _isType(self,value):
        return dateTimeStamp.is_datetimestamp(value)

    @staticmethod
    def is_datetimestamp(value):
        regex='^(-?(?:[1-9][0-9]*)?[0-9]{4})-(1[0-2]|0[1-9])-(3[01]|0[1-9]|[12][0-9])T(2[0-3]|[01][0-9]):([0-5][0-9]):([0-5][0-9])(\.[0-9]+)\.*(Z|[+-](?:2[0-3]|[01][0-9]):[0-5][0-9])?$'
        if re.search(regex, value):
            return True
        return False


class double(SingleSubType):

    def _isType(self,value):
        return double.is_double(value)

    @staticmethod
    def is_double(value):
        regex='^((\+|-)?([0-9]+(\.[0-9]*)?|\.[0-9]+)([Ee](\+|-)?[0-9]+)?|(\+|-)?INF|NaN)$'
        if re.match(regex, value):
            return True
        return False

class duration(MultiSubType):

    def __init__(self):
        subTypes=[
            yearMonthDuration()
            ,dayTimeDuration()

        ]
        super(duration, self).__init__(subTypes=subTypes)

    def _isType(self,value):
        return duration.is_duration(value)

    @staticmethod
    def is_duration(value):
        regex='-?P((([0-9]+Y([0-9]+M)?([0-9]+D)?|([0-9]+M)([0-9]+D)?|([0-9]+D))(T(([0-9]+H)([0-9]+M)?([0-9]+(\.[0-9]+)?S)?|([0-9]+M)([0-9]+(\.[0-9]+)?S)?|([0-9]+(\.[0-9]+)?S)))?)|(T(([0-9]+H)([0-9]+M)?([0-9]+(\.[0-9]+)?S)?|([0-9]+M)([0-9]+(\.[0-9]+)?S)?|([0-9]+(\.[0-9]+)?S))))'
        if re.match(regex, value):
            return True
        return False


class yearMonthDuration(SingleSubType):
    def _isType(self,value):
        return yearMonthDuration.is_yearMonthDuration(value)

    @staticmethod
    def is_yearMonthDuration(value):
        regex='^(-?P((([0-9]+Y)([0-9]+M)?)|([0-9]+M)))$'
        if re.match(regex, value):
            return True
        return False

class dayTimeDuration(SingleSubType):
    def _isType(self,value):
        return dayTimeDuration.is_dayTimeDuration(value)

    @staticmethod
    def is_dayTimeDuration(value):
        regex='^([^YM]*[DT].*)$'
        if re.match(regex, value):
            return True
        return False



class float(SingleSubType):

    def _isType(self,value):
        return float.is_float(value)

    @staticmethod
    def is_float(value):
        regex='^((\+|-)?([0-9]+(\.[0-9]*)?|\.[0-9]+)([Ee](\+|-)?[0-9]+)?|(\+|-)?INF|NaN)$'
        if re.match(regex, value):
            return True
        return False

class gDay(SingleSubType):


    def _isType(self,value):
        return self.__class__.is_valid(value)

    @staticmethod
    def is_valid(value):
        regex='^(---(0[1-9]|[12][0-9]|3[01])(Z|(\+|-)((0[0-9]|1[0-3]):[0-5][0-9]|14:00))?)$'
        if re.match(regex, value):
            return True
        return False



class gMonthDay(SingleSubType):


    def _isType(self,value):
        return self.__class__.is_valid(value)

    @staticmethod
    def is_valid(value):
        regex='^(--(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])(Z|(\+|-)((0[0-9]|1[0-3]):[0-5][0-9]|14:00))?)$'
        if re.match(regex, value):
            return True
        return False


class gMonth(SingleSubType):


    def _isType(self,value):
        return self.__class__.is_valid(value)

    @staticmethod
    def is_valid(value):
        regex='^(--(0[1-9]|1[0-2])(Z|(\+|-)((0[0-9]|1[0-3]):[0-5][0-9]|14:00))?)$'
        if re.match(regex, value):
            return True
        return False


class gYear(SingleSubType):


    def _isType(self,value):
        return self.__class__.is_valid(value)

    @staticmethod
    def is_valid(value):
        regex='^(-?([1-9][0-9]{3,}|0[0-9]{3})(Z|(\+|-)((0[0-9]|1[0-3]):[0-5][0-9]|14:00))?)$'
        if re.match(regex, value):
            return True
        return False


class gYearMonth(SingleSubType):

    def _isType(self,value):
        return self.__class__.is_valid(value)

    @staticmethod
    def is_valid(value):
        regex='^(-?([1-9][0-9]{3,}|0[0-9]{3})-(0[1-9]|1[0-2])(Z|(\+|-)((0[0-9]|1[0-3]):[0-5][0-9]|14:00))?)$'
        if re.match(regex, value):
            return True
        return False



class hexBinary(SingleSubType):

    def _isType(self,value):
        return self.__class__.is_valid(value)

    @staticmethod
    def is_valid(value):
        regex='^(([0-9a-fA-F]{2})*)$'
        if re.match(regex, value):
            return True
        return False


class time(SingleSubType):

    def _isType(self,value):
        return self.__class__.is_valid(value)

    @staticmethod
    def is_valid(value):
        regex='^((([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\.[0-9]+)?|(24:00:00(\.0+)?))(Z|(\+|-)((0[0-9]|1[0-3]):[0-5][0-9]|14:00))?)$'
        if re.match(regex, value):
            return True
        return False



class string(SingleSubType):

    def __init__(self):
        super(string, self).__init__(subType=dateTimeStamp())

    def _isType(self,value):
        return self.__class__.is_valid(value)

    @staticmethod
    def is_valid(value):
        regex='^(([0-9a-fA-F]{2})*)$'
        if re.match(regex, value):
            return True
        return False





class language(SingleSubType):


    def _isType(self,value):
        return self.__class__.is_valid(value)

    @staticmethod
    def is_valid(value):
        regex='^([a-zA-Z]{1,8}(-[a-zA-Z0-9]{1,8})*)$'
        if re.match(regex, value):
            return True
        return False


class NMTOKEN(SingleSubType):


    def _isType(self,value):
        return self.__class__.is_valid(value)

    @staticmethod
    def is_valid(value):
        regex='^([-._:A-Za-z0-9]+)$'
        if re.match(regex, value):
            return True
        return False





class name(SingleSubType):


    def _isType(self,value):
        return self.__class__.is_valid(value)

    @staticmethod
    def is_valid(value):
        regex='^([_:A-Za-z][-._:A-Za-z0-9]*)$'
        if re.match(regex, value):
            return True
        return False

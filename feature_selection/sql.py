from pyparsing import Word, delimitedList, Optional, \
    Group, alphas, nums, alphanums, ParseException, Forward, oneOf, quotedString, \
    ZeroOrMore, Keyword 

class InvalidSQL(Exception):
    pass

def checkQuotedColon(s,loc,toks):
    if ':' in toks[0]:
        raise InvalidSQL("identifier with colon : must be in double quotes.")

def checkDoubleQuotes(s,loc,toks):
    if toks[0][0] == "'":
        raise InvalidSQL("quoted strings must use double quotes.")

ident          = Word( alphas, alphanums + "_:" ).setParseAction(checkQuotedColon)
columnName =   (ident | quotedString().setParseAction(checkDoubleQuotes))("columnName")

whereExpression = Forward()
and_ = Keyword("and", caseless=True)
or_ = Keyword("or", caseless=True)
in_ = Keyword("in", caseless=True)
isnull = Keyword("is null",caseless=True)
isnotnull = Keyword("is not null",caseless=True)
binop = oneOf("= != < > >= <=", caseless=True)
arithSign = Word("+-",exact=1)
realNum = Optional(arithSign) + ( Word( nums ) + "." + Optional( Word(nums) ) )
intNum = Optional(arithSign) + Word( nums )

columnRval = realNum | intNum | quotedString | columnName
whereCondition = Group(
    ( columnName + isnull ) |
    ( columnName + isnotnull ) |
    ( columnName + binop + columnRval ) |
    ( columnName + in_ + "(" + delimitedList( columnRval ) + ")" ) |
    ( "(" + whereExpression + ")" )
    )('condition')
whereExpression << Group(whereCondition + ZeroOrMore( ( and_ | or_ ) + whereExpression ) )('expression')

class SQLValidator(object):
    def __init__(self,s):
        self._s = s
        self._errors = []
        self._parse_result = None

    @property
    def valid(self):
        try:
            self._parse_result = whereExpression.parseString(self._s,parseAll=True)
        except InvalidSQL as e:
            self._errors.append(e.message)
            return False
        except ParseException as e:
            self._errors.append("SQL could not be parsed.")
            return False
        return True

    @property
    def errors(self):
        return self._errors

    @property
    def column_names(self):
        # takes a dictionary, returns a list
        def column_names_in_dict(d):
            result = []
            for key, value in d.iteritems():
                if 'columnName'  == key:
                    result = result + [value]
                if isinstance(value,dict):
                    result = result + column_names_in_dict(value)
            return result
        return column_names_in_dict(self._parse_result.asDict())

##############################################################################
#
# Copyright (c) 2005 Jim Washington and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

# minjson.py
# reads minimal javascript objects.
# str's objects and fixes the text to write javascript.

# Thanks to Patrick Logan for starting the json-py project and making so many
# good test cases.

# Jim Washington 10 Oct 2005.

# 2005-10-10 on reading, looks for \\uxxxx and replaces with u'\uxxxx'
# 2005-10-09 now tries hard to make all strings unicode when reading.
# 2005-10-07 got rid of eval() completely, makes object as found by the
#            tokenizer.
# 2005-09-06 imported parsing constants from tokenize; they changed a bit from
#            python2.3 to 2.4
# 2005-08-22 replaced the read sanity code
# 2005-08-21 Search for exploits on eval() yielded more default bad operators.
# 2005-08-18 Added optional code from Koen van de Sande to escape
#            outgoing unicode chars above 128


from re import compile, sub, search, DOTALL
from token import ENDMARKER, NAME, NUMBER, STRING, OP, ERRORTOKEN
from tokenize import tokenize, TokenError, NL

# set to true if transmission size is much more important than speed
# only affects writing, and makes a minimal difference in output size.
alwaysStripWhiteSpace = False

# set this to True if you want chars above 128 always expressed as /uxxx
# this is expensive.
doUxxxx = False

#Usually, utf-8 will work, set this to utf-16 if you dare.
emergencyEncoding = 'utf-8'

#################################
#      read JSON object         #
#################################

slashstarcomment = compile(r'/\*.*?\*/',DOTALL)
doubleslashcomment = compile(r'//.*\n')

unichrRE = compile(r"\\u[0-9a-fA-F]{4,4}")

def unichrReplace(match):
    return unichr(int(match.group()[2:],16))

escapeStrs = (('\\','\\\\'),('\n',r'\n'),('\b',r'\b'),
    ('\f',r'\f'),('\t',r'\t'),('\r',r'\r'), ('"',r'\"')
    )

class DictToken:
    __slots__=[]
    pass
class ListToken:
    __slots__=[]
    pass
class ColonToken:
    __slots__=[]
    pass
class CommaToken:
    __slots__=[]
    pass
class JSONReader(object):
    """raise SyntaxError if it is not JSON, and make the object available"""
    def __init__(self,data):
        self.stop = False
        #make an iterator of data so that next() works in tokenize.
        self._data = iter([data])
        self.lastOp = None
        self.objects = []
        self.tokenize()
        
    def tokenize(self):
        try:
            tokenize(self._data.next,self.readTokens)
        except TokenError:
            raise SyntaxError

    def resolveList(self):
        #check for empty list
        if isinstance(self.objects[-1],ListToken):
            self.objects[-1] = []
            return
        theList = []
        commaCount = 0
        try:
            item = self.objects.pop()
        except IndexError:
            raise SyntaxError
        while not isinstance(item,ListToken):
            if isinstance(item,CommaToken):
                commaCount += 1
            else:
                theList.append(item)
            try:
                item = self.objects.pop()
            except IndexError:
                raise SyntaxError
        if not commaCount == (len(theList) -1):
            raise SyntaxError
        theList.reverse()
        item = theList
        self.objects.append(item)

    def resolveDict(self):
        theList = []
        #check for empty dict
        if isinstance(self.objects[-1], DictToken):
            self.objects[-1] = {}
            return
        #not empty; must have at least three values
        try:
            #value (we're going backwards!)
            value = self.objects.pop()
        except IndexError:
            raise SyntaxError
        try:
            #colon
            colon = self.objects.pop()
            if not isinstance(colon, ColonToken):
                raise SyntaxError
        except IndexError:
            raise SyntaxError
        try:
            #key
            key = self.objects.pop()
            if not isinstance(key,basestring):
                raise SyntaxError
        except IndexError:
            
            raise SyntaxError
        #salt the while
        comma = value
        while not isinstance(comma,DictToken):
            # store the value
            theList.append((key,value))
            #do it again...
            try:
                #might be a comma
                comma = self.objects.pop()
            except IndexError:
                raise SyntaxError
            if isinstance(comma,CommaToken):
                #if it's a comma, get the values
                try:
                    value = self.objects.pop()
                except IndexError:
                    #print self.objects
                    raise SyntaxError
                try:
                    colon = self.objects.pop()
                    if not isinstance(colon, ColonToken):
                        raise SyntaxError
                except IndexError:
                    raise SyntaxError
                try:
                    key = self.objects.pop()
                    if not isinstance(key,basestring):
                        raise SyntaxError
                except IndexError:
                    raise SyntaxError
        theDict = {}
        for k in theList:
            theDict[k[0]] = k[1]
        self.objects.append(theDict)

    def readTokens(self,type, token, (srow, scol), (erow, ecol), line):
        # UPPERCASE consts from tokens.py or tokenize.py
        if type == OP:
            if token not in "[{}],:-":
                raise SyntaxError
            else:
                self.lastOp = token
            if token == '[':
                self.objects.append(ListToken())
            elif token == '{':
                self.objects.append(DictToken())
            elif token == ']':
                self.resolveList()
            elif token == '}':
                self.resolveDict()
            elif token == ':':
                self.objects.append(ColonToken())
            elif token == ',':
                self.objects.append(CommaToken())
        elif type == STRING:
            tok = token[1:-1]
            for k in escapeStrs:
                if k[1] in tok:
                    tok = tok.replace(k[1],k[0])
            self.objects.append(tok)
        elif type == NUMBER:
            if self.lastOp == '-':
                factor = -1
            else:
                factor = 1
            try:
                self.objects.append(factor * int(token))
            except ValueError:
                self.objects.append(factor * float(token))
        elif type == NAME:
            try:
                self.objects.append({'true':True,
                    'false':False,'null':None}[token])
            except KeyError:
                raise SyntaxError
        elif type == ENDMARKER:
            pass
        elif type == NL:
            pass
        elif type == ERRORTOKEN:
            if ecol == len(line):
                #it's a char at the end of the line.  (mostly) harmless.
                pass
            else:
                raise SyntaxError
        else:
            raise SyntaxError
    def output(self):
        try:
            assert len(self.objects) == 1
        except AssertionError:
            raise SyntaxError
        return self.objects[0]

def safeRead(aString, encoding=None):
    """read the js, first sanitizing a bit and removing any c-style comments
    If the input is a unicode string, that's OK.  If the input is a byte string, 
    strings in the object will be produced as unicode anyway.
    """
    # get rid of trailing null. Konqueror appends this.
    CHR0 = chr(0)
    while aString.endswith(CHR0):
        aString = aString[:-1]
    # strip leading and trailing whitespace
    aString = aString.strip()
    # zap /* ... */ comments
    aString = slashstarcomment.sub('',aString)
    # zap // comments
    aString = doubleslashcomment.sub('',aString)
    # detect and handle \\u unicode characters. Note: This has the side effect
    # of converting the entire string to unicode. This is probably OK.
    unicodechars = unichrRE.search(aString)
    if unicodechars:
        aString = unichrRE.sub(unichrReplace, aString)
    #if it's already unicode, we won't try to decode it
    if isinstance(aString, unicode):
        s = aString
    else:
        if encoding:
            # note: no "try" here.  the encoding provided must work for the 
            # incoming byte string.  UnicodeDecode error will be raised
            # in that case.  Often, it will be best not to provide the encoding
            # and allow the default
            s = unicode(aString, encoding)
            #print "decoded %s from %s" % (s,encoding)
        else:
            # let's try to decode to unicode in system default encoding
            try:
                s = unicode(aString)
                #import sys
                #print "decoded %s from %s" % (s,sys.getdefaultencoding())
            except UnicodeDecodeError:
                # last choice: handle as emergencyEncoding
                enc = emergencyEncoding
                s = unicode(aString, enc)
                #print "%s decoded from %s" % (s, enc)
    # parse and get the object.
    try:
        data = JSONReader(s).output()
    except SyntaxError:
        raise ReadException, 'Unacceptable JSON expression: %s' % aString
    return data

read = safeRead

#################################
#   write object as JSON        #
#################################

#alwaysStripWhiteSpace is defined at the top of the module

tfnTuple = (('True','true'),('False','false'),('None','null'),)

def _replaceTrueFalseNone(aString):
    """replace True, False, and None with javascript counterparts"""
    for k in tfnTuple:
        if k[0] in aString:
            aString = aString.replace(k[0],k[1])
    return aString

def _handleCode(subStr,stripWhiteSpace):
    """replace True, False, and None with javascript counterparts if
       appropriate, remove unicode u's, fix long L's, make tuples
       lists, and strip white space if requested
    """
    if 'e' in subStr:
        #True, False, and None have 'e' in them. :)
        subStr = (_replaceTrueFalseNone(subStr))
    if stripWhiteSpace:
        # re.sub might do a better job, but takes longer.
        # Spaces are the majority of the whitespace, anyway...
        subStr = subStr.replace(' ','')
    if subStr[-1] in "uU":
        #remove unicode u's
        subStr = subStr[:-1]
    if "L" in subStr:
        #remove Ls from long ints
        subStr = subStr.replace("L",'')
    #do tuples as lists
    if "(" in subStr:
        subStr = subStr.replace("(",'[')
    if ")" in subStr:
        subStr = subStr.replace(")",']')
    return subStr

# re for a double-quoted string that has a single-quote in it
# but no double-quotes and python punctuation after:
redoublequotedstring = compile(r'"[^"]*\'[^"]*"[,\]\}:\)]')
escapedSingleQuote = r"\'"
escapedDoubleQuote = r'\"'

def _doQuotesSwapping(aString):
    """rewrite doublequoted strings with single quotes as singlequoted strings with
    escaped single quotes"""
    s = []
    foundlocs = redoublequotedstring.finditer(aString)
    prevend = 0
    for loc in foundlocs:
        start,end = loc.span()
        s.append(aString[prevend:start])
        tempstr = aString[start:end]
        endchar = tempstr[-1]
        ts1 = tempstr[1:-2]
        ts1 = ts1.replace("'",escapedSingleQuote)
        ts1 = "'%s'%s" % (ts1,endchar)
        s.append(ts1)
        prevend = end
    s.append(aString[prevend:])
    return ''.join(s)

strEscapes = (('\n',r'\n'),('\b',r'\b'),
    ('\f',r'\f'),('\t',r'\t'),('\r',r'\r'),('\u',r'\u') )

unicodeRE = compile(u"([\u0080-\uffff])")
unicodeREfunction = lambda(x): r"\u%04x" % ord(x.group(1))
    
slashxRX = compile(r"\\x[0-9a-fA-F]{2,2}")

xmlcharRX = compile(r"&#[0-9a-fA-F]{2,4};")

def slashxRXReplace(match):
    return unichr(int(match.group()[2:],16))

def uxreplace(match):
    c = match.group()[2:-1]
    l = len(c)
    if l == 2:
        return "\\u00%s" % c
    elif l == 3:
        return "\\u0%s" % c
    elif l == 4:
        return "\\u%s" % c

def _escapeSomeStringChars(aString):
    """replace single-character chars that have an escaped
    representation with their literals"""
    if doUxxxx:
        # escape anything above 128 as \uxxxx
        if unicodeRE.search(aString):
            aString = unicodeRE.sub(unicodeREfunction, aString)
    
    for character,replacement in strEscapes:
        if character in aString:
            aString = aString.replace(character,replacement)
    return aString

def _pyexpr2jsexpr(aString, stripWhiteSpace):
    """Take advantage of python's formatting of string representations of
    objects.  Python always uses "'" to delimit strings.  Except it doesn't when
    there is ' in the string.  Fix that, then, if we split
    on that delimiter, we have a list that alternates non-string text with
    string text.  Since string text is already properly escaped, we
    only need to replace True, False, and None in non-string text and
    remove any unicode 'u's preceding string values.

    if stripWhiteSpace is True, remove spaces, etc from the non-string
    text.
    """
    #do some escaping first
    aString = _escapeSomeStringChars(aString)
    #python will quote with " when there is a ' in the string,
    #so fix that first
    if redoublequotedstring.search(aString):
        aString = _doQuotesSwapping(aString)
    marker = None
    if escapedSingleQuote in aString:
        #replace escaped single quotes with a marker
        marker = markerBase = '|'
        markerCount = 1
        while marker in aString:
            #if the marker is already there, make it different
            markerCount += 1
            marker = markerBase * markerCount
        aString = aString.replace(escapedSingleQuote,marker)
    #escape double-quotes
    aString = aString.replace('"',escapedDoubleQuote)
    #split the string on the real single-quotes
    splitStr = aString.split("'")
    outList = []
    alt = True
    for subStr in splitStr:
        if alt:
            #if alt is True, non-string; do replacements
            subStr = _handleCode(subStr,stripWhiteSpace)
        outList.append(subStr)
        alt = not alt
    result = '"'.join(outList)
    if marker:
        #put the escaped single-quotes back as "'"
        result = result.replace(marker,"'")
    return result

def write(obj, encoding='utf-8', stripWhiteSpace=alwaysStripWhiteSpace,\
    encodeOutput=None):
    """Represent the object as a byte string in JSON notation.
    
    JSON specification says that the output is unicode, and what we really 
    usually want is an encoded byte string for output. Since this method cannot
    know whether it is "at the boundary", it will by default output a python 
    unicode object that you can encode at the boundary.  
    
    If there are bytestrings in the object that cannot be decoded in the system
    default encoding, this will decode them to unicode by an encoding provided.
    The default, utf-8, will work in most cases.  
    
    This method includes an experimental encodeOutput parameter, which may 
    suffice to make a byte string is that's what you want.  The encodeOutput 
    parameter needs to be the python identifier for the desired charset 
    encoding.  By default, a python unicode string will be output.
        
    """
    #  first, we get a representation of the object in unicode
    #  we will encode to an encoding later if desired.
    if not isinstance(obj,unicode):
        #get representation of object as unicode.
        aString = str(obj)
        if encoding:
            aString = unicode(aString, encoding)
        else:
            aString = unicode(aString, 'utf-8')
        #if \xnn converted to \\xnn, put those chars back
        if slashxRX.search(aString):
            aString = slashxRX.sub(slashxRXReplace, aString)
    else:
        # it's already a unicode string, no need to convert to unicode
        aString = obj
    
    if isinstance(obj,basestring):
        aString = aString.replace('\\','\\\\')
        if '"' in aString:
            aString = '"%s"' % aString.replace('"',escapedDoubleQuote)
        else:
            aString = '"%s"' % aString
        result = _escapeSomeStringChars(aString)
    else:
        result = _pyexpr2jsexpr(aString,stripWhiteSpace)
        
    #assert isinstance(result,unicode)
    
    if encodeOutput:
        # we have a choice here; xmlcharrefreplace or backslashreplace.
        # since it is likely a web thing, we choose xmlcharrefreplace and 
        # convert that back to \\unnn representation.  This is experimental
        # and may not do the right thing.
        result = result.encode(encodeOutput,"xmlcharrefreplace")
        if xmlcharRX.search(result):
            #if \xnn converted to &#nn;, put those chars back as \\u00nn
            #print "result before conversion: %s" % result
            result = xmlcharRX.sub(uxreplace, result)
            #print "result after conversion: %s" % result
            # Waah! it replaces unprintable chars in the charset with printable
            # but different chars.  It should be rare.
    return result

class ReadException(Exception):
    pass

class WriteException(Exception):
    pass

class oper:
    def __init__(self, value, priority, func):
        self.value = value
        self.priority = priority
        self.func = func
    def __repr__(self):
        return 'oper({},{},{})'.format(self.value, self.priority, self.func)
    def __str__(self):
        return self.value
    def __lt__(self, other):
        return self.priority < other.priority
class omobj(list):
    class _parenslist(tuple):
        def __bool__(self):
            return bool(self[0] or self[1])

    def __new__( self, base = None, nodes = [], parens = None):
        return super().__new__(self, nodes)

    def __init__(self, base = None, nodes = [], parens = None):
        super().__init__(nodes)
        self.base = base or 1
        self.parens = omobj._parenslist(parens or ('', ''))

    @property
    def basestr(self):
        return str(self.base)
    
    @staticmethod
    def basefromstr(base):
        # if base[0] in control.allquotes:
        #     if __debug__:
        #         assert base[-1] in control.allquotes
        #     return base
        if __debug__:
            assert base != None
        try:
            return int(base)
        except ValueError:
            try:
                return float(base)
            except ValueError:
                try:
                    return complex(base)
                except ValueError:
                    return str(base)
                    raise SyntaxError('No known way to deal with \'{}\''.format(base))

    def __bool__(self):
        return bool(len(self) or self.parens or self.base)

    def __repr__(self):
        ret = 'omobj('
        if self.base:
            ret += 'base = ' + repr(self.base) + ', '
        if len(self):
            ret += 'nodes = ' + super().__repr__() + ', '
        if self.parens:
            ret += 'parens = ' + repr(self.parens)
        if not self.parens and (self.base or len(self)):
            ret = ret[:-2]
        return ret + ')'

    # def __str__(self):
    #     if not self:
    #         return ''.join((str(self.parens[0]), self.basestr, str(self.parens[1])))
    #     if self.base in control.opers['binary']:
    #         return ''.join((str(self.parens[0]), str(self[0]), self.basestr, str(self[1]), str(self.parens[1])))
    #     return ''.join((self.basestr, str(self.parens[0]), ', '.join(str(x) for x in self), str(self.parens[1])))

    def eval(self, locls):
        if not self:
            locls['$'] = None
        elif self.basestr in control.allopers:
            control.evaloper(self, locls)
        elif self.basestr in control.funcs:
            control.funcs[self.basestr](self, locls)
        else:
            if self.basestr == '':
                if __debug__:
                    assert len(self) == 1, self #expects 1 element (in parens)
                self[0].eval(locls)
            elif self.basestr in locls:
                locls['$'] = locls[self.basestr]
            else:
                if self.basestr in control.consts:
                    locls['$'] = control.consts[self.basestr]
                else:
                    if self.basestr == 'locals' or self.basestr == 'locls':
                        locls['$'] = str(locls)
                    else:
                        locls['$'] = omobj(base = self.basestr[0])

class control:
    import math
    from random import random
    delims = {'arraysep':(',', None),
              'etc':('|', None),
              'endline':(';', lambda x, y: y)}
    parens = {'l':'([{', 'r':')]}'}
    consts = {
        'True': True,   'False': False,     'None' : None, 'Null' : None, 'Nil' : None,
        'true': True,   'false': False,     'none' : None, 'null' : None, 'nil' : None,
        'T': True, 'F': False, 'N':None, #these can be overriden
        't': True, 'f': False, 'n':None, #these can be overriden
        'pi': math.pi,  'PI': math.pi,      'π': math.pi,   'Π': math.pi,
        'e': math.e,    'E':  math.e,
        'k': 8.9875517873681764E9, 'K': 8.9875517873681764E9,
        'i': complex(0, 1), 'j':complex(0,1),
        'nan':float('nan'), 'NAN': float('nan'),
        'inf':float('inf'), '∞': float('inf'),
        'rand':random(),
        '½': 1 / 2,
        '⅓': 1 / 3,
        '⅔': 2 / 3,
        '¼': 1 / 4,
        '¾': 3 / 4,
        '⅕': 1 / 5,
        '⅖': 2 / 5,
        '⅗': 3 / 5,
        '⅘': 4 / 5,
        '⅙': 1 / 6,
        '⅚': 5 / 6,
        '⅐': 1 / 7,
        '⅛': 1 / 8,
        '⅜': 3 / 8,
        '⅝': 5 / 8,
        '⅞': 7 / 8,
        '⅑': 1 / 9,
        '⅒': 1/ 10,
    }
    opers = {
        'binary':{
            ':'   : oper(':',      0, None), # association
            '??'   : oper(':',      0, None), # association
            '**'  : oper('**',     3, lambda x, y: x ** y), # power of
            '*'   : oper('*',      4, lambda x, y: x *  y), # mult
            '/'   : oper('/',      4, lambda x, y: x /  y), # div
            '%'   : oper('%',      4, lambda x, y: x %  y), # mod
            '+'   : oper('+',      5, lambda x, y: x +  y), # plus
            '-'   : oper('-',      5, lambda x, y: x -  y), # minus
            'b<<' : oper('b<<',    6, lambda x, y: x << y), # bitwise <<
            'b>>' : oper('b<<',    6, lambda x, y: x >> y), # bitwise >>
            'b&'  : oper('b&',     7, lambda x, y: x &  y), # bitwise &
            'b^'  : oper('b^',     8, lambda x, y: x ^  y), # bitwise ^
            'b|'  : oper('b|',     9, lambda x, y: x |  y), # bitwise |
            '<'   : oper('<',     10, lambda x, y: x <  y), # less than
            '>'   : oper('>',     10, lambda x, y: x >  y), # greater than
            '<='  : oper('<=',    10, lambda x, y: x <= y), # less than or equal
            '>='  : oper('>=',    10, lambda x, y: x >= y), # greater than or equal
            '=='  : oper('==',    10, lambda x, y: x == y), # equal to
            '='   : oper('=',     10, lambda x, y: x == y), # equal to
            '<>'  : oper('<>',    10, lambda x, y: x != y), # equal to
            '!='  : oper('!=',    10, lambda x, y: x != y), # not equal to
            '&&'  : oper('&&',    11, None), # boolean and
            '||'  : oper('||',    12, None), # booleon or
            #assignment operators
            # all notes are in form of "x OPERATOR y" like 'x <- y'
            '<-'   : oper('<-',   13, None), # x = y
            '<?-'  : oper('<?-',  13, None), # x = bool(y) ? y : None
            '<+-'  : oper('<+-',  13, None), # x += y
            '<--'  : oper('<--',  13, None), # x -= y
            '<*-'  : oper('<*-',  13, None), # x *= y
            '</-'  : oper('</-',  13, None), # x /= y
            '<**-' : oper('<**-', 13, None), # x **= y
            '<%-'  : oper('<%-',  13, None), # x %= y
            '<&-'  : oper('<&-',  13, None), # x &= y
            '<|-'  : oper('<|-',  13, None), # x |= y
            '<^-'  : oper('<^-',  13, None), # x ^= y
            '<<-'  : oper('<<-',  13, None), # x <<= y
            '<>-'  : oper('<>-',  13, None), # x >>= y
            #inverted assignment operators
            # all notes are in form of "x OPERATOR y" like 'x -> y'
            '->'   : oper('->',   13, None), # y = x
            '-?>'  : oper('-?>',  13, None), # y = bool(x) ? x : None
            '-+>'  : oper('-+>',  13, None), # y += x
            '-->'  : oper('-->',  13, None), # y -= x 
            '-*>'  : oper('-*>',  13, None), # y *= x 
            '-/>'  : oper('-/>',  13, None), # y /= x 
            '-**>' : oper('-**>', 13, None), # y **= x 
            '-%>'  : oper('-%>',  13, None), # y %= x 
            '-&>'  : oper('-&>',  13, None), # y &= x 
            '-|>'  : oper('-|>',  13, None), # y |= x 
            '-^>'  : oper('-^>',  13, None), # y ^= x 
            '-<>'  : oper('-<>',  13, None), # y <<= x 
            '->>'  : oper('->>',  13, None)  # y >>= x 
             },\
        'unary':{
            'l':{'~':oper('~', 1, lambda x, y: ~y),
                 'pos':oper('pos', 1, lambda x, y: +y),
                 'neg':oper('neg', 1, lambda x, y: -y)},
            'r':{'!':oper('!', 2, lambda x, y: not x)}
        }
    }
    opers['unary']['l'].update({d[0]:oper(d[0], 14, d[1]) for d in delims.values()})
    funcs = {
        #reason this is a dict not a tuple is because later on some of these might be 1-line lambdas
        'if': lambda eles, locls: control._doFunc(eles, locls, 'if'),
        'for': lambda eles, locls: control._doFunc(eles, locls, 'for'),
        'disp': lambda eles, locls: control._doFunc(eles, locls, 'disp'),
        'abort': lambda eles, locls: control._doFunc(eles, locls, 'abort'),
        'displ': lambda eles, locls: control._doFunc(eles, locls, 'displ'),
    }


    linebreak = '\n\r' #linebreak is used for comments
    comment = '#'
    escape = '\\'
    datadef = '@'
    nbwhitespace = ' \t\x0b\x0c'
    whitespace = nbwhitespace + linebreak

    allquotes = '\'\"`'
    alldelims = ''.join(v[0] for v in delims.values())
    allparens = ''.join(list(parens.values())) + allquotes #yes, quotes are parens lol :P
    allopers = opers['binary']; allopers.update(opers['unary']['l']); allopers.update(opers['unary']['r'])

    sortedopers = tuple(x for x in reversed(sorted(allopers.keys(), key = lambda l: len(l)))) #sorted by length

    punctuation = '!#$%&*+-/;<=>?@^|~' + allparens + alldelims + allquotes#stuff used to break apart things, ignoring ._
    
    @staticmethod
    def invertparen(paren):
        return {'(':')', ')':'(',   '[':']', ']':'[',   '{':'}','}':'{'}[paren]

    @staticmethod
    def _doFunc(eles, locls, funcname):
        if funcname == 'disp' or funcname == 'displ':
            if len(eles) == 0: #aka, its jsut disp or displ
                print(end = funcname == 'displ' and '\n' or '')
                return
            if __debug__:
                assert eles[0].base == funcname, 'this shouldn\'t break'
            eles[1].eval(locls)
            print(locls['$'], end = '\n' if funcname == 'displ' else '') #keep this here!
        elif funcname == 'abort':
            if len(eles) == 0:
                locls['$'] = ''
            else:
                if __debug__:
                    assert eles[0].base == funcname, 'this shouldn\'t break'
                eles[1].eval(locls)
            if __debug__:
                assert '$' in locls
            quit('Aborting!' + ('' if locls['$'] == '' else ' Message: \'{}\''.format(str(locls['$']))))
        elif funcname == 'if':
            if __debug__:
                assert eles[0].base == funcname, 'this shouldn\'t break'
                assert len(eles[1]) == 2, 'this shouldn\'t break!' #should be CONDITION, VALUE
            eles[1][0].eval(locls) # evaluates the condition
            # if len(eles[1])
            if locls['$']:
                if len(eles[1][1]) == 1:
                    eles[1][1][0].eval(locls)
                else:
                    if __debug__:
                        assert len(eles[1][1]) == 2
                    eles[1][1][0].eval(locls)
            elif len(eles[1][1]) == 2:
                eles[1][1][1].eval(locls)
        elif funcname == 'for':
            if __debug__:
                assert eles[0].base == funcname, 'this shouldn\'t break'
                assert len(eles[1]) == 2, 'this shouldn\'t break!' #should be CONDITION, VALUE
            eles[1][0][0].eval(locls) # evaluates the condition
            while True:
                eles[1][0][1][0].eval(locls) #checks the statement
                if not locls['$']:
                    break
                eles[1][1].eval(locls)
                eles[1][0][1][1].eval(locls)
            if locls['$']:
                eles[1][1][0].eval(locls)
            elif len(eles[1][1]) == 2:
                eles[1][1][1].eval(locls)

        else:
            raise SyntaxError('function \'{}\' isn\'t defined yet!'.format(funcname))
    
    @staticmethod
    def _specialoper(eles, locls):
        name = eles.base
        if name in control.alldelims:
            if name in control.delims['arraysep']:
                eles[0].eval(locls)
                ele1 = locls['$']
                eles[1].eval(locls)
                if isinstance(locls['$'], list):
                    locls['$'] = [ele1] + locls['$']
                else:
                    locls['$'] = [ele1, locls['$']]
                return
            else:
                raise SyntaxError('Special Operator \'{}\' isn\'t defined yet!'.format(name))
        if name == ':':
            if eles[0].base in control.alldelims:
                assert 0, str(eles) + " | " + eles[0]
            if __debug__:
                assert eles[0].base in control.funcs, 'no way to proccess function \'{}\''.format(eles[0].base)
            control.funcs[eles[0].base](eles, locls)
        elif name == '||' or name == '&&':
            eles[0].eval(locls)
            element = locls['$']
            if name == '&&' and not element or name == '||' and element:
                return element
            eles[1].eval(locls)
            locls['$'] = (element or locls['$']) if name == '&&' else (element and locls['$'])
        else:
            direc = name in ['<-', '<?-', '<+-', '<--', '<*-', '</-', '<**-', '<%-', '<&-', '<|-', '<^-', '<<-', '<>-']
            if direc == 1:
                eles[1].eval(locls)
                value =locls['$']
                key = eles[0].base
            else:
                eles[0].eval(locls)
                value =locls['$']
                key = eles[1].base
            if __debug__:
                assert name == '<-'  or\
                       name == '->'  or\
                       name == '<?-' or\
                       name == '-?>' or\
                       key in locls, '\'{}\' needs to be defined to perform \'{}\' on it!'.format(key, name)
                if   name == '<-'   or name == '->'  : locls[key] = value
                elif name == '<?-'  or name == '-?>' :
                    locls[key] = value if value else (locls[key] if key in locls else None)
                elif name == '<+-'  or name == '-+>' : locls[key] += value
                elif name == '<--'  or name == '-->' : locls[key] = value
                elif name == '<*-'  or name == '-*>' : locls[key] = value
                elif name == '</-'  or name == '-/>' : locls[key] = value
                elif name == '<**-' or name == '-**>': locls[key] = value
                elif name == '<%-'  or name == '-%>' : locls[key] = value
                elif name == '<&-'  or name == '-&>' : locls[key] = value
                elif name == '<|-'  or name == '-|>' : locls[key] = value
                elif name == '<^-'  or name == '-^>' : locls[key] = value
                elif name == '<<-'  or name == '-<>' : locls[key] = value
                elif name == '<>-'  or name == '->>' : locls[key] = value
            if direc == 0: #swap the return value
                locls['$'] = locls[key]

    @staticmethod
    def evaloper(eles, locls):
        if eles.base not in control.allopers:
            raise SyntaxError('operator \'{}\' isn\'t defined'.format(eles.base))
        oper = control.allopers[eles.base]
        if oper.func == None:
            control._specialoper(eles, locls)
        elif eles:
            eles[0].eval(locls)
            ret = locls['$']
            name = eles.base
            for ele in eles[1:]:
                ele.eval(locls)
                ret = control.allopers[name].func(ret, locls['$'])
            locls['$'] = ret# x = y

    @staticmethod
    def applyrules(tokens):
        print(tokens)
        if __debug__:
            assert tokens[0] == '@'
            assert tokens[1] == 'define', tokens[1] #currently, only 'define' is defined.
        assert 0, 'not implemented yet! todo: this'
        # fixedtokens = 

class wfile:
    def __init__(self, filepath, encoding = 'utf-8'):
        self.filepath = filepath
        import codecs
        with codecs.open(filepath, 'r', encoding) as f:
            self.striptext = wfile._striptext(f.read())
        self.tokens = wfile._tokenize(self.striptext)
        import copy
        self.lines = wfile._compresstokens(copy.deepcopy(self.tokens))
    
    def __str__(self):
        def getl(linep, l):
            if not l:
                assert str(l) == ';' or str(l) == '', str(l) #no other known case atm
                return linep, ''
            if __debug__:
                assert l[0].base not in control.delims['endline'][0] or not l[0].base, l[0].base # node structure should prevent this.
            ret = ''
            if l[0]:
                ret = '\n{}:  \t{}'.format(linep, l[0])
                linep += 1
            if l[1].base not in control.delims['endline'][0]:
                ret += '\n{}:  \t{}'.format(linep, l[1])
                linep += 1
            else:
                e = getl(linep, l[1])
                ret += e[1]
                linep += e[0]
            return linep, ret
        return 'file \'{}\':\n==[start]==\n{}\n\n==[ end ]=='.format(self.filepath, getl(0, self.lines)[1])

    @staticmethod
    def _striptext(rawt):
        """ remove comments and blank lines"""
        ret = ''
        data = 0b00 # 0b10 = escaped, 0b01 = commented
        for char in rawt:
            # print(char, char in control.linebreak, ret)
            if char in control.escape  and not data & 0b10:
                data ^= 0b10
            elif char in control.comment and not data & 0b10:
                data ^= 0b01
            elif char in control.linebreak:
                continue
                # if not data & 0b10 and (not ret or ret[-1] not in control.linebreak): #so no duplicate \ns
                    # ret += char
                # data &= 0b10 #remove comments
            else:
                if data & 0b10:
                    ret += control.escape
                data &= 0b01
                if not data & 0b01:
                    ret += char
        return ret
    
    @staticmethod
    def _tokenize(rawt):
        """ goes thru, and splits them up first based upon control.sortedopers and then by control.punctuation. """
        def tokenize(rawt):
            for oper in control.sortedopers:
                if oper in rawt:
                    par = rawt.partition(oper)
                    if rawt[rawt.index(oper) - 1] in control.escape:
                        return [par[0] + par[1]] + tokenize(par[2])
                    return tokenize(par[0]) + [par[1]] + tokenize(par[2])
            for punc in control.punctuation + control.delims['endline'][0]:
                if punc in rawt:
                    par = rawt.partition(punc)
                    if rawt[rawt.index(punc) - 1] in control.escape:
                        return [par[0] + par[1]] + tokenize(par[2])
                    return tokenize(par[0]) + [par[1]] + tokenize(par[2])
            return [rawt]
        tokens = [token for token in (token.strip(control.nbwhitespace) for token in tokenize(rawt)) if token]
            
        ret = []
        currentquote = None
        for token in tokens:
            if token in control.allquotes:
                if currentquote == None:
                    ret.append(token)
                    currentquote = token
                else:
                    if token == currentquote:
                        currentquote = None
                    ret[-1] += token                    
            elif currentquote:
                ret[-1] += token
            else:
                ret.append(token)

        #@define stuff
        linep = 0
        while linep < len(ret): 
            if ret[linep] and ret[linep] in control.datadef:
                control.applyrules(ret.pop(0))
            linep+=1
        return ret

    @staticmethod
    def _compresstokens(linetokens):
        def findhighest(linegrp):
            if __debug__:
                assert linegrp, linegrp
            highest = None
            for elep in range(len(linegrp)):
                ele = linegrp[elep].base
                if ele in control.allopers and (highest == None or
                        control.allopers[ele] > control.allopers[linegrp[highest].base]):
                    highest = elep
            if __debug__:
                if not highest:
                    raise SyntaxError('no operator for string \'{}\'!'.format(linegrp))
            return highest
        def compresstokens(linegrp): #this is non-stable
            ret = omobj(parens = linegrp.parens) #universe
            while len(linegrp):
                ele = linegrp.pop(0) #pop(0) is inefficient for list. update this in the future
                if ele not in control.allparens:
                    ret.append(omobj(base = str(ele)))
                else:
                    toappend = omobj()
                    parens = {str(ele):1}
                    while sum(parens.values()) > 0 and len(linegrp):
                        toappend.append(linegrp.pop(0))
                        if toappend[-1] in control.allparens:
                            last = toappend[-1]
                            if last in control.parens['l']:
                                if last not in parens:
                                    parens[last] = 0
                                parens[last] += 1
                            if last in control.parens['r']:
                                if __debug__:
                                    assert control.invertparen(last) in parens, 'unmatched paren \'{}\'!'.format(last)
                                parens[control.invertparen(last)] -= 1
                    if __debug__:
                        assert toappend[-1] in control.allparens, toappend #the last element should be in allparens
                    toappend.parens = (ele, toappend.pop())
                    toappend = compresstokens(toappend)
                    ret.append(toappend)
            return ret
        def fixtkns(line):
            #combine tokens using order of operations
            if not len(line):
                return line
            if len(line) == 1: #if the line is literally a single element
                if len(line[0]) == 0: #if the line is literally a single constant
                    return line
                else:
                    return fixtkns(line[0])
            fhp = findhighest(line)
            if __debug__:
                assert isinstance(line[fhp], omobj), 'expected a omobj for fhp! (not %s)' % line[fhp]
            ret = omobj(base = line[fhp].base, parens = line.parens)
            s = fixtkns(omobj(nodes = line[0:fhp]))
            e = fixtkns(omobj(nodes = line[fhp + 1:]))
            if s != None:
                if len(s) == 1 and not s.base and not s.hasparens():
                    ret.append(s[0])
                else:
                    ret.append(s)
            if e != None:
                if len(e) == 1 and not e.base and not e.hasparens():
                    ret.append(e[0])
                else:
                    ret.append(e)
            return ret
        return fixtkns(compresstokens(omobj(nodes = linetokens)))
    
    def eval(self):
        locls = {}
        self.lines.eval(locls)
        if '$' in locls:
            del locls['$']
        return locls

if __name__ == '__main__':
    import sys
    if len(sys.argv) == 1:
        filepath = 'testcode.om'
    else:
        filepath = sys.argv[1] #0 is 'main.py'
        if __debug__:
            if sys.argv[1] == '/Users/westerhack/code/python/Omega/main.py':
                filepath = 'testcode.om'
    f = wfile(filepath)
    # print(f)
    # print('--')
    f.eval()

"""
@f1(arg)
   @f2
   def func(): pass

"""
















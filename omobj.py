class omobj:
    def __init__(self, base, evalfunc = None):
        self.base = omobj._getbase(base)
        self.evalfunc = evalfunc

    @staticmethod
    def _getbase(base):
        import control
        if base == '':
            return base
        if base[0] in control.allquotes:
            if __debug__:
                assert base[-1] in control.allquotes
            return base
        else:
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

    def __str__(self):
        return str(self.base)

    def __repr__(self):
        return 'omobj({},evalfunc={})'.format(repr(self.base), repr(self.evalfunc))

    def __bool__(self):
        return bool(str(self))
    def __eq__(self, other):
        if __debug__:
            assert hasattr(other, 'base')
            assert hasattr(other, 'evalfunc')
        return self.base == other.base and self.evalfunc == other.evalfunc

    def eval(self, eles, locls):
        if self.evalfunc == None:
            locls['$'] = self.base
        else:
            self.evalfunc(eles, locls)

class oper(omobj):

    def __init__(self, base, priority, evalfunc):
        super().__init__(base, evalfunc)
        self.priority = priority

    def __repr__(self):
        return 'oper({},{},{})'.format(self.base, self.priority, self.evalfunc)

    def __str__(self):
        return self.base
    def __lt__(self, other):
        return self.priority < other.priority

    def eval(self, eles, locls):
        if self.evalfunc == None:
            self._specialoper(eles, locls)
        elif eles:
            eles[0].eval(locls)
            ret = locls['$']
            name = eles.basestr
            for ele in eles[1:]:
                ele.eval(locls)
                ret = self.evalfunc(ret, locls['$'])
            locls['$'] = ret# x = y

    def _specialoper(self, eles, locls):
        from group import group
        import control
        print('todo: uncomment things in _specialoper')
        name = eles.basestr
        if name in control.alldelims:
            if name in control.delims['arraysep']:
                eles[0].eval(locls)
                ret = []
                name = eles.basestr
                for ele in eles:
                    ele.eval(locls)
                    ret.append(locls['$'])
                locls['$'] = group(val = ret)# x = y
                return
            else:
                raise SyntaxError("Special Operator '{}' isn't defined yet!".format(name))
        elif name == ':':
            if eles[0].basestr in locls:
                assert 0, 'when does this ever happen?'
                locls[eles[0].basestr].eval(eles[1])
            else:
                eles[0].base.eval(eles[1],locls)
        elif name == '||' or name == '&&':
            eles[0].eval(locls)
            element = locls['$']
            if name == '&&' and not element or name == '||' and element:
                return element
            eles[1].eval(locls)
        else:
            direc = name[0] == '<' and name[-1] == '-'
            if direc == 1:
                eles[1].eval(locls)
                value =locls['$']
                key = eles[0].basestr
            else:
                eles[0].eval(locls)
                value =locls['$']
                key = eles[1].basestr
                name = '<' + name[1:-1] + '-'
            if __debug__:
                assert name == '<-'  or\
                       name == '->'  or\
                       name == '<?-' or\
                       name == '-?>' or\
                       key in locls, "'{}' needs to be defined to perform '{}' on it!".format(key, name)
            if   name == '<-'  : locls[key] = value
            elif name == '<?-' : locls[key] = value if value else (locls[key] if key in locls else None)
            elif name == '<+-' : locls[key] += value
            elif name == '<--' : locls[key] -= value
            elif name == '<*-' : locls[key] *= value
            elif name == '</-' : locls[key] /= value
            elif name == '<**-': locls[key] **= value
            elif name == '<%-' : locls[key] %= value
            elif name == '<&-' : locls[key] &= value
            elif name == '<|-' : locls[key] |= value
            elif name == '<^-' : locls[key] ^= value
            elif name == '<<-' : locls[key] <<= value
            elif name == '<>-' : locls[key] >>= value
            if direc == 0: #swap the return value
                locls['$'] = locls[key]

class func(omobj):
    def __init__(self, base):
        super().__init__(base, None)
    def eval(self, eles, locls):
        import control
        print("attempting to eval eles '{}' with locls '{}' in func '{}'".format(eles, locls, self))
        if self.evalfunc != None:
            super().eval(eles, local)
        else:
            if 'disp' in str(self):
                if __debug__:
                    if len(eles) != 0:
                        assert eles[0].basestr == str(self), "this shouldn't break"
                if len(eles) == 0:
                    print(end = '' if str(self) == 'disp' else '\n')
                elif len(eles[1]) == 0:
                    eles[1].eval(locls)
                    print(locls['$'],end = '' if str(self) == 'disp' else '\n')
                elif str(self) == 'disp':
                    for ele in eles[1]:
                        ele.eval(locls)
                        print(locls['$'], end = '')
                elif str(self) == 'displ':
                    for ele in eles[1]:
                        ele.eval(locls)
                        print(locls['$'], end = '\n')
                elif str(self) == 'dispc':
                    for ele in eles[1]:
                        ele.eval(locls)
                        print(locls['$'], end = ', ' if ele is not eles[1][-1] else '\n')
            elif str(self) == 'abort':
                if eles.isfinal() and eles.base != control.funcs['abort']:
                    locls['$'] = eles
                elif '$' not in locls:
                    locls['$'] = ''
                if __debug__:
                    assert '$' in locls
                quit('Aborting!' + (str(locls['$']) and " Message: '{}'".format(str(locls['$']))))
            elif str(self) == 'if':
                if __debug__:
                    assert eles[0].basestr == str(self), "this shouldn't break"
                    assert len(eles) in (3, 4), 'can only have if:(cond):(if true)[:(if false)];'
                eles[1].eval(locls) # evaluates the condition
                if locls['$']:
                    eles[2].eval(locls)
                elif len(eles) == 4:
                    eles[3].eval(locls)
            elif str(self) == 'for':
                if __debug__:
                    assert eles[0].basestr == str(self), "this shouldn't break"
                    assert len(eles) == 3, 'can only have for:(...):{ expression };'
                    assert len(eles[1]) == 3, 'can only have (initialize; condition; increment)'
                eles[1][0].eval(locls) # initializes the for loop the condition
                while True:
                    eles[1][1].eval(locls) #check the conditoin
                    if not locls['$']:
                        break
                    eles[2].eval(locls)
                    eles[1][2].eval(locls) #increment
            else:
                raise SyntaxError("function '{}' isn't defined yet!".format(str(self)))

from obj import *#operobj, obj, funcobj,'',  numobj
import math
import random
linebreak = '\n\r' #linebreak is used for comments
comment = '#'
allkeywords = {}
escape = '\\'
datadef = '@'

import re
numre = re.compile(r'^(?:0[oxbeOXBE])?[\d.]+$')

nbwhitespace = ' \t\x0b\x0c'
whitespace = nbwhitespace + linebreak
allquotes = '\'\"`'

delims = {'arraysep':(',', operobj(',', 14)),
          'etc':('|', operobj('|', 14)),
          'endline':(';\n', operobj(';', 14))
          }
parens = {'l':'([{', 'r':')]}'}
consts = {
    'true' : boolobj(True),
    'false': boolobj(False),
    'null' : nullobj(),
    'pi'   : numobj(math.pi), 'π': numobj(math.pi),
    'e'    : numobj(math.e),
    'k'    : numobj(8.987551787368e9),
    'imag' : numobj(complex(0,1)),
    'locls': funcobj('locls', None), #todo, make this return locals
    'rand' : funcobj('rand', random.random),
    'nan'  : numobj(float('nan')), 'NaN': numobj(float('nan')),
    'inf'  : numobj(float('inf')), '∞': numobj(float('inf')),

    '½' : numobj(1 / 2), '⅓' : numobj(1 / 3), '⅔' : numobj(2 / 3), '¼' : numobj(1 / 4), '¾' : numobj(3 / 4),
    '⅕' : numobj(1 / 5), '⅖' : numobj(2 / 5), '⅗' : numobj(3 / 5), '⅘' : numobj(4 / 5), '⅙' : numobj(1 / 6),
    '⅚' : numobj(5 / 6), '⅛' : numobj(1 / 8), '⅜' : numobj(3 / 8), '⅝' : numobj(5 / 8), '⅞' : numobj(7 / 8),
}
opers = {
    'binary':{
        ':'   : operobj(':',      0), # association
        '**'  : operobj('**',     3), # power of
        '*'   : operobj('*',      4), # mult
        '/'   : operobj('/',      4), # div
        '%'   : operobj('%',      4), # mod
        '+'   : operobj('+',      5), # plus
        '-'   : operobj('-',      5), # minus
        'b<<' : operobj('b<<',    6), # bitwise <<
        'b>>' : operobj('b<<',    6), # bitwise >>
        'b&'  : operobj('b&',     7), # bitwise &
        'b^'  : operobj('b^',     8), # bitwise ^
        'b|'  : operobj('b|',     9), # bitwise |
        '<'   : operobj('<',     10), # less than
        '>'   : operobj('>',     10), # greater than
        '<='  : operobj('<=',    10), # less than or equal
        '>='  : operobj('>=',    10), # greater than or equal
        '=='  : operobj('==',    10), # equal to
        '='   : operobj('=',     10), # equal to
        '<>'  : operobj('<>',    10), # equal to
        '!='  : operobj('!=',    10), # not equal to
        '&&'  : operobj('&&',    11), # boolean and
        '||'  : operobj('||',    12), # booleon or
        #assignment operators
        # all notes are in form of "x OPERATOR y" like 'x <- y'
        '<-'   : operobj('<-',   13), # x = y
        '<?-'  : operobj('<?-',  13), # x = bool(y) ? y : None
        '<+-'  : operobj('<+-',  13), # x += y
        '<--'  : operobj('<--',  13), # x -= y
        '<*-'  : operobj('<*-',  13), # x *= y
        '</-'  : operobj('</-',  13), # x /= y
        '<**-' : operobj('<**-', 13), # x **= y
        '<%-'  : operobj('<%-',  13), # x %= y
        '<&-'  : operobj('<&-',  13), # x &= y
        '<|-'  : operobj('<|-',  13), # x |= y
        '<^-'  : operobj('<^-',  13), # x ^= y
        '<<-'  : operobj('<<-',  13), # x <<= y
        '<>-'  : operobj('<>-',  13), # x >>= y
        #inverted assignment operators
        # all notes are in form of "x OPERATOR y" like 'x -> y'
        '->'   : operobj('->',   13), # y = x
        '-?>'  : operobj('-?>',  13), # y = bool(x) ? x : None
        '-+>'  : operobj('-+>',  13), # y += x
        '-->'  : operobj('-->',  13), # y -= x 
        '-*>'  : operobj('-*>',  13), # y *= x 
        '-/>'  : operobj('-/>',  13), # y /= x 
        '-**>' : operobj('-**>', 13), # y **= x 
        '-%>'  : operobj('-%>',  13), # y %= x 
        '-&>'  : operobj('-&>',  13), # y &= x 
        '-|>'  : operobj('-|>',  13), # y |= x 
        '-^>'  : operobj('-^>',  13), # y ^= x 
        '-<>'  : operobj('-<>',  13), # y <<= x 
        '->>'  : operobj('->>',  13)  # y >>= x 
         },
    'unary':{
        'l':{
            '~'  :operobj('~',    1),
            'pos':operobj('pos',  1),
            'neg':operobj('neg',  1),
            },
        'r':{
            '!'  :operobj('!',    2),
            }
    }
}
funcs = {
    #reason this is a dict not a tuple is because later on some of these might be 1-line lambdas
    'if': funcobj('if'),
    'for': funcobj('for'),
    'disp': funcobj('disp'),
    'abort': funcobj('abort'),
    'displ': funcobj('displ'),
    'dispc': funcobj('dispc'), #commas bxn elements
    'skip': funcobj('skip'), #ignore that line
    'del': funcobj('del'),
}

for d in delims.values():
    for val in d[0]:
        opers['unary']['l'][val] = d[1]

alldelims = ''.join(v[0] for v in delims.values())
allparens = ''.join(list(parens.values())) + allquotes #yes, quotes are parens lol :P
import copy
#crap i need a better way than this D:
allopers = copy.copy(opers['binary']); allopers.update(opers['unary']['l']); allopers.update(opers['unary']['r'])
allfuncs = copy.copy(allopers); allfuncs.update(funcs)
allkeywords = copy.copy(allfuncs); allkeywords.update(consts)
del copy

sortedopers = tuple(x for x in reversed(sorted(allopers.keys(), key = lambda l: len(l)))) #sorted by length

punctuation = '!#$%&*+-/;<=>?@^|~' + allparens + alldelims + allquotes#stuff used to break apart things, ignoring ._

def _invertparen(paren):
    return {'(':')', ')':'(',
            '[':']', ']':'[',
            '{':'}', '}':'{'}[paren]


def applyrules(tokens):
    print(tokens)
    if __debug__:
        assert tokens[0] == '@'
        assert tokens[1] == 'define', tokens[1] #currently, only 'define' is defined.
    assert 0, 'not implemented yet! todo: this'
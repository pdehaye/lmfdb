# -*- coding: utf-8 -*-
import sys
import time
import bson
import sage.all
from sage.all import *

from pymongo.connection import Connection
fields = Connection(port=dbport).numberfields.fields
fields = Connection(port=dbport).numberfields.fields

saving = True


def coeffs(s):
    return [a for a in s[1:-1].split(',')]


def base_label(d, r1, D, ind):
    return str(d) + "." + str(r1) + "." + str(abs(D)) + "." + str(ind)


def makeb(n, t):
    return bson.SON([('n', n), ('t', t)])


def makes(n, t):
    return '%02d,%03d' % (n, t)


def makels(li):
    li2 = [str(x) for x in li]
    return ','.join(li2)


def make_disc_key(D):
    s = 1
    if D < 0:
        s = -1
    Dz = D.abs()
    if Dz == 0:
        D1 = 0
    else:
        D1 = int(Dz.log(10))
    return s, '%03d%s' % (D1, str(Dz))


def coeff_to_poly(c):
    return PolynomialRing(QQ, 'x')(c)


def web_latex(u):
    return "\( %s \)" % sage.all.latex(u)

# Timeout code
import multiprocessing
import time


class TimeoutException(Exception):
    pass


class RunableProcessing(multiprocessing.Process):
    def __init__(self, func, *args, **kwargs):
        self.queue = multiprocessing.Queue(maxsize=1)
        args = (func,) + args
        multiprocessing.Process.__init__(self, target=self.run_func, args=args, kwargs=kwargs)

    def run_func(self, func, *args, **kwargs):
        try:
            result = func(*args, **kwargs)
            self.queue.put((True, result))
        except Exception as e:
            self.queue.put((False, e))

    def done(self):
        return self.queue.full()

    def result(self):
        return self.queue.get()


def timeout(seconds, force_kill=True):
    def wrapper(function):
        def inner(*args, **kwargs):
            now = time.time()
            proc = RunableProcessing(function, *args, **kwargs)
            proc.start()
            proc.join(seconds)
            if proc.is_alive():
                if force_kill:
                    proc.terminate()
                runtime = int(time.time() - now)
                raise TimeoutException('timed out after {0} seconds'.format(runtime))
            assert proc.done()
            success, result = proc.result()
            if success:
                return result
            else:
                raise result
        return inner
    return wrapper


# End timeout code

@timeout(600)
def getclgroup(K):
    clg = K.class_group()
    h = int(clg.order())
    clg = clg.invariants()
    clg = [int(j) for j in clg]
    uk = K.unit_group().fundamental_units()
    reg = float(K.regulator())
    return h, clg, uk, reg

# Take the polynomial as a string


@timeout(120)
def grhbnf(pol):
    bnf = pari('bnfinit(' + str(pol) + ',1)')
    return bnf[7]


def string2list(s):
    s = str(s)
    if s == '':
        return []
    return [int(a) for a in s.split(',')]

from outlist import li  # this reads in the list called li

tot = len(li)
print "finished importing li, number = %s" % tot
count = 0

PR = PolynomialRing(QQ, 'a')

for F in li:
# for F in li[0:1]:
    count += 1
    print "%d of %d: %s" % (count, tot, F)
    t = time.time()
    d, sig, D, coeffs, T, ramps = F
    absD = abs(ZZ(D))
    gal = makeb(d, T)
    s, dstr = make_disc_key(ZZ(D))
    ramps = [str(x) for x in ramps]
    pol = coeff_to_poly(coeffs)
    K = NumberField(pol, 'a')
    D = str(D)
    data = {
        'degree': d,
        'disc_abs_key': dstr,
        'disc_sign': s,
        'ramps': ramps,
        'coeffs': makels(coeffs),
        'signature': makels(sig)
    }
    index = 1
    is_new = True
    holdfield = ''
    for field in fields.find({'degree': d,
                              'signature': data['signature'],
                              'disc_abs_key': dstr}):
        index += 1
        if field['coeffs'] == data['coeffs']:
            holdfield = field
            is_new = False
            break

    if is_new:
        print "new field"
        label = base_label(d, sig[0], absD, index)
        info = {'label': label}
        try:
            cltime = time.time()
            h, clg, uk, reg = getclgroup(K)
            cltimeend = time.time()
            data['class_number'] = h
            data['class_group'] = makels(clg)
            if cltimeend - cltime >= 2:  # slow, so save
                data['reg'] = reg
                data['units'] = [web_latex(u) for u in uk]
        except:  # Catch the time out exception
            print "*******************************************  Timed out"
            try:
                bnf = grhbnf(pol)
            except:
                print "-------- Could not bnfinit"
            else:
                print "++++++++ bnf ok"
                data['class_number'] = int(bnf[0][0])
                clg = [int(j) for j in bnf[0][1]]
                data['class_group'] = makels(clg)
                data['reg'] = float(bnf[1])
                fu = str(bnf[4])  # "[3x^3+2, ...]"
                fu = fu.replace('[', '')
                fu = fu.replace(']', '')
                fu = fu.replace('x', 'a')
                uk = fu.split(',')
                uk = [PR(j) for j in uk]
                data['units'] = [web_latex(u) for u in uk]
                data['used_grh'] = True
        info.update(data)
        # print "entering %s into database"%info
        if saving:
            info['galois'] = gal
            fields.save(info)
    else:
        print "field already in database"
    print ""

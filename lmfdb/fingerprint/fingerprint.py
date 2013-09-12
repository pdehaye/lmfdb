
class Fingerprint(object):
    def URL(self):
        raise NotImplementedError
    def pymongo(self):
        return lambda x : x.URL()
    def python(self):
        return self.pymongo()
    def sage(self):
        return self.python()
 
class FingerprintedObject(object):
    def __getattr__(self, x):
        if x[len("fingerprint")] == "fingerprint":
            return self._fingerprints[x[len("fingerprint")+1:]](self)
        else:
            
from sage import *
 
class NumberField(object):
    def discriminant(self):
        return 173452372086487603462397683694367984694308676634269834760894368904367904238689
 
    def half_degree(self):
        return Rational(1/2)
    
    def factored_conductor(self):
        return factor(self.conductor())
 
    def polredabs(self):
        return Polynomial("x^2+1")
    
class FingerprintedObject(object):
    def fingerprint(self, encoding_scheme, encoding_type):
        relevant_scheme = type(self)._fingerprint_fns[encoding_scheme]
        return relevant_scheme[encoding_type](self)
        
class NumberField(FingerprintedObject):
    _fingerprint_fns = {
        "polredabs" : {
                    "pymongo" : lambda x: map(int, x.polredabs().swapped_coefficients()),
                    "python" : lambda x: map(int, x.polredabs().swapped_coefficients()),
                    "sage" : lambda x: Polynomial(x),
                    "URL" : lambda _:_ 
                 },
        "human": { 
                    "python" : lambda x : (x.degree(), x.discriminant()), 
                    "pymongo": lambda x : (x.degree(), jones_trick(x.discriminant()) )
                    "sage" : lambda x: x,
                    "URL" : lambda _:_
        } 
        }
        
    
 
NumberField().fingerprint("polredabs", "pymongo")
 
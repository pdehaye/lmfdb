# A mockup of a fingerprinting functionality for mathematical objects
# The goal is to standardize how we refer to the keys
# Inheriting from FingerprintedObject provides a method with name
# fingerprint
# which takes two arguments: a labelling scheme and a purpose.

from sage import *
 
class FingerprintedObject(object):
    def fingerprint(self, encoding_scheme, encoding_type):
        relevant_scheme = type(self)._fingerprint_fns[encoding_scheme]
        return relevant_scheme[encoding_type](self)
        
class MockupNumberField(FingerprintedObject):
    _fingerprint_fns = {
        "polredabs" : {
                    "pymongo" : lambda x: map(int, x.polredabs().swapped_coefficients()),
                    "python" : lambda x: map(int, x.polredabs().swapped_coefficients()),
                    "sage" : lambda x: Polynomial(x),
                    "URL" : lambda _:_ ,
                    "latex": lambda _:_.field2tex()
                 },
        "human": { 
                    "python" : lambda x : (x.degree(), x.discriminant()), 
                    "pymongo": lambda x : (x.degree(), jones_trick(x.discriminant()) )
                    "sage" : lambda x: x,
                    "URL" : lambda _:_,
                    "latex": lambda _:_.field2tex()
        } 
        }
    def discriminant(self):
        return 173452372086487603462397683694367984694308676634269834760894368904367904238689
 
    def half_degree(self):
        return Rational(1/2)
    
    def factored_conductor(self):
        return factor(self.conductor())
 
    def polredabs(self):
        return Polynomial("x^2+1")

MockupNumberField().fingerprint("polredabs", "pymongo")
 

from astropy import units as u
import sympy as s
import sympy as sym
from IPython.display import display, Math
s.init_printing()

pm = chr(177)

class EQ:
    def __init__(self, value:float, error:float, unit:u.Quantity, name:str=None, symbol:str='not_set'):
        self.value = value * unit
        self.error = error * unit
        self.unit = unit
        self.name = name
        self.symbol = sym.Symbol(symbol)

    def __mul__(self:EQ, other:EQ):
        left_value = self.value.to(u.meter)
        left_error = self.error.to(u.meter)

        right_value = other.value.to(u.meter)
        right_error = other.error.to(u.meter)

        result_value = left_value * right_value 
        result_error = result_value * ((left_error / left_value) + (right_error / right_value))
        
        return EQ(result_value.value, result_error, result_value.unit)

    def __str__(self):
        return f"{self.name} = ({self.value.value} \xb1 {self.error.value}) {self.unit}"
        
def measure_object(cls):
    
    def __str__(self):
        member_variables = [x for x in dir(self) if not '__' in x]

        string:str = f"-----------{cls.__name__}---------------\n"

        for member in member_variables:
            string = f"{string} {EQ.__str__(getattr(cls, member))} \n"
        
        return string + '-----------------------------'
    
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self.__class__, key, kwargs[key])
            value.name = key
            
            

            
    cls.__str__ = __str__   
    cls.__init__ = __init__
    return cls


def error_formula(str_f:str):
    f = s.sympify(str_f)
    symbols = f.free_symbols
    block_exprs = []

    for sym in symbols:
        del_sym = s.diff(f, sym)
        d_sym = s.symbols('\\sigma' + str(sym))
        block_exprs.append(del_sym**2 * d_sym**2)

    return s.sqrt(sum(block_exprs)) 
        


@measure_object
class Sun:
    pass
    
sun = Sun(diameter = EQ(100, 50, u.m),
          lum = EQ(10, 2, u.watt))


print(sun)
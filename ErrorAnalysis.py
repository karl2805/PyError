from astropy import units as u
import sympy as s
import sympy as sym
from IPython.display import display, Math
s.init_printing()

pm = chr(177)



class EQ(object):
    def __init__(self, value:float, error:float, unit:u.Quantity, name:str=None, symbol:str='?'):
        self._value = value * unit
        self._error = error * unit
        self.unit = unit
        self.name = name
        self.symbol = sym.Symbol(symbol)

    def __mul__(self, other):
        """
        Multiples two EQ objects togeater
        Uses the error propogation formula for error
        """
        if not isinstance(other, EQ):
            return NotImplemented
        
        left_value = self._value
        left_error = self._error

        right_value = other._value
        right_error = other._error

        result_value = left_value * right_value 
        result_error = result_value * ((left_error / left_value) + (right_error / right_value))
        
        return EQ(result_value.value, result_error, result_value.unit)
    
    def _check_units(self):
        if not self._value.unit == self._error.unit == self.unit:
            raise Exception("EQ object unit mismatch") 
        
    
    def si(self):
        """
        Convert the EQ to SI units
        """
        return EQ(self._value.si.value, self._error.si.value, self._value.si.unit, self.name)
        
    def __str__(self):
        return f"{self.name} = ({self._value.value} \xb1 {self._error.value}) {self.unit}"
 
 
def error_formula(str_f:str) -> sym.Expr:
    f = s.sympify(str_f)
    symbols = f.free_symbols
    block_exprs = []

    for sym in symbols:
        del_sym = s.diff(f, sym)
        d_sym = s.symbols('\\sigma' + str(sym))
        block_exprs.append(del_sym**2 * d_sym**2)

    return s.sqrt(sum(block_exprs))    
    
def compute_expression(expr:str, **kwargs:EQ):
    error_expr = error_formula(expr)
    symbols = sym.symbols(list(map(str, kwargs.keys())))
    print(type(symbols))
    
    
whatever = compute_expression('x + y + 2 * 3', x=2, y=3, test=3)    
    
        
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



        


@measure_object
class Sun:
    pass
    
sun = Sun(diameter = EQ(100, 50, u.m),
          lum = EQ(5, 2, u.watt))

test = sun.diameter * sun.lum
test.name = "test"
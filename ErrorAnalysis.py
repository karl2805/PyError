from astropy import units as u
import sympy as sym
from IPython.display import display, Math
sym.init_printing()

pm = chr(177)



class EQ(object):
    def __init__(self, value:float, error:float, unit:u.Quantity, name:str=None, symbol:str='?', error_formula:sym.Expr=None):
        self._value = value * unit
        self._error = error * unit
        self.unit = unit
        self.error_formula = error_formula
        self.name = name
        self.symbol = sym.Symbol(symbol)

    def __mul__(self, other):
        """
        Multiples two EQ objects togeater
        Uses the error propogation formula for error
        Not sure if this is really needed
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
    
    def __str__(self):
        return f"{self.name} = ({self._value.value} \xb1 {self._error.value}) {self.unit}"
    
    def _check_units(self):
        if not self._value.unit == self._error.unit == self.unit:
            raise Exception("EQ object unit mismatch") 
        
    def si(self) -> None:
        """
        Convert the EQ to SI units
        """
        return EQ(self._value.si.value, self._error.si.value, self._value.si.unit, self.name)
    
    def fvalue(self) -> float:
        """
        return the value as a float
        """    
        return self._value.value
    
    def qvalue(self) -> u.Quantity:
        """
        return the value as a quantity object
        """
        return self._value

    def ferror(self) -> float:
        """
        return the error as a float
        """
        return self._error.value
    
    def qerror(self) -> u.Quantity:
        """
        return the error as a quantity object
        """
        return self._error
    
    def get_unit(self) -> u.Unit:
        """
        return the unit
        """
        self._check_units()
        return self._value.unit
    
    def to(self, unit: u.Unit):
        """
        Switch Units    
        """
        self._value = self._value.to(unit)
        self._error = self._error.to(unit)
        self.unit = self._value.unit
        self._check_units()
 
 
def error_formula(str_f:str) -> sym.Expr:
    """Get the error formula of the inputted expression

    Args:
        str_f (str): The input expression to compute the error formula of.

    Returns:
        sym.Expr: The computed error formula as a sympy expression.
    """
    f = sym.sympify(str_f)
    symbols = f.free_symbols
    block_exprs = []

    for symbol in symbols:
        del_expr = sym.diff(f, symbol)
        delta_symbol = sym.symbols('sigma_' + str(symbol))
        block_exprs.append(sym.Abs(del_expr * delta_symbol))

    return sum(block_exprs)
    
def compute_expression(str_expr:str, name:str=None, symbol:str='?', if_dimensionless=u.dimensionless_unscaled, **kwargs:EQ | u.Quantity):
    """Returns a new EQ object with the value and error of the expression inputted

    Args:
        str_expr (str): The expression to compute
        name (str, optional): The name of the returned EQ. Defaults to None.

    Returns:
        EQ: The returned EQ object with the value and error of the computed expression
    """
    value_expr = sym.sympify(str_expr)
    error_expr = error_formula(str_expr)
    
    #if there are some quantity objects change them to EQ with no error
    for key, value in kwargs.items():
        if isinstance(value, u.Quantity):
            kwargs[key] = EQ(value.value, 0.0, value.unit)
            
    symbol_value_pairs = [(symbol, eq.fvalue()) for symbol, eq in kwargs.items()]
    symbol_error_pairs = [('sigma_' + symbol, eq.ferror()) for symbol, eq in kwargs.items()]
    
    value_symbols = sym.symbols(list(kwargs.keys()))
    compute_unit = sym.lambdify(value_symbols, value_expr, 'math')
    
    units = [eq.get_unit() for eq in kwargs.values()]
    
    value_result = value_expr.subs(symbol_value_pairs)
    error_result = error_expr.subs(symbol_value_pairs + symbol_error_pairs)
    unit_result = compute_unit(*units)
    
    #if there are literals (Quantity Objects with not error) in the unit_result get rid of them
    if isinstance(unit_result, u.Quantity):
        unit_result = unit_result.unit
    
    if unit_result == u.dimensionless_unscaled:
        unit_result = if_dimensionless
    
    
    return EQ(value_result, error_result, unit_result, name, symbol, error_formula=error_expr)
    
    
def latex_err(error_expr: sym.Expr):
    """Convert an error expression to latex for printing. Only to be used on error formulas!

    Args:
        error_expr (sym.Expr): The error formula.

    Returns:
        _type_: The error formula to print
    """
    expr_str = str(error_expr)
    no_abs = expr_str.replace("Abs", '')
    return sym.latex(sym.sympify(no_abs))

        
def measure_object(cls):
    
    #I want the ---s to be the length of the longest output and have the name of the measure_object in the center.
    #Shouldn't be too difficult to do
    def __str__(self):
        member_variables = [x for x in dir(self) if not '__' in x]

        string:str = f"---------------{cls.__name__}---------------\n"

        for member in member_variables:
            string = f"{string} {EQ.__str__(getattr(self, member))} \n"
        
        return string + '-' * (30 + len(cls.__name__))
    
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self.__class__, key, kwargs[key])
            value.name = key
            
    cls.__str__ = __str__   
    cls.__init__ = __init__
    return cls

 
#this prevents this code block from running if this file is imported to another file
if __name__ == "__main__":
    @measure_object
    class Sun:
        pass

    @measure_object
    class Measurements:
        pass

    e_sun_angular_size = "(1 / m) * (d / D)"
    e_sun_radius = "0.5 * theta * AU"

    m = Measurements()
    m.D = EQ(8.5, 0.2, u.cm, "Distance to Screen", "D")
    m.d = EQ(1.4, 0.1, u.cm, "Diameter of Sun Projection", "d")
    m.F = EQ(350, 1, u.mm, "Telescope Focal Length", "F")
    m.f = EQ(20, 1, u.mm, "Lens Focal Length", "f")
    m.m = compute_expression("F / f", "Telescope Magnification", "m", F=m.F, f=m.f)

    sun = Sun()
    sun.AngularSize = compute_expression(e_sun_angular_size, "Angular Size", if_dimensionless=u.rad, m=m.m, d=m.d, D=m.D)
    test = sun.AngularSize
    
    #added functionality to let contant values like AU be passed in without being an EQ object
    #the outputted unit for this radius is wrong because its being carried over from the angular size. 
    #angles are weird because they're sort of dimensionless, needs to be fixed. In astropy there is a thing called dimensionless_angles()
    #which seems to be the way to fix it.
    sun.Radius = compute_expression(e_sun_radius, "Radius", 'R', theta=sun.AngularSize, AU=1.5e11*u.meter)

    temp = sun.Radius.fvalue()
    temp = temp * u.meter
    
    temp2 = sun.Radius.ferror()
    temp2 = temp2 * u.meter
    
    print(m)
    print(sun)
    
    #Needs improvement
    #the error formula prints with \sigma_{AU} which is zero so the code should remove it. Needs to be fixed
    print("Angular Size Error Formula:", latex_err(error_formula(e_sun_radius)))
    print("Radius Error Formula:", latex_err(error_formula(e_sun_radius)))







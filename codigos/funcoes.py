import numpy as np



def retangular(t_axis,T):
    
    '''
    s(t) = Pi (t/T)
    
    t_axis -> array com valores dos instantes de tempo 
    T      -> largura do pulso retangular
    
    '''
    
    s = [1 if abs(t/T) < 1/2 else 0 for t in t_axis]
    return s


def triangular(t_axis,T):
    
    
    s = [ -abs(t) + 1 if abs(t/T) < 1 else 0 for t in t_axis ]
    
    return s


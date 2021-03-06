"""
This file implements the class for Euler's equation.

This includes a source term to model a toy star, and an atmosphere.
"""

import numpy


class EulerToyStar(object):
    
    def __init__(self, gamma=2, rho_atmosphere=1e-6, e_atmosphere=1e-6):
        assert gamma == 2
        self.gamma = gamma
        self.rho_atmosphere = rho_atmosphere
        self.e_atmosphere = e_atmosphere
        
    def p_from_eos(self, rho, e):
        return (self.gamma - 1.0) * rho * e
    
    def p2c(self, rho, v, e):
        q = numpy.zeros([len(rho), 3])
        # Impose atmosphere based on rho
        v[rho < self.rho_atmosphere] = 0
        e[rho < self.rho_atmosphere] = self.e_atmosphere
        rho[rho < self.rho_atmosphere] = self.rho_atmosphere
        # Impose atmosphere based on e
        v[e < self.e_atmosphere] = 0
        rho[e < self.e_atmosphere] = self.rho_atmosphere
        e[e < self.e_atmosphere] = self.e_atmosphere
        q[:, 0] = rho
        q[:, 1] = rho*v
        q[:, 2] = rho*(e + v**2/2)
        return q
    
    def c2p(self, q):
        rho = q[:, 0]
        S = q[:, 1]
        E = q[:, 2]
        # Impose atmosphere based on rho
        S[rho < self.rho_atmosphere] = 0
        E[rho < self.e_atmosphere * self.rho_atmosphere] = self.e_atmosphere * self.rho_atmosphere
        rho[rho < self.rho_atmosphere] = self.rho_atmosphere
        v = S / rho
        e = E / rho - v**2 / 2
        # Impose atmosphere based on e
        rho[e < self.e_atmosphere] = self.rho_atmosphere
        v[e < self.e_atmosphere] = 0
        e[e < self.e_atmosphere] = self.e_atmosphere
        p = self.p_from_eos(rho, e)
        cs = numpy.sqrt(self.gamma * p / rho)
        return rho, v, e, p, cs
        
    def flux(self, q):
        # rho = q[:, 0, :]
        S = q[:, 1]
        E = q[:, 2]
        _, v, _, p, _ = self.c2p(q)
        f = numpy.zeros_like(q)
        f[:, 0] = S
        f[:, 1] = S * v + p
        f[:, 2] = (E + p) * v
        return f
    
    def source(self, q, x):
        rho, v, _, _, _ = self.c2p(q)
        s = numpy.zeros_like(q)
        s[:, 1] = -rho * x
        s[:, 2] = -rho * v * x
        return s
    
    def max_lambda(self, q):
        _, v, _, _, cs = self.c2p(q)
        return numpy.max(numpy.abs(v)) + numpy.max(numpy.abs(cs))
    

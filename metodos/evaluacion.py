#se deben crear 2 horners doble(no se bien si otro de horner simple), uno q use fraction y otro q use float. para precision exacta(fraction) en la evaluacion normal
# el de float se va a usar en el metodo de newton-halley
from fractions import Fraction
from core.polinomio import Polinomio
from core.resultado import Resultado

#por las dudas D:
def evaluacion_directa(p: Polinomio,alpha) -> Resultado:
    alpha=Fraction(alpha)
    ac = Fraction(0)
    pasos=[]
    n = p.grado
    coef = p.coef
    for i in range(n + 1):
        potencia = alpha ** i
        termino = coef[i] * potencia
        ac += termino
        pasos.append({"i":i,"coef":coef[i],"potencia":potencia,"termino":termino,"acumulado":ac})
    return Resultado(valor=ac,pasos=pasos)

def horner_fraction(p: Polinomio,alpha) -> Resultado:
    alpha=Fraction(alpha)
    a = p.coef
    n = p.grado
    b = [Fraction(0)] * (n + 1) #lista [0,0,0,0...,0]
    b[n]=a[n] #" baja " el coeficiente principal je
    for i in range(n-1,-1,-1): #si ponemos hasta 0 no entraria al b[0] D:
        b[i]= a[i] + ( alpha*b[i+1] )
    paso = {"alpha": alpha, "a": list(a), "b": b}
    return Resultado(valor=b[0], pasos=[paso])

def horner_float(p: Polinomio,alpha: float) -> Resultado:
    a = p.a_float()
    alpha = float(alpha) # nos aseguramos d q sea float por si mandan un entero D:
    n = p.grado
    b = [0.0] * (n + 1)  # lista [0,0...,0]
    b[n] = a[n]  # " baja " el coeficiente principal je
    for i in range(n - 1, -1, -1):  # si ponemos hasta 0 no entraria al b[0] D:
        b[i] = a[i] + (alpha * b[i + 1])
    paso = {"alpha": alpha, "a": list(a), "b": b}
    return Resultado(valor=b[0], pasos=[paso])


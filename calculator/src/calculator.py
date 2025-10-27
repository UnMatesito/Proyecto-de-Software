def resta(a, b):
    return a - b

def suma(a, b):
    return a + b

def multiplicacion(a, b):
    return a * b

def division(a, b):
    try:
        result = a / b
        return result
    except ZeroDivisionError:
        print("No podes divir por 0")
        return None
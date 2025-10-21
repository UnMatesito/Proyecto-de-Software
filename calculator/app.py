from src import calculator


def menu_principal():
    while True:
        print("Seleccione una opción")
        print("1. Sumar.")
        print("2. Restar.")
        print("3. Multiplicar.")
        print("4. Dividir.")
        print("Para salir, ingrese cualquier otro número.")

        try:
            opcion = int(input("Seleccione operación: "))
        except ValueError:
            print("Debe ingresar un número.\n")
            continue

        if opcion not in (1, 2, 3, 4):
            break

        procesar_opcion(opcion)


def procesar_opcion(opcion):
    try:
        valor_a = float(input("Valor A: "))
        valor_b = float(input("Valor B: "))
    except ValueError:
        print("Debe ingresar un número.\n")
        return

    match opcion:
        case 1:
            print(f"Resultado: {calculator.suma(valor_a, valor_b)}\n")
        case 2:
            print(f"Resultado: {calculator.resta(valor_a, valor_b)}\n")
        case 3:
            print(f"Resultado: {calculator.multiplicacion(valor_a, valor_b)}\n")
        case 4:
            if valor_b == 0:
                print("No se puede dividir por 0.\n")
                return
            print(f"Resultado: {calculator.division(valor_a, valor_b)}\n")


if __name__ == '__main__':
    menu_principal()
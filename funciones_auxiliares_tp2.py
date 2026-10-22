import numpy as np

# Funcionrd provistas

def huffman_code(prob_dict: dict[int, float]) -> dict[int, str]:
    """
    Genera un código Huffman a partir de las probabilidades dadas en el 
    diccionario "prob_dict" 
    Argumentos:
    --prob_dict: Diccionario que asocia cada símbolo con su probabilidad
    Retorno:
    --Retorna un diccionario con el código de Huffman para cada símbolo
    """
    # Crear lista de nodos: cada nodo es (probabilidad, símbolo o subárbol)
    nodes = [(p, {char: ''}) for char, p in prob_dict.items()]

    while len(nodes) > 1:
        # Ordenar nodos por probabilidad
        nodes = sorted(nodes, key=lambda x: x[0])

        # Tomar los dos de menor probabilidad
        p1, c1 = nodes.pop(0)
        p2, c2 = nodes.pop(0)

        # Agregar prefijo 0 al primer subárbol y 1 al segundo
        c1 = {k: '0' + v for k, v in c1.items()}
        c2 = {k: '1' + v for k, v in c2.items()}

        # Fusionar los dos subárboles
        new_node = (p1 + p2, c1 | c2)
        nodes.append(new_node)

    # Retornar el diccionario con el código final (nodes: list[tuple[int, dict]])
    return nodes[0][1]


def huffman_decode(bits: str, codigo: dict[int, str]) -> list[int]:
    """
    Decodifica una secuencia de bits usando un código de Huffman.
    Argumentos:
    --bits: Cadena de bits codificados.
    --codigo: Diccionario que asocia cada símbolo con su código Huffman.
    Retorno:
    --Lista de símbolos decodificados.
    """
    inverso = {}
    for simbolo, cod in codigo.items():
        inverso[cod] = simbolo

    simbolos = []
    actual = ''
    for bit in bits:
        actual += bit
        if actual in inverso:
            simbolos.append(inverso[actual])
            actual = ''

    if actual != '':
        raise ValueError("La secuencia termina con un código incompleto.")
        
    return simbolos
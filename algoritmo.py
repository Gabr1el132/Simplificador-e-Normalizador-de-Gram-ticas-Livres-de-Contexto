import re
from copy import deepcopy
from collections import defaultdict

def ler_gramatica(texto):
    gramatica = defaultdict(list)
    for linha in texto.strip().split("\n"):
        if "->" in linha:
            esquerda, direitas = linha.split("->")
            esquerda = esquerda.strip()
            producoes = [p.strip() for p in direitas.split("|")]
            gramatica[esquerda].extend(producoes)
    return dict(gramatica)

def is_terminal(s):
    return all(c.islower() or not c.isalpha() for c in s)

def imprimir_gramatica(titulo, G):
    print(f"\n=== {titulo} ===")
    for nt in sorted(G.keys()):
        print(f"{nt} -> {' | '.join(G[nt])}")

def remover_inuteis_inalcancaveis(G, inicial):
    G = deepcopy(G)
    geram_terminais = set()
    mudou = True
    while mudou:
        mudou = False
        for A in G:
            for prod in G[A]:
                if all(is_terminal(c) or c in geram_terminais for c in prod):
                    if A not in geram_terminais:
                        geram_terminais.add(A)
                        mudou = True
    G = {A: [p for p in G[A] if all(is_terminal(c) or c in geram_terminais for c in p)]
         for A in G if A in geram_terminais}
    alcancaveis = set()
    fila = [inicial]
    while fila:
        A = fila.pop()
        if A not in alcancaveis:
            alcancaveis.add(A)
            for prod in G.get(A, []):
                fila.extend([c for c in prod if c.isupper()])
    G = {A: [p for p in G[A] if A in alcancaveis] for A in G if A in alcancaveis}
    return G

def remover_vazias(G, inicial):
    G = deepcopy(G)
    anulaveis = set()
    mudou = True
    while mudou:
        mudou = False
        for A in G:
            for prod in G[A]:
                if prod == "" or all(c in anulaveis for c in prod):
                    if A not in anulaveis:
                        anulaveis.add(A)
                        mudou = True
    novas_producoes = defaultdict(set)
    for A in G:
        for prod in G[A]:
            indices = [i for i, c in enumerate(prod) if c in anulaveis]
            total = 2 ** len(indices)
            for i in range(total):
                nova = list(prod)
                for bit, idx in enumerate(indices):
                    if (i >> bit) & 1:
                        nova[idx] = ""
                nova_str = "".join(nova)
                if nova_str != "":
                    novas_producoes[A].add(nova_str)
            if all(c in anulaveis for c in prod):
                novas_producoes[A].add("")
    return {A: list(ps) for A, ps in novas_producoes.items()}

def remover_unitarias(G):
    G = deepcopy(G)
    novas = defaultdict(set)
    for A in G:
        novas[A].update(G[A])
    for A in G:
        fila = [A]
        visitados = set()
        while fila:
            B = fila.pop()
            for prod in G.get(B, []):
                if len(prod) == 1 and prod.isupper():
                    if prod not in visitados:
                        fila.append(prod)
                        visitados.add(prod)
                else:
                    novas[A].add(prod)
    return {A: list(prods) for A, prods in novas.items()}

def fnc(G):
    G = deepcopy(G)
    novos = {}
    contador = 1
    terminais = {}
    for A in G:
        novas_prods = []
        for prod in G[A]:
            nova = ""
            for c in prod:
                if is_terminal(c) and len(prod) > 1:
                    if c not in terminais:
                        nome = f"T{contador}"
                        contador += 1
                        terminais[c] = nome
                        novos[nome] = [c]
                    nova += terminais[c]
                else:
                    nova += c
            novas_prods.append(nova)
        G[A] = novas_prods
    while True:
        alterado = False
        for A in list(G.keys()):
            novas_prods = []
            for prod in G[A]:
                if len(prod) > 2:
                    x = prod
                    while len(x) > 2:
                        Y = f"X{contador}"
                        contador += 1
                        novos[Y] = [x[:2]]
                        x = Y + x[2:]
                    novas_prods.append(x)
                    alterado = True
                else:
                    novas_prods.append(prod)
            G[A] = novas_prods
        if not alterado:
            break
    G.update(novos)
    return G

def fng(G):
    G = deepcopy(G)
    novas = defaultdict(list)
    for A in G:
        for prod in G[A]:
            if is_terminal(prod[0]):
                novas[A].append(prod)
            else:
                novas[A].append("a" + prod)
    return novas

def fatorar(G):
    G = deepcopy(G)
    novas = {}
    for A in G:
        prefixos = defaultdict(list)
        for prod in G[A]:
            prefixos[prod[0]].append(prod)
        if len(prefixos) < len(G[A]):
            novas_prods = []
            for p in prefixos:
                if len(prefixos[p]) > 1:
                    nome = A + "'"
                    resto = [x[1:] if len(x) > 1 else "" for x in prefixos[p]]
                    novas[nome] = resto
                    novas_prods.append(p + nome)
                else:
                    novas_prods.append(prefixos[p][0])
            G[A] = novas_prods
    G.update(novas)
    return G

def remover_recursao_esquerda(G):
    G = deepcopy(G)
    novas = {}
    for A in list(G.keys()):
        diretas = [p for p in G[A] if p.startswith(A)]
        indiretas = [p for p in G[A] if not p.startswith(A)]
        if diretas:
            A1 = A + "'"
            novas[A] = [p + A1 for p in indiretas]
            novas[A1] = [p[len(A):] + A1 for p in diretas] + [""]
        else:
            novas[A] = G[A]
    return novas

entrada = """
S -> aAa | bBv
A -> a | aA
"""

inicial = "S"
G = ler_gramatica(entrada)
imprimir_gramatica("Gramática Original", G)

G1 = remover_inuteis_inalcancaveis(G, inicial)
imprimir_gramatica("1. Após remoção de símbolos inúteis/inalcançáveis", G1)

G2 = remover_vazias(G1, inicial)
imprimir_gramatica("2. Após remoção de produções vazias", G2)

G3 = remover_unitarias(G2)
imprimir_gramatica("3. Após substituição de produções unitárias", G3)

G4 = fnc(G3)
imprimir_gramatica("4. Forma Normal de Chomsky (FNC)", G4)

G5 = fng(G4)
imprimir_gramatica("5. Forma Normal de Greibach (FNG, esboço)", G5)

G6 = fatorar(G5)
imprimir_gramatica("6. Após fatoração à esquerda", G6)

G7 = remover_recursao_esquerda(G6)
imprimir_gramatica("7. Após remoção de recursão à esquerda", G7)

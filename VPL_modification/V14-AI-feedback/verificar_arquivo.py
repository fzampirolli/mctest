import re
import sys


def verificar_expressao(expressao, dotall=True):
    qtd = 0
    if dotall:
        matches = re.finditer(expressao, texto_codigo, re.MULTILINE|re.DOTALL)
    else:
        matches = re.finditer(expressao, texto_codigo, re.MULTILINE)
    for match in matches:
        if qtd == 0:
            print("\nErros:")
        qtd += 1
        inicio, fim = texto_codigo[0:match.start()].count("\n") + 1, texto_codigo[0:match.end()].count("\n") + 1
        print("  ({0}-{1}): {2}".format(inicio, fim, match.group()))
    return (qtd == 0)

def remover_expressao(texto_codigo, expressao, texto_novo):
    return re.sub(expressao, texto_novo, texto_codigo) # deve ser sem dotall para os comentarios #


arg_arquivo = str(sys.argv[1])
#print(">>>>", sys.argv[1])

texto_codigo = ""
try:
    arquivo_codigo = open(arg_arquivo, 'r')
    texto_codigo = arquivo_codigo.read()
except:
    print("arquivo não existe: ", str(sys.argv[1]).split(".")[0])
    sys.exit(1)
    #arquivo_codigo.close()


# """
patternStringMultiLinha = r"(\"\"\")|(\'\'\')"
if not verificar_expressao(patternStringMultiLinha):
    erro = True
    print("Nao eh permitido utilizar \"\"\" ou \'\'\'")
    sys.exit(0)


# remover strings
texto_codigo = remover_expressao(texto_codigo, r"[rf]*\".+?\"", "\"texto\"") # aspas duplas
texto_codigo = remover_expressao(texto_codigo, r"[rf]*\'.+?\'", "\"texto\"") # aspa simples

# remover comentarios
texto_codigo = remover_expressao(texto_codigo, "\\#.+", "")

erro = False

# del lista[indice]
# del(), max(), min(), sum(), reversed(), sort(), sorted()
# cmp(), filter(), map(), enumerate(), iter(), repr(), slice(), zip(), all()
patternFuncoesListas = r"(del +)|([ \\\n\(]+(del|max|min|sum|reversed|sorted|sort|cmp|filter|map|enumerate|iter|repr|slice|zip|all)[ \\\n]*\()"
if not verificar_expressao(patternFuncoesListas):
    erro = True
    print("Funcoes nao permitidas:")
    print("  del lista[indice], del(), max(), min(), sum(), reversed(), sort(), sorted(), cmp(), filter(), map(), enumerate(), iter(), repr(), slice(), zip(), all()\n")

# lista += [elemento], lista = lista + [elemento]
patternOperadorListas = r"(\+=[ \\\n]*\[)|(\+[ \\\n]*\[)"
if not verificar_expressao(patternOperadorListas):
    erro = True
    print("Nao eh permitido adicionar elementos em lista: lista += [elemento]")    
  
   
# funcoes em listas (exceto .format() e .split())
patternMetodosObjetos = r"([a-zA-Z_\'\"]+[a-zA-Z0-9_()]*\.[ \\\n]*(?!format|split|sqrt|open|read)[a-zA-Z_]+[a-zA-Z0-9_()]*)"
if not verificar_expressao(patternMetodosObjetos):
    erro = True
    print("Nao eh permitido usar metodos prontos.\n")
    
# in lista (exceto in range())
patternIn = r"( +[ \\\n]*in +[ \\\n]*(?!(range[ \\\n]*\())[a-zA-Z_]+[a-zA-Z0-9_()]*)"
if not verificar_expressao(patternIn):
    erro = True
    print("Nao eh permitido usar in (excecao: for .. in range..).\n")

# sublista [indice1:indice2], [indice1:], [:indice2], [:], [::indice]
patternSublista = r"(\[[ \\\n]*[a-zA-Z0-9_()]*\:+[ \\\n]*-*[a-zA-Z0-9_()]*\])"
if not verificar_expressao(patternSublista):
    erro = True
    print("Nao eh permitido usar [indice1:indice2], [indice1:], [:indice2], [:], [::indice]\n")
    
# (*lista) expressao com * em lista
patternStarredUnpack = r"([\=\(][ \\\n]*(\*)+[a-zA-Z0-9_()]+)"
if not verificar_expressao(patternStarredUnpack):
    erro = True
    print("Nao eh permitido usar expressao com * em lista, por exemplo: (*lista)\n")
    
# a op1 b op2 c, op1 e op2 em [<, >, <=, >=, !=, ==] - por exemplo: a < b < c
patternCondicionais = r"([a-zA-Z0-9_()]+[ \\\n]*(\<|\>|\<=|\>=|\!\=|==)+[ \\\n]*[a-zA-Z0-9_()]+[ \\\n]*(\<|\>|\<=|\>=|\!\=|==))"
if not verificar_expressao(patternCondicionais):
    erro = True
    print("Nao eh permitido usar: a op1 b op2 c, em que op1 e op2 podem ser [<, >, <=, >=, !=, ==] - por exemplo: a < b < c\n")
    
# a, b = b, a
patternSwap = r"([a-zA-Z_]+[a-zA-Z0-9_]*[ \\\n]*,[ \\\n]*[a-zA-Z_]+[a-zA-Z0-9_]*[ \\\n]*=[ \\\n]*[a-zA-Z_]+[a-zA-Z0-9_]*[ \\\n]*,[ \\\n]*[a-zA-Z_]+[a-zA-Z0-9_]*)"
if not verificar_expressao(patternSwap):
    erro = True
    print("Nao eh permitido realizar troca de valores da seguinte forma: a, b = b, a\n")
    
# global
patternGlobal = r"([ \\\n]+global[ \\\n]+[a-zA-Z_]+[a-zA-Z0-9_()]*)"
if not verificar_expressao(patternGlobal):
    erro = True
    print("Nao eh permitido usar global\n")
    
# lambda
patternLambda = r"([ \\\n\(]+lambda[ \\\n]+)"
if not verificar_expressao(patternLambda):
    erro = True
    print("Nao eh permitido usar lambda\n")

# import
patternImport = r"(import[ \\\n]+(?!math))"
if not verificar_expressao(patternImport):
    erro = True
    print("Nao eh permitido usar import (apenas import math pode ser utilizado)\n")

# asterisco para formar strings
patternMultiString = r"\".+?\" *\*"
if not verificar_expressao(patternMultiString, dotall=False):
    erro = True
    print("Nao eh permitido usar asterisco para formar strings, por exemplo: \"texto\" * 5 \n")

    
if erro:
    sys.exit(0)
else:
    sys.exit(1)
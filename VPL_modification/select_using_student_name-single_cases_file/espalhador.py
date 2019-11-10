# /usr/bin/python3.6

import sys
import string
import unicodedata

D = {}
for c in string.ascii_lowercase:
	D[c] = string.ascii_lowercase.find(c)+1

for c in string.ascii_uppercase:
	D[c] = string.ascii_uppercase.find(c)+1

def distro_table(nome): # Versão H

	hash_base_B = 0; # Equivalente ao calculo da versão B
	hash_base_C = 0; # Equivalente ao calculo da versão C
	hash_base_D = 0; # Equivalente ao calculo da versão D
	hash_base_E = 0; # Equivalente ao calculo da versão E

	for c in nome:
		hash_base_B *= 100
		hash_base_B += D[c]
		hash_base_C += int(len(string.ascii_lowercase)**D[c])

	hash_base_E = hash_base_B
	hash_base_D = hash_base_C
	hash_base_C %= int(1e10)

	hash_base_B **= len(string.ascii_lowercase)
	hash_base_E **= len(string.ascii_lowercase)

	for c in nome:
		hash_base_E += int(len(string.ascii_lowercase)**D[c])

	while hash_base_B > int(1e10):
		a = hash_base_B % int(1e10)
		hash_base_B //= int(1e10)
		hash_base_B += a

	while hash_base_D > int(1e10):
		a = hash_base_D % int(1e10)
		hash_base_D //= int(1e10)
		hash_base_D += a

	while hash_base_E > int(1e10):
		a = hash_base_E % int(1e10)
		hash_base_E //= int(1e10)
		hash_base_E += a

	return (hash_base_B+hash_base_C+hash_base_D+5*hash_base_E)//8

# for line in sys.stdin:
#     nome = unidecode.unidecode(line.split()[0])

#     print(nome,end="\t")
#     print(distro_table(nome),end="\n")

nome = input()

nome = unicodedata.normalize('NFKD', nome).encode('ascii','ignore').decode('ascii').split()[0]

# print(nome,end="\t")
print(distro_table(nome),end="\n")
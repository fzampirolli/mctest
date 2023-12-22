# MCTest + VPL Moodle - versão 4.1
Autor(es):
* Francisco de Assis Zampirolli

1. Não usa mais o makefile para descompactar o zip. Os arquivos deste zip já estão nesta pasta.

2. Criar uma atividade VPL "modelo" com todos os arquivos desta pasta. 

3. Ao criar uma nova atividade VPL, utilizar a opção "baseado em" para essa atividade "modelo", em "opções de execução" da atividade VPL do Moodle.

4. Em "Opções de execução", fazer upload dos arquivos "linker.json" e "students_variations.vpl", gerados por MCTest.

vpl_run.sh 
  linguagens para avaliações
  txt - para teste de mesa

se txt:
  vpl_main.py
  vpl_mctest.py
  vpl_utils.py

Arquivos adaptados da versão 12 (https://github.com/fzampirolli/mctest/tree/master/VPL_modification/V12-trace_test) 
criada originalmente pelo Heitor Rodrigues Savegnago e seu orientador Prof. Dr. Paulo Henrique Pisani

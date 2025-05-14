# MCTest + VPL Moodle - versão 4.1

Autores:

* Heitor Rodrigues Savegnago (até v10)
* Paulo Henrique Pisani (até v10)
* Fernando Teubl (v12)
* Francisco de Assis Zampirolli

Arquivos adaptados da versão 12 (https://github.com/fzampirolli/mctest/tree/master/VPL_modification/V12-trace_test).

1. Não usa mais o makefile para descompactar o zip. Os arquivos deste zip já estão nesta pasta.

2. Criar uma atividade VPL "modelo" com todos os arquivos desta pasta.

3. Ao criar uma nova atividade VPL, utilizar a opção "baseado em" para essa atividade "modelo", em "opções de execução"
   da atividade VPL do Moodle.

4. Em "Opções de execução", fazer *upload* dos arquivos `linker.json` e `students_variations.vpl`, gerados pelo MCTest.

* vpl_run.sh
  * linguagens para avaliações
  * txt - para teste de mesa

* se txt (v12):
  * vpl_main.py
  * vpl_mctest.py
  * vpl_utils.py

* V13: 
  * compatível com Moodle v4.1
  * `students_variations.csv` 
    * agora também com email: Nome, Email, Variação
    * a chave é o email
    

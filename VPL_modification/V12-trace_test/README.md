# MCTest + VPL Integration + Trace Table


## Paper:

Teubl, F.; Zampirolli, F. A. Automated Correction for Trace Tables in a CS1 Course. 
In: Simpósio Brasileiro de Informática na Educação (SBIE), 2023, Passo Fundo. CBIE, 2023.

Não usa mais o makefile para descompactar o zip. Os arquivos deste zip já estão nesta pasta.

## Passo-a-passo

1. Criar uma atividade VPL "modelo" oculta com todos os arquivos desta pasta.

2. Ao criar uma nova atividade VPL, utilizar a opção "baseado em" 
   para essa atividade "modelo", em "opções de execução" da atividade VPL do Moodle.

3. Em "Opções de execução", fazer upload dos arquivos `linker.json` 
   e `students_variations.vpl`, gerados por MCTest.

`vpl_run.sh` 
 - linguagens para avaliações 
 - txt para teste de mesa

se txt, processa: 
 - `vpl_main.py` 
 - `vpl_mctest.py` 
 - `vpl_utils.py`

Arquivos adaptados da versão 10 (https://github.com/fzampirolli/mctest/tree/master/VPL_modification/V10-new_selector) 
criados pelo Heitor Rodrigues Savegnago e o seu orientador Prof. Dr. Paulo Henrique Pisani
# MCTest: Como Criar e Corrigir Exames Parametrizados Automaticamente

---
> Autor: Francisco de Assis Zampirolli </br>
> ISBN: 978-65-00-79086-3 ([CBL](https://www.cblservicos.org.br/isbn/)) </br>
> Ano: 2023
---

Este livro reúne e consolida as publicações disponibilizadas 
no endereço [vision.ufabc.edu.br](http://vision.ufabc.edu.br), 
especialmente aquelas em que o mesmo autor principal esteve envolvido. 
Para obter mais informações, consulte o prefácio do livro.

---
## Formatos do livro

Fazer *download* para visulizar melhor.

### Versão digital:

* PDF: [livro.pdf](https://github.com/fzampirolli/mctest/blob/master/book/1ed-br/livro.pdf)
* HTML: [livro.html](https://github.com/fzampirolli/mctest/blob/master/book/1ed-br/livro.html)
* EPUB: [livro.epub](https://github.com/fzampirolli/mctest/blob/master/book/1ed-br/livro.epub)

O formato EPUB altera muito o estilo do livro. 
Ainda não achei um conversor adequado para o estilo utilizado. 

[eBoox](https://play.google.com/store/apps/details?id=com.reader.books&hl=pt_BR&gl=US) 
 é o melhor visualizador de EPUB para Android que encontrei para este livro.

---
## Caso queira imprimir, seguem sugestões

### 1) Fábrica do Livro 
* https://www.fabricadolivro.com.br/

#### Fornecer as seguintes especificações

* Livro sem Orelha Capa 
* Lam. Fosca no Duo Design 250g 4x0 
* miolo impressão Frente e Verso - 21x29,7cm - 21x29,7 cm 
* Duo Design (Papel Cartão) 250g 
* Laminação Fosca
* páginas 244 - níveis de cinza

#### Valores
* R$ 209 - níveis de cinza (R$52,25 cada - mínimo de 4 cópias)
* R$ 452,40 - (91 pags coloridas e 153 pags em níveis de cinza - R$ 113,10 cada)
* Frete R$ 9 - motoboy São Paulo

#### Versão para impressão:
* [livro-capa21x29.7.pdf](https://github.com/fzampirolli/mctest/blob/master/book/1ed-br/livro-capa21x29.7.pdf)
* [livro-impressao11pt.pdf](https://github.com/fzampirolli/mctest/blob/master/book/1ed-br/livro-impressao11pt.pdf)
* [livro-impressao12pt.pdf](https://github.com/fzampirolli/mctest/blob/master/book/1ed-br/livro-impressao12pt.pdf)

O arquivo *12pt.pdf tem letras grandes, mas com pouca margem (superior, inferior e laterais).

### 2) Amazon.com

Disponível através do arquivo *11pt.pdf e miolo colorido na [Amazon](https://www.amazon.com/dp/B0CHL7DLKC?ref_=pe_3052080_397514860).

**Curiosidade:** O autor ganha 60% do valor - custo de impressão ($20,52). Optei por não lucrar com a venda:
- Lucro: 0,60 * $34,20 - $20,52 = $0,00
- Frete: $21,85

### 3) ?

---
## Como instalar o MCTest

Para instalar o [MCTest](https://github.com/fzampirolli/mctest), siga os passos abaixo:

1. **Instale o [VirtualBox](https://www.virtualbox.org/)**

2. **Instale o Ubuntu 22.04 no VirtulBox**

3. **No Ubuntu, execute os comandos no terminal**:

   ```bash
   sudo su
   wget https://raw.githubusercontent.com/fzampirolli/mctest/master/_setup-all.sh
   source _setup-all.sh

Isso fará o download do *script* de instalação e executará as configurações necessárias.

Aguarde a conclusão: Após alguns minutos, o processo estará concluído, e o MCTest será configurado.

Acesse o MCTest: Após a conclusão, abrir um navegador com URL http://127.0.0.1:8000.

Para mais detalhes e opções de configuração, consulte o arquivo [_setup-all.sh](https://raw.githubusercontent.com/fzampirolli/mctest/master/_setup-all.sh).

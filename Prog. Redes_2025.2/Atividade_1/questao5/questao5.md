Questão 5 - Problema do Troco

  Faça um programa que informa o nÃºmero mínimo de cédulas de cada valor de real a serem retornadas a um cliente de um restaurante que pagou uma conta. O programa recebe o valor da conta e o valor que o cliente pagou; exibe o nÃºmero de cédulas de cada valor que deve ser dado ao cliente.
  
  <br>**Versão 2**
  
  Mas agora temos outra questão. O caixa do restaurante não tem cédulas de todos os valores. Assim, antes de iniciar o processamento do troco, solicite a quantidade de cédulas disponível de cada valor. Agora, só informe o troco se houver cédulas suficientes; caso contrário, apresente a mensagem:
  
  ```
    O caixa não tem cédulas disponíveis para o troco!!!
  ```


  <br>**Versão 3**

  Além de verificar a quantidade de cédulas disponível de cada valor, ser forem suficientes, diminua-as do caixa, indicando que o troco foi dado.


  <br>**Versão 4**
  
  Faça com que seu programa tente outras formas de devolver o troco, quando certa combinação de cédulas não estiver disponível.

  Para melhor compreensão, considere a seguinte situação do caixa:

  ```
    ----------------------------------------
    Situação do caixa - Cédulas:
    ----------------------------------------
    # de cédulas de R$ 100: 2
    # de cédulas de R$ 50: 1
    # de cédulas de R$ 20: 3
    # de cédulas de R$ 5: 5
    # de cédulas de R$ 2: 6
    # de cédulas de R$ 1: 2
  ```

  Para um troco de R$ 218, a proposição inicial seria de:

  ```
    Troco - Cédulas:
    ----------------------------------------
    # de cédulas de R$ 100: 2
    # de cédulas de R$ 10: 1
    # de cédulas de R$ 5: 1
    # de cédulas de R$ 2: 1
    # de cédulas de R$ 1: 1
    ----------------------------------------
  ```

  Ocorre que não há notas de R$ 10 no caixa, gerando a mensagem:

  ```
    O caixa não tem cédulas disponíveis para o troco!!!
  ```
  
  Entretanto, é possível dar o troco, desde que as cédulas sejam:

  ```
    ----------------------------------------
    # de cédulas de R$ 100: 1
    # de cédulas de R$ 50: 1
    # de cédulas de R$ 20: 3
    # de cédulas de R$ 2: 4
    ----------------------------------------
  ```

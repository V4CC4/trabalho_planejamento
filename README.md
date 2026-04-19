# Trabalho 2 - Confiabilidade Composta

Pacote Python para calcular os indices `LOLP`, `LOLE`, `EPNS` e `EENS` do sistema do Trabalho 2 por:

- enumeracao completa dos estados;
- simulacao Monte Carlo nao sequencial.

## Hipoteses adotadas

- Sistema com `1` gerador de `600 MW` e `2` linhas de transmissao em paralelo de `400 MW` cada.
- Componentes modelados a `2` estados: operativo ou falho.
- Falhas estatisticamente independentes.
- Indisponibilidade estacionaria calculada por:
  - `lambda_h = lambda_ano / 8760`
  - `mu = 1 / r`
  - `q = lambda_h / (lambda_h + mu)`
- O gerador fica limitado pela curva de disponibilidade energetica do bloco.
- A oferta efetiva em cada bloco e:
  - `min(geracao_disponivel_no_bloco, capacidade_das_lts_ativas)`
- O corte de carga e:
  - `max(carga - oferta_efetiva, 0)`
- O ano foi modelado com `12` blocos de `730 h`.

## Formulas usadas

- `LOLP = sum(p_estado * peso_bloco * I[corte > 0])`
- `EPNS = sum(p_estado * peso_bloco * corte)`
- `LOLE = 8760 * LOLP`
- `EENS = 8760 * EPNS`

Na SMC nao sequencial, o bloco temporal e sorteado com probabilidade proporcional a sua duracao e o estado de cada componente e sorteado a partir da disponibilidade estacionaria. A saida reporta os coeficientes de variacao de `LOLP`, `LOLE`, `EPNS` e `EENS`, enquanto o criterio de parada continua usando o coeficiente de variacao do `EPNS`.

## Como executar

Sem instalar o pacote:

```bash
PYTHONPATH=src python3 -m pse_confiabilidade run --method enumeration
PYTHONPATH=src python3 -m pse_confiabilidade run --method smc --seed 42
PYTHONPATH=src python3 -m pse_confiabilidade run --method both
```

Ou abrir o notebook:

```bash
jupyter notebook notebooks/trabalho_2_confiabilidade.ipynb
```

Se preferir instalar em modo editavel:

```bash
python3 -m pip install -e .
python3 -m pse_confiabilidade run --method both
```

## Testes

```bash
python3 -m unittest discover -s tests -v
```

## Interpretacao do caso

Neste problema, a maior parte do risco vem da indisponibilidade do gerador, porque sua taxa de indisponibilidade e muito maior que a das linhas. As linhas afetam o resultado principalmente quando o gerador esta disponivel e a transmissao reduz a capacidade de entrega para `400 MW` ou `0 MW`.

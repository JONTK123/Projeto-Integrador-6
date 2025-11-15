# 📊 Métricas de Avaliação do Sistema de Recomendação

## Visão Geral

O sistema agora calcula **múltiplas métricas** durante o treinamento para avaliar a qualidade do modelo de forma abrangente. Todas as métricas são registradas automaticamente no MLflow.

---

## 🎯 Métricas Implementadas

### 1. Precision@K

**O que mede:** Quantos dos itens recomendados são realmente relevantes.

**Fórmula:** `Precision@K = (Itens relevantes nos top K) / K`

**Interpretação:**
- **Alto (próximo de 1.0)**: A maioria das recomendações é relevante
- **Baixo (próximo de 0.0)**: Muitas recomendações não são relevantes

**Valores calculados:**
- `test_precision@5`: Precision nas top 5 recomendações
- `test_precision@10`: Precision nas top 10 recomendações
- `test_precision@20`: Precision nas top 20 recomendações

**Exemplo:**
- Se você recomenda 10 estabelecimentos e 7 são relevantes: Precision@10 = 0.7

---

### 2. Recall@K

**O que mede:** Quantos dos itens relevantes foram recuperados nas recomendações.

**Fórmula:** `Recall@K = (Itens relevantes nos top K) / (Total de itens relevantes)`

**Interpretação:**
- **Alto (próximo de 1.0)**: O modelo encontra a maioria dos itens relevantes
- **Baixo (próximo de 0.0)**: O modelo perde muitos itens relevantes

**Valores calculados:**
- `test_recall@5`: Recall nas top 5 recomendações
- `test_recall@10`: Recall nas top 10 recomendações

**Exemplo:**
- Se existem 20 estabelecimentos relevantes e você recomenda 10, encontrando 8: Recall@10 = 0.4

---

### 3. F1-Score@K

**O que mede:** Média harmônica entre Precision e Recall (balanceamento).

**Fórmula:** `F1@K = 2 × (Precision@K × Recall@K) / (Precision@K + Recall@K)`

**Interpretação:**
- **Alto (próximo de 1.0)**: Boa combinação de Precision e Recall
- **Baixo (próximo de 0.0)**: Um dos dois (ou ambos) está baixo

**Valores calculados:**
- `test_f1@5`: F1-Score nas top 5 recomendações
- `test_f1@10`: F1-Score nas top 10 recomendações

**Quando usar:**
- Quando você quer balancear Precision e Recall
- Útil quando há trade-off entre encontrar mais itens (Recall) vs. garantir relevância (Precision)

---

### 4. AUC (Area Under the ROC Curve)

**O que mede:** Capacidade do modelo de distinguir entre itens relevantes e não relevantes.

**Fórmula:** Área sob a curva ROC (Receiver Operating Characteristic)

**Interpretação:**
- **1.0**: Perfeito - modelo sempre classifica corretamente
- **0.5**: Aleatório - não melhor que chute
- **< 0.5**: Pior que aleatório

**Valores calculados:**
- `train_auc`: AUC no conjunto de treino
- `test_auc`: AUC no conjunto de teste

**Quando usar:**
- Avaliar qualidade geral do modelo
- Comparar diferentes algoritmos
- Detectar overfitting (train_auc muito maior que test_auc)

---

### 5. MRR (Mean Reciprocal Rank)

**O que mede:** Posição média do primeiro item relevante na lista de recomendações.

**Fórmula:** `MRR = (1 / posição_do_primeiro_relevante) / número_de_usuários`

**Interpretação:**
- **1.0**: Primeiro item sempre é relevante
- **0.5**: Primeiro item relevante aparece em média na posição 2
- **0.0**: Nenhum item relevante encontrado

**Valores calculados:**
- `train_mrr`: MRR no conjunto de treino
- `test_mrr`: MRR no conjunto de teste

**Quando usar:**
- Quando a posição do primeiro item relevante é importante
- Útil para sistemas onde o usuário vê apenas as primeiras recomendações

**Exemplo:**
- Se o primeiro item relevante aparece na posição 3: MRR = 1/3 = 0.33

---

## 📈 Comparação de Métricas

### Qual Métrica Usar?

| Situação | Métrica Recomendada | Por quê? |
|----------|-------------------|----------|
| **Qualidade geral** | AUC | Mede capacidade de distinguir relevante/não relevante |
| **Top da lista** | Precision@5, MRR | Foco nas primeiras recomendações |
| **Cobertura** | Recall@10 | Quantos itens relevantes foram encontrados |
| **Balanceamento** | F1@10 | Combina Precision e Recall |
| **Diferentes tamanhos** | Precision@5, @10, @20 | Ver como performance varia com tamanho da lista |

---

## 🎯 Interpretação Prática

### Cenário 1: Alta Precision, Baixo Recall

```
Precision@10: 0.9
Recall@10: 0.2
```

**Significado:**
- ✅ Recomendações são muito relevantes (90%)
- ❌ Mas encontra poucos itens relevantes (20%)
- **Ação:** Modelo é conservador, precisa ser mais exploratório

### Cenário 2: Baixa Precision, Alta Recall

```
Precision@10: 0.3
Recall@10: 0.8
```

**Significado:**
- ❌ Muitas recomendações não são relevantes (30%)
- ✅ Mas encontra a maioria dos itens relevantes (80%)
- **Ação:** Modelo é muito exploratório, precisa ser mais preciso

### Cenário 3: Balanceado (Ideal)

```
Precision@10: 0.7
Recall@10: 0.6
F1@10: 0.65
```

**Significado:**
- ✅ Boa precisão (70% relevantes)
- ✅ Boa cobertura (60% dos relevantes encontrados)
- ✅ Balanceado (F1 = 0.65)

---

## 🔍 Análise no MLflow

### Como Comparar Modelos

1. **Acesse MLflow UI:** `mlflow ui`
2. **Compare runs:** Selecione múltiplos experimentos
3. **Analise métricas:**
   - **Precision@10**: Qual modelo tem mais recomendações relevantes?
   - **Recall@10**: Qual modelo encontra mais itens relevantes?
   - **F1@10**: Qual modelo tem melhor balanceamento?
   - **AUC**: Qual modelo tem melhor capacidade geral?

### Seleção do Melhor Modelo

O sistema usa **test_precision@10** como métrica principal para selecionar o melhor modelo, mas você pode:

1. **Ver todas as métricas** no MLflow
2. **Comparar manualmente** diferentes aspectos
3. **Escolher modelo** baseado na métrica mais importante para seu caso

---

## 📊 Exemplo de Saída

Após treinar, você verá no console:

```
📊 MLflow: Métricas registradas:
   Precision@10: 0.4523, Recall@10: 0.3821
   AUC: 0.7821, MRR: 0.6234
   F1@10: 0.4134
```

E no MLflow UI, todas as métricas estarão disponíveis para comparação!

---

## 🎓 Referências

- **Precision & Recall**: Métricas clássicas de recuperação de informação
- **AUC**: Padrão em classificação binária
- **MRR**: Comum em sistemas de busca e recomendação
- **F1-Score**: Balanceamento entre Precision e Recall

---

## 💡 Dicas

1. **Não foque apenas em uma métrica**: Use múltiplas para ter visão completa
2. **Considere o contexto**: Precision pode ser mais importante em alguns casos, Recall em outros
3. **Compare com baseline**: Um modelo aleatório tem Precision@10 ≈ 0.1 (se 10% dos itens são relevantes)
4. **Monitore overfitting**: Se train_auc >> test_auc, o modelo está decorando os dados
5. **Use F1 quando houver trade-off**: Se Precision e Recall estão em conflito, F1 ajuda a balancear

---

**Última atualização:** Sistema agora calcula 10+ métricas automaticamente durante o treinamento! 🎉


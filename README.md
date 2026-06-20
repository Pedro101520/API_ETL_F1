# API de ETL para o dashboard Analytics F1

**Dashboard:** https://formula1-analytics-project.streamlit.app

**Repositório do modelo de previsão:** https://github.com/Pedro101520/f1_prediction_models

**Repositório do dashboard:** https://github.com/Pedro101520/F1_Analytics

Estes códigos representam o ETL desenvolvido especialmente para fornecer informações atualizadas para o dashboard **F1 Analytics**.

Para evitar qualquer erro eventual que possa ocorrer nas fontes de dados originais, as informações processadas são armazenadas no **Storage do GCP**, e a partir disso o dashboard consome os dados.

Destaco que todas as informações são atualizadas automaticamente após o término de cada corrida/sprint/qualifying, uma vez que os pipelines de ETL foram transformados em API e tiveram sua execução agendada no **Cloud Scheduler** do GCP.

## Tecnologias Utilizadas
- Python
- Flask
- Pandas
- Google Cloud (Storage, Cloud Run, Cloud Scheduler)
- Docker

## Visão geral da estrutura
```
Acesso das informações via Jolpica F1 e FastF1 da última corrida
        ↓
API de ETL (Cloud Run + Cloud Scheduler)
        ↓
Salvar arquivos no Storage do GCP para acesso posterior no Dashboard
        ↓
Dashboard Streamlit
```

## Como funciona

Desenvolvi a API de uma forma simples, para deixar o mais compreensível possível: uma única rota executa todas as funções do pipeline, uma por vez. São elas:

| Função | Descrição |
|---|---|
| **Calendário** | ETL das informações das corridas atuais e das que ainda irão ocorrer |
| **Campeonato** | Visão geral de desempenho de todos os pilotos e equipes da temporada |
| **Equipes** | Visão de desempenho por corrida de cada equipe individualmente |
| **Pilotos** | Visão de desempenho por corrida de cada piloto individualmente |

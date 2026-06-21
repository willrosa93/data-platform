# data-platform

Pipeline de dados batch construído como parte do roadmap de 55 dias para transição para Engenharia de Dados. 
**Dia 1: Config dbt + BigQuery + primeiro model staging**

## Stack
| Camada | Tecnologia |
|--------|-----------|
| Data Warehouse | BigQuery |
| Transformação | dbt Core 1.11.11 |
| Auth | OAuth via gcloud |

## Fluxo atual
`project-e57dc814-3be0-44da-96e.ecommerce.orders` → dbt `stg_orders` → `dbt_dev.stg_orders`

## Como rodar localmente
```bash
# Pré-requisitos: gcloud autenticado, dbt instalado
cd ~/person_projects/data-platform/dbt/orders_pipeline
dbt build --select stg_orders

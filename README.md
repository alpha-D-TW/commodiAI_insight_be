# CHART CHAT BACKEND

### Embedding model
[bge-base-zh-v1.5](https://huggingface.co/BAAI/bge-base-zh-v1.5)

### How to run locally

#### 1. Run server
`uvicorn gen_ai.main:app --reload`

#### 2. Run DB migration
`alembic upgrade head`

### How to run with Docker

#### 1. Pull frontend repo to current directory
```
git clone git@github.com:alpha-D-TW/commodiAI_insight_fe.git
```

#### 2. Run with docker compose
```
docker compose up -d
```

#### 3. The containers should be as follows

| CONTAINER ID | IMAGE                                              | COMMAND                | CREATED            | STATUS                      | PORTS                                                                  | NAMES                 |
|:-------------|:---------------------------------------------------|:-----------------------|:-------------------|:----------------------------|:-----------------------------------------------------------------------|:----------------------|
| 7a476d1aa8ed | commodiai_insight_be-frontend                      | "docker-entrypoint.s…" | 7 minutes ago      | Up About a minute           | 0.0.0.0:3000->3000/tcp                                                 | frontend              |
| 5e2e743899b7 | commodiai_insight_be-backend                       | "uvicorn gen_ai.main…" | About a minute ago | Up About a minute           | 0.0.0.0:8000->8000/tcp                                                 | backend               |
| e4b526108c3b | localstack/localstack                              | "docker-entrypoint.sh" | About a minute ago | Up About a minute (healthy) | 127.0.0.1:4510-4559->4510-4559/tcp, 127.0.0.1:4566->4566/tcp, 5678/tcp | localstack-main       |
| 055fe8f530a8 | postgres:latest                                    | "docker-entrypoint.s…" | About a minute ago | Up About a minute           | 0.0.0.0:5432->5432/tcp                                                 | postgres              | 
| 22d221deb02f | opensearchproject/opensearch:latest                | "./opensearch-docker…" | About a minute ago | Up About a minute           | 0.0.0.0:9200->9200/tcp, 9300/tcp, 0.0.0.0:9600->9600/tcp, 9650/tcp     | opensearch-node       |
| ad0fe79cc996 | opensearchproject/opensearch-dashboards:latest     | "./opensearch-dashbo…" | About a minute ago | Up About a minute           | 0.0.0.0:5601->5601/tcp                                                 | opensearch-dashboards |

#### 4. Run DB migration
```
docker-compose exec backend alembic upgrade head
```

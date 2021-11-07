

# Liquidity Pool Metrics ETL
Automated ETL Pipeline to capture, clean and ontologize metrics from liquidity pools into an indexed RDBMS.

## Requirements

Docker [Installation Steps](https://docs.docker.com/get-docker/)

## Sample Pipeline
The preconfigured source code extracts liquidity and volume (in USD) metrics for BadgerDAO tokens on [Uniswap V2's Subgraph](https://thegraph.com/hosted-service/subgraph/uniswap/uniswap-v2), transforms the data through a Spark cluster running on a HDFS, and loads into a postgres table indexed on Liquidity Pool Address and Entry ID, partitioned by hour. 

Run the following command to spin up the `docker-compose.yml` services on a docker daemon
    docker-compose up -d

To view the performance of your cluster navigate to:

Spark Web UI: http://localhost:8080/
HDFS Web UI: http://localhost:9870/explorer.html#/user/root/

Captured metrics are cleaned and loaded by append-only pyspark jobs running at 5 minute intervals.  

To access the SQL command line of the indexed RDBMS:

    docker exec -it postgres /bin/bash/
    psql -U postgres -d liquidity

Sample query:

`SELECT * from lqdty_info;`

## High-level Architecture
This ETL service leverages HDFS and Spark for distributed storage and compute, enabling the service to scale as more liquidity pools are added into the pipeline.

![Architecture Diagram](https://github.com/goonlagoon/chainlink-lp/blob/main/media/architecture.png?raw=true)

Append-only jobs keep compute and runtime consistent regardless of data volume. 

Th

## Additional LPs
To add another liquidity pool into the pipeline, add another ingest configuration file similar to `badgerdao_ingest.env` to the configs folder.

```env
subgraph=SUBGRAPH_PATH
poolId=POOL_ID_FIELD_NAME
tokenId=TOKEN_ID_TO_FILTER
liquidity=LIQUIDITY_FIELD_NAME
volumeUSD=VOLUME_FIELD_NAME
timeout=TIMEOUT_BETWEEN_REQUESTS
records_per_file=RECORDS_TO_BATCH_PER_FILE
```

and add the following service config to the `docker-compose.yml` file.

```yml
version: '3'
services:
  ingest:
    build: ./lp-ingest
    container_name: lp_ingest-X
    restart: always
    depends_on:
    - postgres
    ports: 
    - "5000:5000"
    environment:
        WAIT_HOSTS: postgres:5432
        SERVICE_PRECONDITION: "namenode:9000 namenode:9870 datanode:9864"
    env_file:
        - ./config/NEW_INGEST_CONFIG_FILE.env
    
```

## Additional Storage
To add more HDFS capacity, add the following service config to the `docker-compose.yml` file to spin up additional data nodes.
```yml
version: '3'
services:
  datanode:
    image: bde2020/hadoop-datanode:2.0.0-hadoop3.2.1-java8
    container_name: datanode-X
    restart: always
    ports:
      - "9864:9864"
      - "50010:50010"
      - "50020:50020"
    volumes:
      - hadoop_datanode:/hadoop/dfs/data
    environment:
      SERVICE_PRECONDITION: "namenode:9870"
    env_file:
      - ./config/hadoop.env
```

## Additional Compute
To add more compute capacity, add the following service config to the `docker-compose.yml` file to spin up additional compute nodes.
```yml
version: '3'
services:
  spark-worker-1:
    image: bde2020/spark-worker:3.0.0-hadoop3.2
    container_name: spark-worker-X
    depends_on:
    - spark-master
    ports:
    - "8082:8081"
    environment:
    - "SPARK_MASTER=spark://spark-master:7077"
    - CORE_CONF_fs_defaultFS=hdfs://namenode:9000
    env_file:
    - ./config/hadoop.env
```

## Health Checks

Ingest job outputs 0 for liquidity and volume metric requests that fail. Preview failing epochs at http://localhost:9870/explorer.html#/user/root/health_check  
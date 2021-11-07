

# Liquidity Pool Metrics ETL
Automated ETL Pipeline to capture, clean and ontologize metrics from liquidity pools into an indexed RDBMS.

## Requirements

Docker [Installation Steps](https://docs.docker.com/get-docker/)

## Sample Pipeline
The preconfigured source code extracts liquidity and volume (in USD) metrics for BadgerDAO tokens on [Uniswap V2's Subgraph](https://thegraph.com/hosted-service/subgraph/uniswap/uniswap-v2), transforms the data through a Spark cluster running on a HDFS, and loads into a postgres table indexed on Liquidity Pool Address and Entry ID, partitioned by hour. 

Run the following command to spin up the `docker-compose.yml` services on a docker daemon
`docker-compose up -d`

To view the performance of your cluster navigate to:

Spark Web UI: http://localhost:8080/
HDFS Web UI: http://localhost:9870/explorer.html#/user/root/

Captured metrics are cleaned and loaded by append-only jobs running at 5 minute intervals.  

To access the SQL command line of the indexed RDBMS:

`docker exec -it postgres /bin/bash/`
`psql -U postgres -d liquidity`

Sample query:

`SELECT * from lqdty_info;`

## High-level Architecture

![Architecture Diagram](https://github.com/goonlagoon/chainlink-lp/tree/main/media/architecture.png?raw=true)


## Additional LPs


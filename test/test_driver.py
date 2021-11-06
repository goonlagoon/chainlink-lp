df = spark.read.format("com.databricks.spark.avro").load("hdfs://namenode:9000/user/root/clean/*")


psql_url = "jdbc:postgresql://postgres:5432/liquidity"
table = "public.lqdty_info"
mode = "overwrite"
properties = {"user":"postgres", "password": "example"}

(
    df.write\
        .jdbc(psql_url, table, properties=properties)
)
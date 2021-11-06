from pyspark import SparkConf, SparkContext
from pyspark.sql import SparkSession
import pyspark.sql.functions as F
import argparse
import yaml
import os

def get_lower_bound_ts(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            job_config = yaml.load(f, Loader=yaml.FullLoader)
            latest_epoch = job_config["latest_epoch"]
            print("INFO: LATEST EPOCH", str(latest_epoch))
            return latest_epoch
    else:
        print("INFO: LATEST EPOCH", str(0))
        return 0


def get_unread_files(spark, hdfs_path, pool_id, latest_epoch):
    path = "/".join(["/user/root/clean", pool_id])
    fs = spark._jvm.org.apache.hadoop.fs.FileSystem.get(spark._jsc.hadoopConfiguration())
    list_status = fs.listStatus(spark._jvm.org.apache.hadoop.fs.Path(path))
    file_names = [file.getPath().getName() for file in list_status if file.getPath().getName().split("=")[-1] > str(latest_epoch)]
    file_names = [file for file in file_names if file != "_SUCCESS"]
    file_paths = ["/".join([hdfs_path, "clean", pool_id, file_name, "*"]) for file_name in file_names]
    print("INFO: READING FILES FROM PATHS", file_paths)
    latest_epoch = int(max([file.split("=")[-1] for file in file_names]))
    print("INFO: LATEST EPOCH", latest_epoch)
    return (file_paths, latest_epoch)

if __name__ == "__main__":
    parser = argparse.ArgumentParser("lp_load")
    parser.add_argument("--hdfs_path", help="Define hdfs path root", type=str)
    parser.add_argument("--pool_id", help="Define pool id", type=str)
    parser.add_argument("--pg_port", help="Postgres Port", type=str)
    parser.add_argument("--pg_db", help="Postgres DB", type=str)
    parser.add_argument("--pg_table", help="Postgres Table", type=str)
    parser.add_argument("--pg_user", help="Postgres User", type=str)
    parser.add_argument("--pg_pwd", help="Postgres Password", type=str)

    args = parser.parse_args()


    conf = (
        SparkConf()
        .set("spark.hadoop.fs.default.name", args.hdfs_path)
        .set("spark.hadoop.fs.defaultFS", args.hdfs_path)
    )
    sc = SparkContext(conf=conf)
    spark = SparkSession(sc)
    
    job_config_path = "/job_config.yml"
    latest_epoch = get_lower_bound_ts(job_config_path)
    files, latest_epoch = get_unread_files(spark, args.hdfs_path, args.pool_id, latest_epoch)

    df = spark.read.format("com.databricks.spark.avro").load(files)

    psql_url = "jdbc:postgresql://postgres:{0}/{1}".format(args.pg_port, args.pg_db) 
    table = args.pg_table
    properties = {"user": args.pg_user, "password": args.pg_pwd}
    print(psql_url, table, properties)
    try:
        (
            df.write\
                .mode("append")
                .option("numPartitions", 5)
                .jdbc(psql_url, table, properties=properties)
        )

        with open(job_config_path, "w") as f:
                yaml.dump({'latest_epoch': latest_epoch}, f)
    except:
        print("ERROR: JDBC WRITE FAILED")

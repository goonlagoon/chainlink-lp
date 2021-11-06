from pyspark import SparkConf, SparkContext
from pyspark.sql import SparkSession
import pyspark.sql.functions as F
import argparse
import os
import yaml

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
    path = "/".join(["/user/root/raw", pool_id])
    fs = spark._jvm.org.apache.hadoop.fs.FileSystem.get(spark._jsc.hadoopConfiguration())
    list_status = fs.listStatus(spark._jvm.org.apache.hadoop.fs.Path(path))
    file_names = [file.getPath().getName() for file in list_status if file.getPath().getName().split("_")[-1].split(".")[0] > str(latest_epoch)]
    file_paths = ["/".join([hdfs_path, "raw", pool_id, file_name]) for file_name in file_names]
    print("INFO: READING FILES FROM PATHS", file_paths)
    latest_epoch = int(max([file.split("_")[-1].split(".")[0] for file in file_names]))
    print("INFO: LATEST EPOCH", latest_epoch)
    return (file_paths, latest_epoch)

if __name__ == "__main__":
    parser = argparse.ArgumentParser("lp_clean")
    parser.add_argument("--hdfs_path", help="Define root hdfs path", type=str)
    parser.add_argument("--pool_id", help="Define pool id", type=str)
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

    df = (
        df
        .withColumn("insert_ts", F.to_timestamp("insert_ts"))
        .withColumn("insert_timestamp_hour", F.date_trunc("hour", F.col("insert_ts")))
        .withColumn("insert_ts_hour_epoch", F.col("insert_timestamp_hour").cast("long"))
        .withColumn("pk", F.concat_ws("-", F.col("poolid"), F.col("insert_ts")))
    )

    ### write results
    try:
        (
            df
                .write
                .partitionBy("insert_ts_hour_epoch")
                .save("/".join([args.hdfs_path, "clean", args.pool_id]), format="avro", mode='append')
        )

        with open(job_config_path, "w") as f:
            yaml.dump({'latest_epoch': latest_epoch}, f)
            
    except:
        print("ERROR: HDFS WRITE FAILED")

    ### write health check
    (
        df
            .filter((F.col("liquidity") == 0) | (F.col("volume_usd") == 0))
            .write
            .partitionBy("insert_timestamp_hour")
            .save("/".join([args.hdfs_path, "health_check"]), format="avro", mode='overwrite')
    )



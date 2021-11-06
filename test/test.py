
from hdfs.ext.avro import AvroWriter
from hdfs.util import HdfsError
from hdfs import Client
import json
import avro.schema

hdfs_path='http://namenode:9870'
client = Client(hdfs_path)

schema = {
    'name': 'avro.example.LiquidityPool',
    'type': 'record',
    'fields': [
        {'name': 'a', 'type': 'string'},
		{'name': 'b', 'type': 'string'},
    ]
}
schema_parsed = avro.schema.Parse(json.dumps(schema))
records = [{ "a" :"test", "b": "test"}]
filename = "test4.avro"

with AvroWriter(client, filename, schema=schema) as writer:
    print("HDFS: AVRO WRITER CONNECTION OPENED")
    for record in records:
        writer.write(record)

"""
  spark-clean:
    image: bde2020/spark-base:3.1.1-hadoop3.2
    container_name: spark-clean
    ports
"""
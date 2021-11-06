import requests
import time
import datetime
from config import appconfig
import os
from hdfs import Client
from hdfs.ext.avro import AvroWriter
from hdfs.util import HdfsError

# set app configs
dirname = os.path.dirname(__file__)
params = appconfig(filename=dirname + "/configs/liquidity_pool.ini")

# set request configs
URL = "/".join(["https://api.thegraph.com/subgraphs", params["subgraph"]])
HEADERS = {
  'Content-Type': 'application/json'
}
# set hdfs configs
hdfs_path='http://namenode:9870'
client = Client(hdfs_path)
file_path = "/user/root/raw"
try:
	client.list(file_path)
except HdfsError:
	client.makedirs(file_path)
	print(client.list(file_path))

schema = {
    'name': 'avro.example.LiquidityPool',
    'type': 'record',
    'fields': [
        {'name': 'poolid', 'type': 'string'},
        {'name': 'liquidity', 'type': 'double'},
		{'name': 'volume_usd', 'type': 'double'},
		{'name': 'insert_ts', 'type': ["null", {
            "type" : "string",
            "logicalType" : "timestamp-micros"
        }]}
		
    ]
}

records = []
try:
	while True:
		payload = "".join(
			[
				"{\"query\":\"{\\n  token (id: \\\"",
				params["tokenid"],
				"\\\"){\\n    ",
				"\\n".join([	
					params["poolid"],
					params["liquidity"],
					params["volumeusd"]
				]),
				"\\n  }\\n}\",\"variables\":{}}"
			]
		)
		response = requests.post(
			url=URL, 
			headers=HEADERS,
			data=payload,
			verify=False
		)
		ts = datetime.datetime.now(datetime.timezone.utc)
		ts_format = "%Y-%m-%dT%H:%M:%S.%f"
		if response:
			r = response.json()
			
			if "data" in r and "token" in r["data"]:
				token_data = r["data"]["token"]
				print("RESPONSE: ", token_data)
				records.append(
					{
						"poolid" : token_data[params["poolid"]],
						"liquidity" : float(token_data[params["liquidity"]]),
						"volume_usd" : float(token_data[params["volumeusd"]]),
						"insert_ts" : ts.strftime(ts_format)
					}
				)
			else:
				records.append(
					{
					"poolid" : token_data[params["poolid"]],
					"liquidity" : 0,
					"volume_usd" : 0,
					"insert_ts" : ts.strftime(ts_format)
					}
				)
		else:
			records.append(
				{
				"poolid" : token_data[params["poolid"]],
				"liquidity" : 0,
				"volume_usd" : 0,
				"insert_ts" : ts.strftime(ts_format)
				}
			)
		if (len(records) % int(params["records_per_file"]) == 0):
			ts_name = records[0]["insert_ts"].replace(':', '_').replace('.', '_')
			filename = 'raw/{0}/lqdty_raw_{1}.avro'.format(token_data[params["poolid"]], ts.strftime('%s'))
			try:
				with AvroWriter(client, filename, schema=schema) as writer:
					print("INFO: AVRO WRITER CONNECTION OPENED")
					for record in records:
						writer.write(record)
					print("INFO: FILE WRITTEN SUCCESSFULLY")
				records.clear()
			except Exception as e: 
				print("ERROR: HDFS WRITE FAILED")
				print(e)
				exit()
		time.sleep(int(params["timeout"]))
		
except KeyboardInterrupt:
	print("INGEST INTERRUPTED")
	#close_connection(conn)
import sys,json,time,hmac,urllib
from datetime import datetime, timedelta
from base64 import b64encode
from hashlib import sha1
from readconfig import config_read
from influxdb import InfluxDBClient

#modules for cloud service providers
from cloud_providers import kt



class influxdb_request(object):
    def __init__(self, account_name,influxdbconfig):
        influxdb_ip=influxdbconfig.get("ip")
        influxdb_port=influxdbconfig.get("port") #do I really need this?
        self.influxdb_name=account_name #will create database based on cloud account name
        
        self.connector=InfluxDBClient(influxdb_ip,influxdb_port,'root','root',self.influxdb_name)
        
    def convert_to_utc(self,timestamp):
        offset=time.timezone / 3600.0 #is it right way to do this?
        cvttime=datetime.strptime(str(timestamp).split('.')[0], '%Y-%m-%dT%H:%M:%S')
        utc=datetime.strftime((cvttime + timedelta(hours=offset)),'%Y-%m-%dT%H:%M:%S.000Z')
        return utc
    
    def build_data_model(self):
        #data example:
        #   hostname(uuid-of-host) CPUUtilization
        #   {u'timestamp': u'2017-03-17T00:00:00.000', u'average': 0.446, u'minimum': 0.43, u'maximum': 0.46, u'unit': u'Percent'}
         
        #should I move this to /conf/config.yml?
        model=[{
                "measurement":self.data.get("metric"),
                "tags":{
                    "host":self.data.get("host"),
                    "uuid":self.data.get("uuid"),
                    "region":"kr",
                    "provider":self.data.get("provider"),
                    "account":self.data.get("account")
                },
                "time":self.convert_to_utc(self.data.get("data").get("timestamp")),
                "fields":{
                    "average":self.data.get("data").get("average"),
                    "minimum":self.data.get("data").get("minimum"),
                    "maximum":self.data.get("data").get("maximum")
                }
            }]
        return model
    
    def insert(self,data):
        self.data=data
        try:
            self.connector.create_database(self.influxdb_name) #If there's already exist, It'll NOT override but run without error
            self.connector.write_points(self.build_data_model())
            #need some verification code here, but not now
            return {"result":True,"message":self.data}
        except Exception, e:
            return {"result":False,"message":str(e)}



class run(object):
    def __init__(self, configpath, starttime, endtime):
        self.config=json.loads(config_read(configpath))
        message=[] #for result message
        
        try:
            for account in self.config.get("accounts"):
                self.account=account
                account_name=self.account.keys()[0]
                
                #I don't like this.. too ugly
                influxdb_info=self.account.get(account_name).get("influxdb")
                service_provider=self.account.get(account_name).get("provider")
                
                if service_provider == "kt":
                    get_metrics_data=kt.cloudwatch_request(self.account,starttime,endtime)
                #need exception here
                
                metrics_data=get_metrics_data()

                influxdb_conn=influxdb_request(account_name,influxdb_info) 
                for i in metrics_data:
                    for j in i.get("data"):
                        data={"account":account_name,
                              "host":i.get("vm_host"),
                              "uuid":i.get("vm_uuid"),
                              "provider":service_provider,
                              "metric":i.get("metric"),
                              "data":j}
                        message.append(influxdb_conn.insert(data))
        except Exception, e:
            message.append({"account":account_name,"exception":str(e)})
        finally:
            print json.dumps(message, indent=4)

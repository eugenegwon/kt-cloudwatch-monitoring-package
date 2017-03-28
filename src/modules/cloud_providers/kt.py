import sys,json,time,hmac,urllib,re
from base64 import b64encode
from hashlib import sha1

#for KT cloudwatch

class cloudwatch_request(object):
    def __init__(self, account, starttime, endtime):
        self.account=account
        self.starttime=starttime
        self.endtime=endtime
        
        self.debug=False
        
        self.metrics_type=[
            {"name":'CPUUtilization',"unit":"Percent"},
            {"name":'MemoryTarget',"unit":'Bytes'},
            {"name":'MemoryInternalFree',"unit":'Bytes'},
            {"name":'DiskReadBytes',"unit":'Bytes'},
            {"name":'DiskWriteBytes',"unit":"Bytes"},
            {"name":'NetworkIn',"unit":"Bytes"},
            {"name":'NetworkOut',"unit":"Bytes"}
            ]
        
        vm_list=self.get_server_list()
        self.result=[]

        for metric in self.metrics_type:
            metricname=metric.get("name")
            metricunit=metric.get("unit")
            for vm in vm_list:
                vm_host=re.sub('[\(\)]', ' ', vm).split(" ")[0]
                vm_uuid=re.sub('[\(\)]', ' ', vm).split(" ")[1]
                self.result.append({"vm_host":vm_host,"vm_uuid":vm_uuid,"metric":metricname,"data":(self.get_metrics(vm,metricname,metricunit))})
        
    def __call__(self):
        return self.result
        
    def credential_build(self):      
        kt_id=self.account.keys()[0]
        kt_key=self.account.get(kt_id).get("key")
        kt_secret=self.account.get(kt_id).get("secret")
        
        #make credential
        responsetype="json"
        ucloud_cmd={}

        #parsing args to command
        for arg in self.args:
            command_key,command_value=arg.split('=',1)
            ucloud_cmd.update({str(command_key):str(command_value)})
        ucloud_cmd.update({'apikey':str(kt_key),'response':str(responsetype)})
 
        #order dict and create command_string for encryption
        command_string='&'.join('='.join([parameter, urllib.quote_plus(ucloud_cmd.get(parameter))]) for parameter in sorted(ucloud_cmd))
        hex_dig=b64encode(hmac.new(str(kt_secret),(command_string.lower()),digestmod=sha1).digest())
        signature=urllib.urlencode({'signature':hex_dig})
        
        return '&'.join((command_string,signature))
    
    def send(self):
        request_url=self.credential_build()
        ucloud_response_raw=urllib.urlopen(str(self.api_url)+str(request_url))
        ucloud_response=ucloud_response_raw.read()
        
        if self.debug == True:
            print ucloud_response
        
        response=json.dumps(json.loads(ucloud_response),sort_keys=True,indent=4)
        return response
    
    #def get_lb_list(self):
    #   self.api_url="https://api.ucloudbiz.olleh.com/loadbalancer/v1/client/api?"
    
    def get_server_list(self):
        self.api_url="https://api.ucloudbiz.olleh.com/server/v1/client/api?"
        self.args=['command=listVirtualMachines']
        
        vm_list_raw=json.loads(self.send())        
        vms=[]
        for vm in vm_list_raw.get("listvirtualmachinesresponse").get("virtualmachine"):
            vms.append(vm.get("name")+"("+vm.get("id")+")")
            
        return vms

    def get_metrics(self, vm,metricname,unit):
        self.api_url="https://api.ucloudbiz.olleh.com/watch/v1/client/api?"
        self.args=['command=getMetricStatistics',
                    'dimensions.member.1.name=name',
                    str('dimensions.member.1.value='+vm),
                    str('metricname='+metricname),
                    'period=5',
                    str('unit='+unit),
                    'statistics.member.1=Average',
                    'statistics.member.2=Maximum',
                    'statistics.member.3=Minimum',
                    'namespace=ucloud/server',
                    str('starttime='+self.starttime),
                    str('endtime='+self.endtime)]

        metrics_data=json.loads(self.send())
        result=metrics_data.get("getmetricstatisticsresponse").get("metricstatistics")

        return result


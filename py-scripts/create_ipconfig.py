import json
import configparser

config = configparser.ConfigParser()
config['DNS']={}
config['client']={}
config['client']['ips'] = ''
config['server']={}

config['DNS'] = {
            'inter': '10.128.0.2',
            'exter': '35.232.57.157'
        }

machines=json.load(open('machine_client.json'))
for item in machines: 
    config['client']['ips'] = config['client']['ips'] + item['hostname'] + ','

machines=json.load(open('machine_server.json'))
for key in ['hestia-asia-southeast1-c-server', 'hestia-northamerica-northeast1-c-server', 'hestia-australia-southeast1-c-server', 'hestia-southamerica-east1-b-server', 'hestia-europe-west2-b-server']: 
    config['server'][key] = machines[key]['external_ip1']

with open('ip.conf','w') as cfg:
    config['layer'] = {}
    config['layer']['hestia-asia-southeast1-c-server'] = 'hestia-australia-southeast1-c-server'
    config['layer']['hestia-northamerica-northeast1-c-server'] = 'hestia-southamerica-east1-b-server'
    config['layer']['hestia-australia-southeast1-c-server'] = 'hestia-europe-west2-b-server'
    config['layer']['hestia-southamerica-east1-b-server'] = 'hestia-europe-west2-b-server'
    config['client']['ips'] = config['client']['ips'][:-1]
    config.write(cfg)
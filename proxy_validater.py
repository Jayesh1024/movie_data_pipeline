import requests
import json
import httpx
import asyncio
with open('Free_Proxy_List.json','r') as f:
    proxies_list=json.load(f)

async def ip_checker(ip,port):
    url='http://httpbin.org/ip'
    proxy_dict={
        "http://":f"http://{ip}:{port}",
        "https://":f"http://{ip}:{port}"
    }
    async with httpx.AsyncClient(proxies=proxy_dict) as client:
        try:
            print(f"Checking ip: {ip} with port: {port}")
            response = await client.get(url,timeout=5)
            return {
                'status_code':response.status_code,
                'ip':ip,
                'port':port
            }
        except Exception as e:
            return {
                'status_code':-1,
                'ip':ip,
                'port':port,
                'error':e
            }

async def main():
    ip_checker_coro=[]
    healthy_ips=[]
    unhealthy_ips=[]
    for proxy in proxies_list:
        ip_checker_coro.append(ip_checker(ip=proxy['ip'],port=proxy['port']))

    results = await asyncio.gather(*ip_checker_coro)

    for result in results:
        if result['status_code']==200:
            ip_dict={
                'ip':result['ip'],
                'port':result['port']
            }
            healthy_ips.append(ip_dict)
        
        elif result['status_code']==-1:
            ip_dict={
                'ip':result['ip'],
                'port':result['port'],
                'error':str(result['error'])
            }
            unhealthy_ips.append(ip_dict)

    with open('healthy_ips.json','w') as f:
        json.dump(healthy_ips,f,indent=2)

    with open('unhealthy_ips.json','w') as f:
        json.dump(unhealthy_ips,f,indent=2)

asyncio.run(main())

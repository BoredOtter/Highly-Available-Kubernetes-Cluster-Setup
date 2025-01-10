import requests,time
service_url="http://192.168.0.30/"
headers={"Host":"grafana.bm.boredotter.dev"}
last_state_success=True
failure_start=None
while True:
    try:
        response=requests.get(service_url,headers=headers,timeout=0.5,allow_redirects=True)
        if 200<=response.status_code<300:
            if not last_state_success:print(f"Usługa odzyskała sprawność po {time.time()-failure_start:.2f} s.")
            else:print(f"Zapytanie udane (kod {response.status_code}).")
            last_state_success=True
        else:
            if last_state_success:failure_start=time.time()
            last_state_success=False
            print(f"Zapytanie nieudane. Kod: {response.status_code}")
    except requests.RequestException as e:
        if last_state_success:failure_start=time.time()
        last_state_success=False
        print(f"Zapytanie nieudane: {e}")

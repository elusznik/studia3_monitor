#!/usr/bin/python3
from datetime import date
from datetime import datetime
import requests
import time

from fake_useragent import UserAgent
from flask_apscheduler import APScheduler

def uptime(url, header):
    gettime = 0
    response = requests.get(url, headers=header, verify=True, timeout=5)
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"[!] Exception caught: {e}")
        return response.status_code, gettime
    if response.status_code == 200:
        gettime = round(response.elapsed.total_seconds(), 2)
    else:
        gettime = 0
    return response.status_code, gettime


ua = UserAgent()
header = {
    'User-Agent': ua.chrome
}

#url = "https://studia.elka.pw.edu.pl"
url = "https://httpstat.us/504"

status, time = uptime(url, header)
print(status, time)

scheduler = APScheduler()
scheduler.add_job(func=uptime, trigger="interval", seconds=60)
scheduler.start()

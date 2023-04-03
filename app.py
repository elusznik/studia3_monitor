import csv
import datetime
import time

import matplotlib.pyplot as plt
import requests
from flask import Flask, render_template, send_file

app = Flask(__name__)


class Status:
    def __init__(self, timestamp, status_code, response_time):
        self.timestamp = timestamp
        self.status_code = status_code
        self.response_time = response_time


def check_website():
    url = "https://studia.elka.pw.edu.pl"
    try:
        start_time = time.time()
        response = requests.get(url, timeout=15)
        end_time = time.time()
        response_time = end_time - start_time
        if response_time > 15:
            status_code = 0
        else:
            status_code = response.status_code
    except requests.exceptions.RequestException:
        status_code = 0
        response_time = 0
    return status_code, response_time


def record_status():
    with open("status.csv", "a") as f:
        writer = csv.writer(f)
        status_code, response_time = check_website()
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        writer.writerow([timestamp, status_code, response_time])


def get_last_24h_status():
    status_list = []
    now = datetime.datetime.now()
    with open("status.csv") as f:
        reader = csv.reader(f)
        for row in reader:
            timestamp = datetime.datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S")
            if now - timestamp <= datetime.timedelta(hours=24):
                status_code = int(row[1])
                response_time = float(row[2])
                status_list.append(Status(timestamp, status_code, response_time))
    return status_list


def get_uptime_percentage(status_list):
    if not status_list:
        return 0.0
    uptime = sum(1 for status in status_list if status.status_code == 200)
    return float(uptime) / len(status_list) * 100


def get_downtime_percentage(status_list):
    if not status_list:
        return 0.0
    downtime = sum(1 for status in status_list if status.status_code != 200 or status.response_time > 15)
    return float(downtime) / len(status_list) * 100


def generate_plot(status_list):
    x = [status.timestamp for status in status_list]
    y = [status.response_time * 1000 for status in status_list]
    plt.plot(x, y)
    plt.xlabel("Time")
    plt.ylabel("Response time (ms)")
    plt.savefig("static/status.png")


@app.route("/")
def index():
    record_status()
    status_list = get_last_24h_status()
    uptime_percentage = get_uptime_percentage(status_list)
    downtime_percentage = get_downtime_percentage(status_list)
    generate_plot(status_list)
    return render_template("index.html", uptime_percentage=uptime_percentage, downtime_percentage=downtime_percentage)


@app.route("/status")
def status():
    return send_file("static/status.png", mimetype="image/png")

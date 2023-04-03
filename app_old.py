import csv
import datetime

import requests
from fake_useragent import UserAgent
from flask import Flask, render_template
from flask_apscheduler import APScheduler

app = Flask(__name__)
app.config["SERVER_NAME"] = "127.0.0.1:5000"
scheduler = APScheduler()
scheduler.api_enabled = True
scheduler.init_app(app)
scheduler.start()


@scheduler.task("interval", id="uptime", seconds=60)
@app.route("/")
def uptime():
    with app.app_context():
        # url = "https://httpstat.us/500"
        url = "https://studia.elka.pw.edu.pl/"
        ua = UserAgent()
        header = {
            "User-Agent": ua.chrome
        }
        try:
            response = requests.get(url, headers=header, verify=True, timeout=60)
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            # print(f"[!] Exception caught: {e}")
            msg = f"HTTP error {response.status_code}"
            up = 0
        except requests.exceptions.ConnectTimeout as e:
            print(f"[!] Exception caught: {e}")
            # return render_template('index_old.html', msg="Connection timeout")
            msg = f"Connection timeout"
            up = 0
        except requests.exceptions.ConnectionError as e:
            print(f"[!] Exception caught: {e}")
            # return render_template("index_old.html", msg="Connection error")
            msg = "Connection error"
            up = 0
        """if response.status_code == 200:
            get_time = round(response.elapsed.total_seconds(), 2)
        else:
            get_time = 0"""
        get_time = response.elapsed.total_seconds()
        date = datetime.datetime.now()
        print(date)
        with open("log.csv", "a+", encoding="UTF8", newline="") as f:
            writer = csv.writer(f)
            if response.status_code == 200:
                up = 1
                msg = f"OK, {get_time}s"
            else:
                writer.writerow([date, up, get_time])
        with open("log.csv", "r", encoding="UTF8", newline="") as f:
            reader = csv.reader(f)
            rows = list(reader)
            # print(rows)
        print(msg)
        return render_template("index_old.html", msg=msg)


@app.route("/dupa")
def dupa():
    return "dupa"


if __name__ == "__main__":
    app.run()

from flask import Flask, Response, request
from flask_limiter import Limiter
from selenium import webdriver
from flask_limiter.util import get_remote_address
from random import seed, randint
from time import sleep
from os import environ

PORT = (int(environ.get('PORT')) if environ.get('PORT') else 8080)
IS_HTTPS = False
IS_LOCALHOST = False
URL = "localhost"
FLAG = environ.get('FLAG') or 'jctf{test_flag}'
if FLAG[0] == "j":
    print('Warning: flag is not set!!!')

current_seed = randint(0, 2**32)
app = Flask(__name__)
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["50000 per hour"],
    storage_uri="memory://",
)


def set_chrome_options():
    """Sets chrome options for Selenium.
    Chrome options for headless browser is enabled.
    """
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_prefs = {"profile.default_content_settings": {"images": 2}}
    chrome_options.experimental_options["prefs"] = chrome_prefs
    return chrome_options


@app.post("/report")
def report():
    offering = request.form.get('offering')
    if not isinstance(offering, str):
        return "Error"
    if len(offering) > 630:
        return "Payload bigger than 630 characters. You've been caught!"
    bribe = request.form.get('bribe')
    allowed = "](+![)"
    msg = "Payload successfully smuggled"

    if bribe is not None:
        try:
            bribe = int(bribe)
            number = randint(-1234567, 7654321)
            seed(number)
            if bribe == number:
                allowed += 'hs:pi/\'t=;'
                msg += " (with guard bribed!)"
            else:
                return f"Your bribe attempt fails. The accepted number was 
{number}"
        except:
            return "You tripped! Try again"

    if not all([_ in allowed for _ in offering]):
        return f"Caught with contraband once more!"
    driver = webdriver.Chrome(options=set_chrome_options())
    url = "http" + "s" * IS_HTTPS + "://" + URL + ":" + str(PORT)
    driver.get(url)
    sleep(0.3)
    try:
        driver.add_cookie({"name": "flag", "value": FLAG})
        driver.execute_script(offering + ";")
    except Exception as e:
        print(e)
    sleep(1)
    driver.stop_client()
    return msg


@app.route("/")
def mainpage():
    with open("index.html") as f:
        return f.read()


@app.route("/style.css")
def styles():
    with open("style.css") as f:
        return Response(f.read(), mimetype="text/css")


@app.route('/source')
@limiter.limit("5/second")
def source():
    return Response(open(__file__).read(), mimetype="text/plain")


def main():
    app.run('0.0.0.0', PORT)


if __name__ == '__main__':
    main()

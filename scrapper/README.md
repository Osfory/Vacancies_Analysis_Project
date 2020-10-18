###Getting started:

- Install venv for python project isolation: `python -m venv .`
- Activate venv for shell: `source bin/activate`
- Install manual declared dependencies: `pip install -r dependencies.txt`
- Download chrome driver: `https://sites.google.com/a/chromium.org/chromedriver/`
- You may open chrome with remote address: `chromium --remote-debugging-port=9222 --user-data-dir=/tmp/chrometmp` and connect to it using `connect $PORT` command: `python headhunterScrapper.py /home/aleksey/PycharmProjects/Web_driver/chromedriver_linux64/chromedriver /home/aleksey/PycharmProjects/Vacancies_Analysis_Project/rawdata 1 2 connect 9222` (example)
- Either use `open` command and just open new browser: `python headhunterScrapper.py /home/aleksey/PycharmProjects/Web_driver/chromedriver_linux64/chromedriver /home/aleksey/PycharmProjects/Vacancies_Analysis_Project/rawdata all 1 open` (example)




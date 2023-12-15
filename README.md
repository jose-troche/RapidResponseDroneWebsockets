


# Development environment

* Create a new python venv and activate it
* Install the requirements.txt

```
python3 -m venv .rrdws.venv
. .rrdws.venv/bin/activate
pip install -r requirements.txt
```

* For local dev
```
pip install 'watchdog[watchmedo]'

cd ground_station
watchmedo auto-restart --pattern "*.py" --recursive --signal SIGTERM \
  python websocket_server.py
```



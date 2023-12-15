


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
cd ground_station
./main.py

# or

./main.py 0 1

# Where the numbers are indices for the array of components, so 0 and 2 will run the first and the third component
[
    drone_telemetry_listener,
    websocket_server
]
```






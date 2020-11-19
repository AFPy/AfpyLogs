# AfpyLogs

Web view of IRC logs from #python-fr channel on Freenode.


## Installing

    pip install -e .


## Testing

    pip install -e .[test]
    pytest


## Running

    gunicorn --workers 2 --bind unix:afpylogs.sock -m 007 server


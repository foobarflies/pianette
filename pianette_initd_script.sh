#!/bin/sh
case "$1" in
    start)
        sudo -i PYTHONIOENCODING="utf-8" /home/pi/pianette/main.py
    ;;

    stop)
        sudo killall python3
    ;;

    *)
        echo 'Usage: /etc/init.d/pianette {start|stop}'
        exit 1
    ;;
esac

exit 0
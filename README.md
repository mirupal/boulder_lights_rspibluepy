# ED-Board Server

This is a small python script which starts an bluetooth server based on the simple demo of `pybluez`. Check out their repo.

On receiving data the sever triggers a function to enable certain LEDs in the LED-Matrix. 

The receiving data must contain an json string which consist of xy coordinates.

Schema:
```json
[
    { "x": 1, "y": 1},
    { "x": 2, "y": 4},
    .. and so on
]
```

## Servcie wrapper
Use the config for the service
```ini
[Unit]
Description=Ed Board
After=multi-user.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 /home/pi/ed-board-server/edboard.py --cascaded 4 --block-orientation -90
Restart=on-abort

[Install]
WantedBy=multi-user.target
```
Folow the guide in this gist:
https://gist.github.com/emxsys/a507f3cad928e66f6410e7ac28e2990f

sudo systemctl daemon-reload

## manual steps for connections after rpi restsart

After these command the app can directly connect for chat.

```sh
$ sudo sdptool add SP         # There can be channel specified one of 79 channels by adding `--channel N`.
$ sudo sdptool browse local   # Check on which channel RFCOMM will be operating, to select in next step.

$ sudo killall rfcomm
$ sudo rfcomm listen /dev/rfcomm0 N picocom -c /dev/rfcomm0 --omap crcrlf   # `N` should be channel number on which SDP is pointing the SP
```

## trigger led matrix with json params (ble server integrated)

for ble connection to work run this comman before mydemo.py

`$ sudo hciconfig hciX piscan`

in ~/dev/max7219 trigger command

`sudo python3 examples/mydemo.py --cascaded 4 --block-orientation -90`

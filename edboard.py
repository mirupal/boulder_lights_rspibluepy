#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2017-18 Richard Hull and contributors
# See LICENSE.rst for details.

import os
import re
import time
import argparse
import bluetooth
import json


from luma.led_matrix.device import max7219
from luma.core.interface.serial import spi, noop
from luma.core.render import canvas
from luma.core.virtual import viewport
from luma.core.legacy import text, show_message
from luma.core.legacy.font import proportional, CP437_FONT, TINY_FONT, SINCLAIR_FONT, LCD_FONT


def drawRoute(n, block_orientation, rotate, inreverse, routeJson):
    # this method parses the routeJson and enables leds in
    # led matrix for 2d coordinates in json data

    # create matrix device
    serial = spi(port=0, device=0, gpio=noop())
    #device = max7219(serial, cascaded=n or 1, block_orientation=block_orientation,
    #                 rotate=rotate or 0, blocks_arranged_in_reverse_order=inreverse)
    device = max7219(serial, width=32, height=8, block_orientation=block_orientation,
                     rotate=rotate or 0, blocks_arranged_in_reverse_order=inreverse)
    print("Created device")
    print(routeJson)

    route = json.loads(routeJson)

    # enable leds by using draw.point method
    with canvas(device) as draw:
       for hold in route:
           print("hold pos: " + str(hold["x"]) + " " + str(hold["y"]))
           draw.point((hold["x"],hold["y"]), fill="white")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='matrix_demo arguments',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('--cascaded', '-n', type=int, default=1, help='Number of cascaded MAX7219 LED matrices')
    parser.add_argument('--block-orientation', type=int, default=0, choices=[0, 90, -90], help='Corrects block orientation when wired vertically')
    parser.add_argument('--rotate', type=int, default=0, choices=[0, 1, 2, 3], help='Rotate display 0=0°, 1=90°, 2=180°, 3=270°')
    parser.add_argument('--reverse-order', type=bool, default=False, help='Set to true if blocks are in reverse order')

    args = parser.parse_args()

    os.system("sudo hciconfig hciX piscan")

    # bluetooth server setup
    server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    server_sock.bind(("", bluetooth.PORT_ANY))
    server_sock.listen(1)

    port = server_sock.getsockname()[1]

    # TODO check if this needs to be changed
    uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"
    bluetooth.advertise_service(server_sock, "SampleServer", service_id=uuid,
                            service_classes=[uuid, bluetooth.SERIAL_PORT_CLASS],
                            profiles=[bluetooth.SERIAL_PORT_PROFILE],
                            # protocols=[bluetooth.OBEX_UUID]
                            )

    try:
        while True:
            print("Waiting for connection on RFCOMM channel", port)

            client_sock, client_info = server_sock.accept()
            print("Accepted connection from", client_info)

            # use received data to enable leds
            try:
                while True:
                    data = client_sock.recv(1024)
                    if not data:
                        break
                    
                    # data needs to be decoded to utf-8 string as it comes in binary form
                    drawRoute(
                        args.cascaded, 
                        args.block_orientation, 
                        args.rotate, 
                        args.reverse_order, 
                        data.decode("utf-8")
                        ) 
            except (OSError, KeyboardInterrupt):
                pass
            
    except KeyboardInterrupt:
        pass

    print("Disconnected.")

    client_sock.close()
    server_sock.close()
    print("All done.")

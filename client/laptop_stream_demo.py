"""
Laptop Stream Demo

View the JPEG or H264 stream from R1 on your laptop direclty over WiFi

"""
# prep for python 3.0
from __future__ import absolute_import
from __future__ import print_function
import argparse
import os
import subprocess
import threading
import time


from skydio.comms.http_client import HTTPClient
from skydio.comms.udp_link import UDPLink


def main():
    parser = argparse.ArgumentParser(
        description="Control R1 from a computer with a connected gamepad.")
    parser.add_argument('--baseurl', metavar='URL', default='http://192.168.10.1',
                        help='the url of the vehicle')

    # NOTE: you'll need a token file in order to connect to a simulator.
    # Tokens are NOT required for real R1s.
    parser.add_argument('--token-file',
                        help='path to the auth token for your simulator')

    parser.add_argument('--stream', choices=['h264', 'jpeg'], default='jpeg',
                        help='The video stream type that the vehicle should produce')

    args = parser.parse_args()

    if 'sim' in args.baseurl:
        # Due to Network Address Translation, RTP tends not to work on the open internet.
        # The sim will send packets, but your firewall will reject them.
        # You may be able to add port-forwarding to your firewall to fix this.
        raise RuntimeError('RTP streaming is not supported in the simulator yet.')

    if args.stream == 'h264':
        # H264 is the 720P 15fps h264 encoded stream directly from the camera.
        stream_settings = {'source': 'H264', 'port': 55004}
        # TODO: this stream seems like have client-induced lag
        # Perhaps due to incorrect timestamps.
    elif args.stream == 'jpeg':
        # NATIVE is the raw images, though we convert to 240p jpeg by default before sending.
        stream_settings = {'source': 'NATIVE', 'port': 55004}
    else:
        raise ValueError('Unknown stream format {}'.format(args.stream))

    # Create the client to use for all requests.
    client = HTTPClient(args.baseurl,
                        pilot=True,
                        token_file=args.token_file,
                        stream_settings=stream_settings)

    if not client.check_min_api_version():
        print('Your vehicle is running an older api version.'
              ' Update recommended in order to enable streaming.')

    # Periodically poll the status endpoint to keep ourselves the active pilot.
    def update_loop():
        while True:
            client.update_pilot_status()
            time.sleep(2)
    status_thread = threading.Thread(target=update_loop)
    status_thread.setDaemon(True)
    status_thread.start()

    # Create a low-latency udp link for quickly sending messages to the vehicle.
    remote_address = client.get_udp_link_address()
    link = UDPLink(client.client_id, local_port=50112, remote_address=remote_address)

    # Connect the UDPLink to the vehicle before trying to takeoff.
    link.connect()

    # proxy RTP packets to a remote host
    subprocess.Popen(['python', 'gstreamer_viewer.py',
                      '--format', args.stream])

    while True:
        link.send_json('', {})
        time.sleep(0.1)


if __name__ == '__main__':
    main()

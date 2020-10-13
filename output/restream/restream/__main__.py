import sys
import requests
from restream.network_client import NetworkClient
from restream.util.log import Log

class Restreamer:

    def __init__(self):
        print('Init Restreamer')
        
    def restream(self, url: str, client: NetworkClient, additional_headers: dict = None):
        session = requests.Session()
        if additional_headers:
            session.headers.update(additional_headers)
        r = session.get(url, stream=True)

        print(r.headers)

        for line in r.raw:
            if line:
                if not client.send(line):
                    Log.error('Could not send.')
                    return

# Main

def main():
    if len(sys.argv) < 3:
        print('python3 -m concat SOURCE TARGET\n e.g. python3 -m https://www.superstream.com:5000 127.0.0.1:1234')
        sys.exit()

    args = sys.argv
    source = args[1]
    target = args[2]

    target_components = target.split(':')
    if len(target_components) < 2:
        Log.warning('No target port? Set to 80!')
        target_components.append('80')

    network_client = NetworkClient()
    if not network_client.connect(target_components[0], int(target_components[1])):
        return
    
    restreamer = Restreamer()

    additional_headers = {'Icy-MetaData': '0'}
    restreamer.restream(source, network_client, additional_headers)

if __name__ == '__main__':
    main()
from file_dealer.lib.utils.log import Log
from file_dealer.cook import Cook
from file_dealer.pusher import Pusher
from file_dealer.provider import Provider
from time import sleep
import sys

class Dealer:

    def __init__(self, folder: str, file_type: str = ''):
        Log.happy("I've got what you need...")
        self.cook = Cook(folder, file_type)
    
    def push(self, address: str, port: int, packet_delay: float = 0.0):
        pusher = Pusher()
        pusher.connect(address, port)
        
        # Push files in endless loop
        while True:
            for file in self.cook.files:
                try:
                    pusher.send_file(file)
                except Exception as exception:
                    Log.error('Pushing error:', exception)
                    break
                sleep(packet_delay)

    def provide(self, target: str, port: int, packet_delay: float = 0.0):
        provider = Provider(target, port)

        # Provide files in endless loop
        while True:
            try:
                provider.provide_files(self.cook.files, packet_delay)
            except Exception as exception:
                Log.error('Providing error:', exception)
                break

# Main

def main():
    if len(sys.argv) < 4:
        print('python3 -m file_dealer FOLDER EXTENSION TARGET:PORT Optional[INTER-PACKET-DELAY]\n e.g. python3 -m file_dealer ./files mp3 127.0.0.1:1234 2.1')
        sys.exit()

    args = sys.argv
    folder = args[1]
    extension = args[2]

    target = args[3]
    target_components = target.split(':')
    if len(target_components) < 2:
        Log.warning('No target port? Set to 80!')
        target_components.append('80')

    delay = None
    if len(sys.argv) >= 4:
        delay = args[4]

    dealer = Dealer(folder, extension)
    dealer.provide(target_components[0], target_components[1], delay)
    

if __name__ == '__main__':
    main()

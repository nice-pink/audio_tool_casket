# Run

`python3 -m file_dealer FOLDER EXTENSION TARGET:PORT Optional[INTER-PACKET-DELAY]`

Example:

Send all files from folder `./files` with extension `mp3` to `127.0.0.1:1234` with a inter packet delay of 2.1 seconds.

```
cd output/file_dealer/
python3 -m file_dealer ./files mp3 127.0.0.1:1234 2.1
`
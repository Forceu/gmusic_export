# gmusic_export

## Export Google Music Takeout Data to Subsonic Based Servers


This script allows you export your playlists and liked songs to your subsonic based servers (eg. Airsonic or Funkwhale). The songs already need to be present at the server.

#### Usage

To use it, first you must modify the server url and credential variables at the top of the script. Then you call the script with python3:

`python3 gmusic_export.py -s /home/user/googletakeout/` This will star all songs that have an CSV file in the folder googletakeout


`python3 gmusic_export.py -p "Nice songs" /home/user/googletakeout/` This will add all songs that have an CSV file in the folder googletakeout to the new playlist "Nice Songs"

If any items fail (eg. cannot be looked up at the server), a copy of the CSV file will be placed in a subfolder named "failed" located in the folder where the script was called.

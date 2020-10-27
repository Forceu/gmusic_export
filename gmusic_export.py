import libsonic, os, csv, html, argparse, sys
from shutil import copyfile

#####CHANGE ME######
URL      = 'https://your.server.url'
PORT     =  443
USERNAME = 'youruser' # case sensitive!
PASSWORD = 'yourpassword' # might be different to your regular password
####################


example_text = '''Example:

 python3 gmusic_export.py -s /home/user/googletakeout/
 python3 gmusic_export.py -p "Nice songs" /home/user/googletakeout/'''


parser = argparse.ArgumentParser(prog='gmusic_export', description='Export your starred songs and playlists to Subsonic based services. Failed items will be copied to subfolder "failed".',epilog=example_text,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument('PATH', help='Path to folder with CSV files from Google Takeout')
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument("-s", "--star", help="Star all songs in folder", action="store_true")
group.add_argument("-p", "--playlist", help="Add all songs in folder to a new playlist.", action='store', dest='name')

args = parser.parse_args()

CSVPATH=os.path.join(args.PATH, '')
IS_STAR=args.star
PLAYLIST_NAME=args.name


conn = libsonic.Connection(URL, USERNAME, PASSWORD, port=PORT)

processedSongs = 0
failedSongs = []
playlistSongs = []



def get_song_id(connection, title, artist, album):
  songs = conn.search3(query=title)
  if "searchResult3" in songs:
    if len(songs['searchResult3']['song'])>0:
      for song in songs['searchResult3']['song']:
        if (song['title'].casefold()==title.casefold() and ((artist.casefold() in song['artist'].casefold() or (song['artist']=='Various Artists' and len(songs['searchResult3']['song'])==1))) and (song['album'].casefold()==album.casefold() or len(songs['searchResult3']['song'])==1)):
          return song['id']
  return -1


def star_song(connection, title, artist, album):
  songid = get_song_id(connection, title, artist, album)
  if (songid!=-1):
    starresult = conn.star(sids=[song['id']])
    if ("status" in starresult and starresult["status"]=="ok"):
      return True
  return False


def add_song_to_playlistarray(connection, title, artist, album):
  global playlistSongs
  songid = get_song_id(connection, title, artist, album)
  if (songid!=-1):
    playlistSongs.append(songid)
    return True
  return False


def create_playlist(connection, playlistname, playlistSongs):
  playlists=connection.createPlaylist(name=playlistname,songIds=playlistSongs)
  if ("status" in playlists and playlists["status"]=="ok"):
    return True
  return False
  

class bcolors:
    OK = '\033[92m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

def submit_song(csvrow, filename):
  global IS_STAR
  title=html.unescape(csvrow[0])
  album=html.unescape(csvrow[1])
  artist=html.unescape(csvrow[2])
  if IS_STAR:
    presult = star_song(conn, title, artist, album)
  else:
    presult = add_song_to_playlistarray(conn, title, artist, album)
  if presult:
    print(f"{bcolors.OK}OK   "+title+" - "+artist+" ("+album+")"+bcolors.ENDC)
    global processedSongs
    processedSongs = processedSongs +1
  else:
    print(f"{bcolors.FAIL}FAIL "+title+" - "+artist+" ("+album+")"+bcolors.ENDC)
    failedSongs.append(title+" - "+artist+" ("+album+")")
    if not os.path.exists("./failed"):
      os.makedirs("./failed")
    if not os.path.isfile("./failed/"+filename):
      copyfile(CSVPATH+filename, "./failed/"+filename)

for file in os.listdir(CSVPATH):
  if file.endswith(".csv"):
    with open(CSVPATH+(file), 'r') as csvfile:
       songreader = csv.reader(csvfile, delimiter=',', quotechar='"')
       next(songreader)
       for row in songreader:
         submit_song(row, file)


if (IS_STAR == False):
  print()
  print()
  if create_playlist(conn, PLAYLIST_NAME, playlistSongs):
    print(f"{bcolors.OK}Playlist "+PLAYLIST_NAME+" has been created."+bcolors.ENDC)
  else:
    print(f"{bcolors.FAIL}Unable to create Playlist "+PLAYLIST_NAME+"!"+bcolors.ENDC)

print()
print("Done. Success: "+str(processedSongs))
print("List of "+str(len(failedSongs))+" failed items: ")
for song in failedSongs:
  print(song)



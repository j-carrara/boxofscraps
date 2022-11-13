scp -r -i "***REMOVED***" ../Documents/boxofscraps/src ***REMOVED***:~/boxofscraps
ssh -i "***REMOVED***" ***REMOVED***
pkill screen
cd boxofscraps/src
screen -s bot -dm python3.8 bot.py
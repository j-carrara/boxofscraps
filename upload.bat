scp -r -i "***REMOVED***" src ***REMOVED***:~/boxofscraps
ssh -i "***REMOVED***" ***REMOVED*** pkill screen
ssh -i "***REMOVED***" ***REMOVED*** screen -s bot -dm python3.8 ~/boxofscraps/src/bot.py
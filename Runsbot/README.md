[![Language](https://img.shields.io/badge/language-Python-green.svg?style=for-the-badge)](http://www.python.org)

# MLB Limnoria/Supybot Announcer

```
(runsbotchannel <add|list|del> <#channel> <ALL|TEAM>) -- Add or delete team(s) from a specific channel's output. Use team abbreviation for specific teams or ALL for everything. Can only specify one at a time. Ex: add #channel1 ALL OR add #channel2 TOR OR del #channel1 ALL OR list 
```
## Config Options
* supybot.plugins.Runsbot.allPlays
* * Will announce allPlays (only recommended when in team specific channel)
* supybot.plugins.Runsbot.checkInterval
* supybot.plugins.Runsbot.dateFlip
* supybot.plugins.Runsbot.isDebug
* supybot.plugins.Runsbot.isFirst
* supybot.plugins.Runsbot.isLoaded
* supybot.plugins.Runsbot.isWarmups
* supybot.plugins.Runsbot.public

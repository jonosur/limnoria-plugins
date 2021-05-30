[![Language](https://img.shields.io/badge/language-Python-green.svg?style=for-the-badge)](http://www.python.org)

# MLB Limnoria/Supybot Announcer

```
(runsbotchannel <add|list|del> <#channel> <ALL|TEAM>) -- Add or delete team(s) from a specific channel's output. Use team abbreviation for specific teams or ALL for everything. Can only specify one at a time. Ex: add #channel1 ALL OR add #channel2 TOR OR del #channel1 ALL OR list 
```
## Config Options
* supybot.plugins.Runsbot.allPlays
  * Will announce allPlays (only recommended when in team specific channel)
* supybot.plugins.Runsbot.checkInterval
 * Time in seconds that the bot will trigger the internal scheduler
* supybot.plugsin.Runsbot.announceInterval
 * Time in seconds used to know how much of a delay you want on announcing the information after it has happened
* supybot.plugins.Runsbot.isDebug
 * If True the plugin will post additional information to default INFO level log setting
* supybot.plugins.Runsbot.isJSON
 * If you would like to post the stored dated for use elsewhere or for debuging provide a file location (/home/jonosur/public_html/runsbot.json) 
* supybot.plugins.Runsbot.isFirst
* supybot.plugins.Runsbot.isLoaded
* supybot.plugins.Runsbot.isWarmups
* supybot.plugins.Runsbot.public

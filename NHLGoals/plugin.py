###
# Copyright (c) 2022, graetful
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions, and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions, and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the author of this software nor the name of
#     contributors to this software may be used to endorse or promote products
#     derived from this software without specific prior written consent.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

###
from random import randint, random
import datetime
import string
import pendulum
import requests
from supybot import utils, plugins, ircutils, callbacks
import supybot.schedule as schedule
from supybot.commands import *
try:
    from supybot.i18n import PluginInternationalization
    _ = PluginInternationalization('NHLGoals')
except ImportError:
    # Placeholder that allows to run the plugin on a bot
    # without the i18n module
    _ = lambda x: x

ctable = {
        "1": "\0034,4 \x0F\x02 NJD",
        "2": "\00312,12 \x0F\x02 NYI",
        "3": "\0032,2 \x0F\x02 NYR",
        "4": "\0037,7 \x0F\x02 PHI",
        "5": "\0038,8 \x0F\x02 PIT",
        "6": "\0038,8 \x0F\x02 BOS",
        "7": "\0032,2 \x0F\x02 BUF",
        "8": "\0034,4 \x0F\x02 MTL",
        "9": "\0034,4 \x0F\x02 OTT",
        "10": "\0032,2 \x0F\x02 TOR",
        "12": "\0034,4 \x0F\x02 CAR",
        "13": "\0032,4 \x0F\x02 FLA",
        "14": "\0032,2 \x0F\x02 TBL",
        "15": "\0034,4 \x0F\x02 WSH",
        "16": "\0034,4 \x0F\x02 CHI",
        "17": "\0034,4 \x0F\x02 DET",
        "18": "\0038,8 \x0F\x02 NSH",
        "19": "\0032,2 \x0F\x02 STL",
        "20": "\0034,4 \x0F\x02 CGY",
        "21": "\00313,13 \x0F\x02 COL",
        "22": "\0037,7 \x0F\x02 EDM",
        "23": "\0032,2 \x0F\x02 VAN",
        "24": "\0037,7 \x0F\x02 ANA",
        "25": "\0033,3 \x0F\x02 DAL",
        "26": "\00315,15 \x0F\x02 LAK",
        "28": "\00311,11 \x0F\x02 SJS",
        "29": "\0032,2 \x0F\x02 CBJ",
        "30": "\0033,3 \x0F\x02 MIN",
        "52": "\00312,12 \x0F\x02 WPG",
        "53": "\00313,13 \x0F\x02 ARI",
        "54": "\0038,8 \x0F\x02 VGK",
        "55": "\00310,10 \x0F\x02 SEA",
    }
teamsList = {'ANA': {'long': 'Anaheim Ducks', 'short': 'Ducks'}, 
        'BOS': {'long': 'Boston Bruins', 'short': 'Bruins'},
        'BUF': {'long': 'Buffalo Sabres', 'short': 'Sabres'}, 
        'CGY': {'long': 'Calgary Flames', 'short': 'Flames'}, 
        'CAR': {'long': 'Carolina Hurricanes', 'short': 'Hurricanes'}, 
        'CHI': {'long': 'Chicago Blackhawks', 'short': 'Blackhawks'}, 
        'COL': {'long': 'Colorado Avalanche', 'short': 'Avalanche'}, 
        'CBJ': {'long': 'Columbus Blue Jackets', 'short': 'Blue Jackets'}, 
        'DAL': {'long': 'Dallas Stars', 'short': 'Stars'}, 
        'DET': {'long': 'Detroit Red Wings', 'short': 'Red Wings'}, 
        'EDM': {'long': 'Edmonton Oilers', 'short': 'Oilers'}, 
        'FLA': {'long': 'Florida Panthers', 'short': 'Panthers'}, 
        'LAK': {'long': 'Los Angeles Kings', 'short': 'Kings'}, 
        'MIN': {'long': 'Minnesota Wild', 'short': 'Wild'}, 
        'MTL': {'long': 'Montreal Canadiens', 'short': 'Canadiens'}, 
        'NSH': {'long': 'Nashville Predators', 'short': 'Predators'}, 
        'NJD': {'long': 'New Jersey Devils', 'short': 'Devils'}, 
        'NYI': {'long': 'New York Islanders', 'short': 'Islanders'}, 
        'NYR': {'long': 'New York Rangers', 'short': 'Rangers'}, 
        'OTT': {'long': 'Ottawa Senators', 'short': 'Senators'}, 
        'PHI': {'long': 'Philadelphia Flyers', 'short': 'Flyers'}, 
        'ARI': {'long': 'Arizona Coyotes', 'short': 'Coyotes'}, 
        'PIT': {'long': 'Pittsburgh Penguins', 'short': 'Penguins'}, 
        'STL': {'long': 'St. Louis Blues', 'short': 'Blues'}, 
        'SJS': {'long': 'San Jose Sharks', 'short': 'Sharks'}, 
        'SEA': {'long': 'Seattle Kraken', 'short':'Kraken'},
        'TBL': {'long': 'Tampa Bay Lightning', 'short': 'Lightning'}, 
        'TOR': {'long': 'Toronto Maple Leafs', 'short': 'Maple Leafs'}, 
        'VAN': {'long': 'Vancouver Canucks', 'short': 'Canucks'}, 
        'WSH': {'long': 'Washington Capitals', 'short': 'Capitals'}, 
        'WPG': {'long': 'Winnipeg Jets', 'short': 'Jets'}, 
        'VGK': {'long': 'Vegas Golden Knights', 'short': 'Knights'}}

class NHLGoals(callbacks.Plugin):
    """This plugin is to fetch videos of NHL Goals from the NHL API"""
    threaded = True
    def __init__(self, irc):
        self.__parent = super(NHLGoals, self)
        self.__parent.__init__(irc)
        self.events = {}
        self.plays = {}

    def tiny(self, url):
        shorturl = requests.get("http://tinyurl.com/api-create.php?url={}".format(url))
        return shorturl.text

    def _repeat(self, irc, msg, args, name, gameid, now=True):
        f = self._findvid
        id = schedule.addPeriodicEvent(f, 60, name, now, args=(irc, msg, args, name, gameid))
        assert id == name
        self.events[name] = gameid

    def _remove(self, irc, name):
        if name in self.events:
                del self.events[name]
                schedule.removeEvent(name)
 
    def _findvid(self, irc, msg, args, name, gameid):
        curl = "https://statsapi.web.nhl.com/api/v1/game/{}/content/".format(gameid)
        resp = self._fvid(irc, curl, name)

    def _fvid(self, irc, curl, name):
        ccontent = requests.get(curl).json()
        for each in ccontent['highlights']['scoreboard']['items']:
            kwords = list('{}'.format(i['value']) for i in each['keywords'])
            for i in kwords:
                if str(i) == str(name):
                    for v in each['playbacks']:
                        if v['name'] == 'FLASH_1800K_896x504':
                            video = v['url']
                            vurl = self.tiny(video)
                            irc.reply('\x02{}\x02: {} - {}'.format(self.plays[name]['who'], self.plays[name]['desc'], vurl))
                            f = self._remove
                            schedule.addEvent(f, 1, args=(irc, name))


    def goals(self, irc, msg, args, team, num, date):
        """<team> <#> [<date>]
        Gets the goal video for team and goal number specified. If goal is in database but video not generated a scheduler will be created and announce it when found."""
        if date is None:
            result = datetime.datetime.now()
        elif date == "yesterday":
            result = datetime.datetime.now() - datetime.timedelta(1)
        elif date == "tomorrow":
            result = datetime.datetime.now() + datetime.timedelta(1)
        elif date == "nextweek":
            result = datetime.datetime.now() + datetime.timedelta(7)
        elif date == "lastweek":
            result = datetime.datetime.now() - datetime.timedelta(7)
        elif date == "today":
            result = datetime.datetime.now()
        else:
            for form in ["%d%b", "%d %b", "%b%d", "%b %d", "%d%B", "%d %B", "%b%B", "%b %B", "%B %d", "%B%d", "%Y%m%d", "%Y-%m-%d", "%m%d"]:
                try:
                    result = datetime.datetime.strptime(date, form)
                    #If year isn't mentioned datetime will default to 1900
                    if "%Y" not in form:
                        year = datetime.datetime.now().year
                        result = result.replace(year=year)
                except:
                    pass
        if result is None:
            return None
        day = result.day
        month = result.month
        year = result.year
        date = '{}-{}-{}'.format(year, month, day)
        playing = []
        teamsListbyShort = {y['short']:{'long':y['long'],'abb':x,'short':y['short']} for x, y in teamsList.items()}
        valid = ' '.join(list(teamsList.keys()))
        if team.upper() not in teamsList.keys():
            irc.reply('Valid Teams: {}'.format(valid))
            return
        games = {}
        if date:
            url = "https://statsapi.web.nhl.com/api/v1/schedule?hydrate=team&date={}".format(date)
        else:
            url = "https://statsapi.web.nhl.com/api/v1/schedule?hydrate=team"
        content = requests.get(url).json()
        if len(content.get('dates')) == 0:
            irc.reply('No game found for {} on {}'.format(team.upper(), date))
            return
        for each in content['dates'][0]['games']:
            away = each['teams']['away']['team']['abbreviation']
            home = each['teams']['home']['team']['abbreviation']
            games[each['gamePk']] = []
            games[each['gamePk']].append(home)
            games[each['gamePk']].append(away)
            games[each['gamePk']].append(each['status']['statusCode'])
            playing.append(home)
            playing.append(away)
        count = 0
        goalsList = {}
        if team.upper() not in playing:
            date = pendulum.now().format('YYYY-MM-DD')
            irc.reply('No game found for {} on {}!'.format(team.upper(), date))
            return
        for x,y in games.items():
            if team.upper() in y:
                if y[2] == "1":
                        irc.reply('Game found for {} on {} but not started yet!'.format(team.upper(), date))
                        return
                feedurl = "https://statsapi.web.nhl.com/api/v1/game/{}/feed/live?hydrate=team".format(x)
                curl = "https://statsapi.web.nhl.com/api/v1/game/{}/content/".format(x)
                fcontent = requests.get(feedurl).json()
                away = y[1]
                home = y[0]
                gameid = x
                for each in fcontent['liveData']['plays']['allPlays']:
                    id = each['result']['eventTypeId']
                    if id == "GOAL":
                        who = each['team']['triCode']
                        cwho = ctable[str(each['team']['id'])]
                        if team.upper() == who:
                            desc = each['result']['description']
                            per = each['about']['ordinalNum']
                            clock = each['about']['periodTime']
                            perType = each['about']['periodType']
                            event = each['about']['eventId']
                            awayg = each['about']['goals']['away']
                            homeg = each['about']['goals']['home']
                            count = count + 1
                            try:
                                strength = each['result']['strength']['code']
                            except:
                                strength = ""
                            per = "{} {}".format(per, strength)
                            desc = "\x02\x1F[\x0F{} {} @ {} {} - {} {}\x02\x1F]\x0F {}\x0F {}".format(away,awayg, home, homeg, clock, per, cwho, desc)
                            goalsList[count] = ([id, who, event, desc])

        try:
                eid = goalsList[int(num)][2]
                desc = goalsList[int(num)][3]
                ccontent = requests.get(curl).json()
                for each in ccontent['highlights']['scoreboard']['items']:
                    kwords = list('{}'.format(i['value']) for i in each['keywords'])
                    for i in kwords:
                        if i == str(eid):
                            for v in each['playbacks']:
                                if v['name'] == 'FLASH_1800K_896x504':
                                    video = v['url']
                                    irc.reply("{} - {}".format(desc,self.tiny(video)))
                                    return
                if str(eid) in self.events:
                    irc.error(_('There is already a request for that goal video in the queue!'), Raise=True)
                irc.reply('{} - {}'.format(desc, "Video added to queue, I will let you know when it's ready!"))
                name = str(eid)
                self.plays[name] = {'who':msg.nick,
                                     'gameid':gameid,
                                     'event':name,
                                     'desc':desc}
                self._repeat(irc, msg, args, name, gameid)

                return
        except:
            irc.reply('{} Game found, but goal not found!'.format(team.upper()))

    goals = wrap(goals, (['somethingWithoutSpaces', 'somethingWithoutSpaces', optional('something')]))

    @wrap
    def goalrnd(self, irc, msg, args):
        """Returns a random NHL Goal Video from the API (between 2018,2023 and not months 7,8,9)"""
        irc.reply(self.getgoals(irc))

    def getgoals(self, irc):
        idate = []
        for i in range(0,25):
            e = datetime.date(randint(2018,2023), randint(1,12),randint(1,28))
            if e.month in [7,8,9]:
                continue
            idate.append(e.strftime('%Y-%m-%d'))
            for each in idate:
                content = requests.get('https://statsapi.web.nhl.com/api/v1/schedule?hydrate=team&date={}'.format(each)).json()
                try:
                    gameids = list('{}'.format(x['gamePk']) for x in content['dates'][0]['games'])
                except:
                    gameids = []
                for val in gameids:
                    url = "https://statsapi.web.nhl.com/api/v1/game/{}/content".format(val)
                    content = requests.get(url).json()
                    goals = []
                    try:
                        for each in content['media']['milestones']['items']:
                            if each['type'] == "GOAL":
                                date = each['timeAbsolute'].split('T')[0]
                                desc = each['highlight']['description']
                                cwho = ctable[each['teamId']]
                                gdesc = each['description']
                                per = each['ordinalNum']
                                time = each['periodTime']
                                teams = each['highlight']['blurb'].split(':')[0]
                                for v in each['highlight']['playbacks']:
                                    if "1800K" in v['name']:
                                       url = v['url']
                                       date = pendulum.parse(date).format('ddd MMM Do YYYY')
                                       return'{}\x0F: {}[{}/{}] {} on {} -- \x02{}\x02'.format(cwho, gdesc, time, per, desc, date, self.tiny(url))
                    except:
                        pass
          
Class = NHLGoals


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:

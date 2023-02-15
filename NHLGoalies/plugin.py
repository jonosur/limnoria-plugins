###
# Copyright (c) 2023, grateful
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

import requests
from bs4 import BeautifulSoup
from datetime import datetime
from supybot import utils, plugins, ircutils, callbacks
from supybot.commands import *
from supybot.i18n import PluginInternationalization
import pendulum

_ = PluginInternationalization('NHLGoalies')

gstatus = {}
gtime = 0
gstring = ''
ctable = {'NJD': '1', 'NYI': '2', 'NYR': '3', 'PHI': '4', 'PIT': '5', 'BOS': '6', 'BUF': '7', 'MTL': '8', 'OTT': '9', 'TOR': '10', 'CAR': '12', 'FLA': '13', 'TBL': '14', 'WSH': '15', 'CHI': '16', 'DET': '17', 'NSH': '18', 'STL': '19', 'CGY': '20', 'COL': '21', 'EDM': '22', 'VAN': '23', 'ANA': '24', 'DAL': '25', 'LAK': '26', 'SJS': '28', 'CBJ': '29', 'MIN': '30', 'WPG': '52', 'ARI': '53', 'VGK': '54', 'SEA': '55'}

cids = {
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

class NHLGoalies(callbacks.Plugin):
    """This plugin is used to fetch NHL Goalie starting information"""
    threaded = True

    def _getgoalies(self):
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
            'SEA': {'long': 'Seattle Kraken', 'short': 'Kraken'}, 
            'TBL': {'long': 'Tampa Bay Lightning', 'short': 'Lightning'}, 
            'TOR': {'long': 'Toronto Maple Leafs', 'short': 'Maple Leafs'}, 
            'VAN': {'long': 'Vancouver Canucks', 'short': 'Canucks'}, 
            'WSH': {'long': 'Washington Capitals', 'short': 'Capitals'}, 
            'WPG': {'long': 'Winnipeg Jets', 'short': 'Jets'}, 
            'VGK': {'long': 'Vegas Golden Knights', 'short': 'Knights'}}
        teamsListbyShort = {y['short']:{'long':y['long'],'abb':x,'short':y['short']} for x, y in teamsList.items()}
        valid = ' '.join(list(teamsList.keys()))
        url = "https://www.leftwinglock.com/starting-goalies/"
        headers = {'Host':'www.leftwinglock.com','User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36'}
        content = requests.get(url, headers=headers)
        soup = BeautifulSoup(content.text, 'html.parser')
        names = []
        for each in soup.find_all('h4', {'class':'comparison__person-full-name'}):
            last = str(each).split('</a></span>')[-1].strip('</h4>').lstrip(' ')
            first = each.a.text.replace('\xa0','')
            name = "{} {}".format(first, last)
            names.append(name)       
        status = []
        status2 = []
        for each in soup.find_all('div', {'class':'comparison__person-wrapper-info'}):
            stxt = each.text.replace('\n','')
            status2.append(stxt)
            if stxt == 'Projected' or stxt =='Likely':
                stxt = "\0038\x02{}\x0F".format(stxt)
            if stxt == 'Confirmed':
                stxt = "\0033\x02{}\x0F".format(stxt)
            if stxt == 'Unconfirmed':
                stxt = "\0034\x02{}\x0F".format(stxt)
            status.append(stxt)
        teams = []
        for each in soup.find_all('div', {'class':'comparison__person-team'}):
            teams.append(each.text.replace('\n',''))
        stats = []
        for each in soup.find_all('ul', {'class':'comparison__person-footer-list'}):
            stats.append(' | '.join('{}'.format(i.text) for i in each.find_all('li')))
        times = []
        for each in soup.find_all('h5', {'class':'comparison__versus-place'}):
            times.append(each.text.split('Eastern ')[-1])
            times.append(each.text.split('Eastern ')[-1])
        data = {}
        for a, b, c, d, e, f in zip(teams, status, stats, times, names, status2):
            short = teamsListbyShort[a.title()]['short']
            long = teamsListbyShort[a.title()]['long']
            abb = teamsListbyShort[a.title()]['abb']
            data[abb] = {'status':b,'stats':c,'time':d,'short':short,'long':long,'name':e,'status2':f,'abb':abb}
        goalies = data
        return goalies


    def outgames(self):
        dt = pendulum.now().format('YYYY-MM-DD')
        content = requests.get("https://statsapi.web.nhl.com/api/v1/schedule?startDate={}&endDate={}&hydrate=team,linescore,broadcasts(all),tickets,game(content(media(epg)),seriesSummary),radioBroadcasts,metadata,seriesSummary(series)&site=en_nhlCA&teamId=&gameType=&timecode=".format(dt, dt)).json()
        games = {}
        for each in content['dates'][0]['games']:
            home = each['teams']['home']['team']['abbreviation']
            away = each['teams']['away']['team']['abbreviation']
            pt = pendulum.parse(each['gameDate']).in_tz('America/New_York').format('h:mmA zz')
            blist = ', '.join('{}'.format(x['name']) for x in each['broadcasts'])
            outp = "{} @ {} {} | {}".format(away, home, pt, blist)
            games[away] = outp
            games[home] = outp
        return games


    def goalies(self, irc, msg, args, team):
        """<team>    !=stored data *=fresh data
        Returns the starting goalie information for team."""
        global gstatus
        global gtime
        global gstring
        ogames = self.outgames()
        if gtime == 0:
            gtime = datetime.now()
        else:
            otime = datetime.now() - gtime
        try:
            #if we find confirmed status in stored and havent done a pull in under an hour?
            if (gstatus[team.upper()]['status2'] == 'Confirmed') and (otime.seconds < 3600):
                y = gstatus[team.upper()]
                x = ctable[y['abb']]
                z = cids[x]
                omsg = '{}\x0F {} ({}) is {} ({}) - last update {} [!]'.format(z,y['name'],y['stats'],y['status'],ogames[y['abb']],y['time'], gstring)
                irc.reply(omsg)
                return
        except:
            pass

        glist = self._getgoalies()
        gtime = datetime.now()
        gstring = datetime.now().strftime('%Y-%m-%d %H:%M:%S%p')
        y = glist[team.upper()]
        x = ctable[y['abb']]
        z = cids[x]
        omsg = '{}\x0F {} ({}) is {} ({}) - last update {} [*]'.format(z,y['name'],y['stats'],y['status'],ogames[y['abb']],y['time'], gstring)
        irc.reply(omsg)
        gstatus = glist

    goalies = wrap(goalies, (['somethingWithoutSpaces']))

Class = NHLGoalies


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:

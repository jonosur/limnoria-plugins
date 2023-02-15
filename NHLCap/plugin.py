###
# Copyright (c) 2017, grateful
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
from bs4 import BeautifulSoup
import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
import re
import requests
try:
    from supybot.i18n import PluginInternationalization
    _ = PluginInternationalization('NHLCap')
except ImportError:
    # Placeholder that allows to run the plugin on a bot
    # without the i18n module
    _ = lambda x: x


class NHLCap(callbacks.Plugin):
    """Returns NHL Teams Salary Cap Information"""
    threaded = True

    def FindTeam(self, search):
        teams_list = ['Anaheim Ducks','Boston Bruins','Buffalo Sabres','Calgary Flames','Carolina Hurricanes',
            'Chicago Blackhawks','Colorado Avalanche','Columbus Blue Jackets','Dallas Stars','Detroit Red Wings',
            'Edmonton Oilers','Florida Panthers','Los Angeles Kings','Minnesota Wild','Montreal Canadiens',
            'Nashville Predators','New Jersey Devils','New York Islanders','New York Rangers','Ottawa Senators',
            'Philadelphia Flyers','Arizona Coyotes','Pittsburgh Penguins','St. Louis Blues','San Jose Sharks',
            'Tampa Bay Lightning','Toronto Maple Leafs','Vancouver Canucks','Washington Capitals','Winnipeg Jets',
            'Vegas Golden Knights','Seattle Kraken']

        teams_list_abbrev = ['ANA','\0038,1 BOS \x0F','BUF','CGY','CAR','CHI','COL','CBJ','DAL','DET','EDM','FLA','LAK','MIN','MTL',
            'NSH','NJD','NYI','NYR','OTT','PHI','ARI','PIT','STL','SJS','TBL','TOR','VAN','WSH','WPG','VGK','SEA']

        teams_string = "{}".format(', '.join(teams_list_abbrev))

        find_match = -1
        if search:
            search = search.title()
        for team in teams_list:
            find_match = find_match + 1
            if search == team:
                return(teams_list_abbrev[find_match])


    def cap(self, irc, msg, args, search):
        """<player>
        Returns Salary Cap Information
        """
        url="https://www.capfriendly.com/search?s={}".format(search.replace(" ", "+"))
        content = requests.get(url).text
        soup = BeautifulSoup(content, "html.parser")
        try:
            results = soup.find_all('h5')[1].text
            if results == "Player Results: 0":
                irc.reply("Player not found: {}".format(search))
                return
        except:
            pass
        try:
            table = soup.tbody.find_all('a')[0]
            href = table.get('href')
            link = "https://www.capfriendly.com" + href
            content = requests.get(link).text
            soup = BeautifulSoup(content, "html.parser")
        except:
            pass

        name = soup.h1.get_text().title()
        team = self.FindTeam(soup.h3.text)
        exempt = re.search("Waivers Exempt", content, re.S)
        try:
            current = soup.find('div', attrs={'class':'contract_data'})
        except:
            error = soup.find('div', attrs={'class':'err show'})
            irc.reply("{} : {}".format(name, error))
            return
        divs = current.find_all('div')
        count = -1
        lenght = divs[5].text.title()
        value = divs[7].text.title()
        ch = "{} | {} | {}".format(divs[9].text.title(), divs[10].text.title(), divs[12].text.title()).replace('% :','%:')
        signing_date = divs[11].text.title()
        rows = soup.tbody.find_all('tr')
        last = rows[-2].find_all('td')
        pbonus = last[4].text
        sbonus = last[5].text
        expiry = last[0].text
        try:
            estatus = divs[6].text
        except:
            estatus = 'N/A'

        nmc = last[1].text
        cap_hit = last[2].text
        contract_type = divs[0].h6.text.title()
        if nmc != "":
            cap_hit = "{} | {}".format(cap_hit, nmc)
        if exempt:
            expiry = "Expiry After {} Season | {}".format(expiry, exempt.group())
        else:
            expiry = "Expiry After {} Season".format(expiry)
        cap_hit = "Cap Hit: {} | Performance Bonus: {} | Signing Bonus: {}".format(cap_hit, pbonus, sbonus)
        output = "\x02{}\x02 :: {} | {} | {} | {} | {} | {} | {} | {} | {}".format(name,
                                                                                            team,
                                                                                            lenght,
                                                                                            contract_type,
                                                                                            value,
                                                                                            ch,
                                                                                            signing_date,
                                                                                            cap_hit,
                                                                                            expiry, estatus)
        irc.reply(output.replace('EXPIRY STATUS','Exp. Status'))
    cap = wrap(cap, ([('text')]))

    def teamcap(self, irc, msg, args, team):
        """<team>
        Returns Team Salary Cap Information
        """
        team = team.upper()

        nhl = ["ANA","BOS","BUF","CGY","CAR","CHI","COL","CBJ","DAL","DET","EDM","FLA","LAK","MIN","MTL",
        "NSH","NJD","NYI","NYR","OTT","PHI","ARI","PIT","STL","SJS","TBL","TOR","VAN","VGK","WSH","WPG","SEA"]

        nhlteamlist = "{}".format(' '.join(nhl))

        if team not in nhlteamlist:
            irc.reply("Valid Teams: {}".format(nhlteamlist))
            return

        if team == "ANA":
            team = "Ducks"
        if team == "BOS":
            team = "Bruins"
        if team == "BUF":
            team = "Sabres"
        if team == "CGY":
            team = "Flames"
        if team == "CAR":
            team = "Hurricanes"
        if team == "CHI":
            team = "Blackhawks"
        if team == "COL":
            team = "Avalanche"
        if team == "CBJ":
            team = "BlueJackets"
        if team == "DAL":
            team = "Stars"
        if team == "DET":
            team = "RedWings"
        if team == "EDM":
            team = "Oilers"
        if team == "FLA":
            team = "Panthers"
        if team == "LAK":
            team = "Kings"
        if team == "MIN":
            team = "Wild"
        if team == "MTL":
            team = "Canadiens"
        if team == "NSH":
            team = "Predators"
        if team == "NJD":
            team = "Devils"
        if team == "NYI":
            team = "Islanders"
        if team == "NYR":
            team = "Rangers"
        if team == "OTT":
            team = "Senators"
        if team == "PHI":
            team = "Flyers"
        if team == "ARI":
            team = "Coyotes"
        if team == "PIT":
            team = "Penguins"
        if team == "STL":
            team = "Blues"
        if team == "SJS":
            team = "Sharks"
        if team == "TBL":
            team = "Lightning"
        if team == "TOR":
            team = "MapleLeafs"
        if team == "VAN":
            team = "Canucks"
        if team == "VGK":
            team = "GoldenKnights"
        if team == "WSH":
            team = "Capitals"
        if team == "WPG":
            team = "Jets"
        if team == "SEA":
            team = "Kraken"

        url = "https://www.capfriendly.com/teams/" + team
        content = requests.get(url)
        soup = BeautifulSoup(content.text, 'html.parser')
        header = soup.find('div', {'class':'c'})
        d1 = soup.find_all('div', {'class':'c'})[3]
        a1 = d1.find_all('h5')[0].text.title().replace('  ','').replace("'S",'s').split(':')[1]
        a2 = d1.find_all('h5')[1].text.title().replace('  ','').replace("'S",'s').split(':')[1]
        a3 = d1.find_all('h5')[2].text.title().replace('  ','').replace("'S",'s').split(':')[1]
        a4 = d1.find_all('div')[0].text.title().replace('  ','').replace("'S",'s').split(':')[1]
        a5 = d1.find_all('div')[1].text.title().replace('  ','').replace("'S",'s').split(':')[1]
        a6 = d1.find_all('div')[2].text.title().replace('  ','').replace("'S",'s').split(':')[1]
        table = re.search("class=\"mb5\">(.*?)<\/div><\/div>", content.text, re.S)
        try:
            numbers = re.findall("<span class=\"num.*?>(.*?)</span>", table.group(0), re.S)
        except:
            numbers = ""
        other = re.search("class=\"mt5\">(.*?)<\/div><div>(.*?)<\/div>", content.text, re.S)
        roster = other.group(1)
        contracts = other.group(2)

        roster = re.sub('ROSTER SIZE', '\x02Roster Size\x02', roster)
        contracts = re.sub('CONTRACTS', '\x02Contracts\x02', contracts)
        irc.reply("\x02\x1F{} Salary Information\x02\x0F".format(team))
        msgrow1 = "\x02Projected Cap Hit\x02:   {:12} \x02Projected LTIR Used\x02: {:12} \x02Current Cap Space\x02: {:12}".format(a1, a2, a3)
        msgrow2 = "\x02Projected Cap Space\x02: {:12} \x02Deadline Cap Space\x02:  {:12} \x02Today's Cap Hit\x02:   {:12}".format(a4, a5, a6)

        irc.reply(msgrow1)
        irc.reply(msgrow2)
        irc.reply("{} {}".format(roster, contracts))

    teamcap = wrap(teamcap, ([('somethingWithoutSpaces')]))


Class = NHLCap


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:

###
# Copyright (c) 2017, Jonathan "grateful" Surman
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     thisc list of conditions, and the following disclaimer.
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
import time
import datetime
import re
import urllib.request as urlreq
import urllib.parse as urlparse
import urllib
import supybot.ircdb as ircdb
import supybot.schedule as schedule

import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
import supybot.ircmsgs as ircmsgs
try:
    from supybot.i18n import PluginInternationalization
    _ = PluginInternationalization('Injuries')
except ImportError:
    # Placeholder that allows to run the plugin on a bot
    # without the i18n module
    _ = lambda x: x

# User-Agent field to send when downloading url (some pages require one of firefox, chrome, ie etc.)
_USER_AGENT = "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0"
# Accept-Language field to send when downloading url (this one should be fine, english - USA)
_ACCEPT_LANGUAGE = "en-US;q=0.7,en;q=0.3"
# time in seconds to keep data in cache
_CACHE_TIME = 300
# number of download cache slots
_CACHE_SLOTS = 50
# don't cache download if number of characters is greater this one (prevents caching very large pages)
_CACHE_MAXCHARS = 50000
# if UTF-8 decoding of downloaded data fails, use this one (west european i think)
# will cause some garbage/weird letters for non-ascii (>127) characters, but usually is fine
_FAILSAFE_HTTP_ENCODING = "ISO-8859-1"
# download result: success
DL_OK = 0
# download result: error 404: Not Found
DL_HTTP404 = 1
# download result: some other http error (ie. 5xx - server failure)
DL_HTTP_ERROR = 2
# download result: general network-level error (ie. non-existent url or no route to host)
DL_NET_ERROR = 3
# download result: other errors - for example out of memory, system socket failure
DL_OS_ERROR = 4

class Injuries(callbacks.Plugin):
    """Returns NHL Injuries from RotoWorld"""
    threaded = True

    def __init__(self, irc):
        # set __parent - double _ means that coder really really doesn't it to be accessed out
        # of script. __parent will hold parent class - which is "callbacks.Plugin"
        self.__parent = super(Injuries, self)
        # call parent's init method - so plugin is initiated properly
        self.__parent.__init__(irc)

=

    def injuries(self, irc, msg, args, league, team):
        """[league] [team]
        Returns NHL, MLB, NBA, NFL Injuries for specific [team].
        """
        team = team.upper()
        league = league.upper()
        nhl = ["ANA","BOS","BUF","CGY","CAR","CHI","COL","CBJ","DAL","DET","EDM","FLA","LAK","MIN","MTL",
        "NSH","NJD","NYI","NYR","OTT","PHI","ARI","PIT","STL","SJS","TBL","TOR","VAN","WSH","WPG"]
        mlb = ["BOS","NYY","ARI","ATL","BAL","CHC","CWS","CIN","CLE","COL","DET","MIA","HOU",
        "KC","LAA","LAD","MIL","MIN","NYM","OAK","PHI","PIT","SD","SF","SEA","STL","TB","TEX","TOR","WSH"]
        nba = ["ATL", "BKN", "BOS", "CHA", "CHI", "CLE", "DAL", "DEN", "DET", "GSW", "HOU", "IND", "LAC", "LAK",
        "MEM", "MIA", "MIL", "MIN", "NOP", "NYK", "OKC", "ORL", "PHI", "PHX", "POR", "SAC", "SAS", "TOR", "UTA", "WAS"]
        nfl = ["ARZ", "ATL", "BAL", "BUF", "CAR", "CHI", "CIN", "CLE", "DAL", "DEN", "DET", "GB", "HOU", "IND", "JAC",
        "KC", "LAC", "LAR", "MIA", "MIN", "NE", "NO", "NYG", "NYJ", "OAK", "PHI", "PIT", "SEA", "SF", "TB", "TEN", "WAS"]


        nhlteamlist = "{}".format(' '.join(nhl))
        mlbteamlist = "{}".format(' '.join(mlb))
        nbateamlist = "{}".format(' '.join(nba))
        nflteamlist = "{}".format(' '.join(nfl))

        if league in "NHL":
            if team not in nhl:
                irc.reply("Valid Teams: {}".format(nhlteamlist))
                return
            if team in "CGY":
                team = "CAL"
            if team in "CBJ":
                team = "CLS"
            if team in "MTL":
                team = "MON"
            if team in "WSH":
                team = "WAS"
            if team in "NSH":
                team = "NAS"
            if team in "TBL":
                team = "TB"
            if team in "LAK":
                team = "LA"
            url = "https://www.rotowire.com/hockey/tables/injury-report.php?team={}&pos=ALL".format(team)

        elif league in "MLB":
            if team not in mlbteamlist:
                irc.reply("Valid Teams: {}".format(mlbteamlist))
                return
            if team in "ARI":
                team = "ARZ"
            if team in "LAD":
                team = "LA"
            if team in "WSH":
                team = "WAS"

            url = "https://www.rotowire.com/baseball/tables/injury-report.php?team={}&pos=ALL".format(team)
        elif league in "NBA":
            if team not in nbateamlist:
                irc.reply("Valid Teams: {}".format(nbateamlist))
                return
            if team in "GWS":
                team = "GW"
            if team in "MIL":
                team = "MLW"
            if team in "NOP":
                team = "NO"
            if team in "NYK":
                team = "NY"
            if team in "PHX":
                team = "PHO"
            if team in "SAC":
                team = "SA"
            if team in "SAS":
                team = "SAC"

            url = "https://www.rotowire.com/basketball/tables/injury-report.php?team={}&pos=ALL".format(team)
        elif league in "NFL":
            if team not in nflteamlist:
                irc.reply("Valid Teams: {}".format(nflteamlist))
                return
            url = "https://www.rotowire.com/football/tables/injury-report.php?team={}&pos=ALL".format(team)
        else:
            irc.reply("Leagues Allowed: NHL, MLB, NBA, NFL")
            return
        content = requests.get(url).json()
        alist = []
        for each in content:
            alist.append('{} {} - {} ({})'.format(each['position'],each['player'],each['injury'],each['status']))
        irc.reply('{} - {}'.format(team, ' | '.join(alist)))

    injuries = wrap(injuries, (['somethingWithoutSpaces', 'somethingWithoutSpaces']))

Class = Injuries

# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:

###
# Copyright (c) 2017, grateful
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
import re
from bs4 import *

import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
import supybot.ircmsgs as ircmsgs
try:
    from supybot.i18n import PluginInternationalization
    _ = PluginInternationalization('NHLRookies')
except ImportError:
    # Placeholder that allows to run the plugin on a bot
    # without the i18n module
    _ = lambda x: x

class NHLRookies(callbacks.Plugin):
    """This plugin fetches data for Rookie Skaters in the National Hockey League"""
    threaded = True

    def __init__(self, irc):
        # set __parent - double _ means that coder really really doesn't it to be accessed out
        # of script. __parent will hold parent class - which is "callbacks.Plugin"
        self.__parent = super(NHLRookies, self)
        # call parent's init method - so plugin is initiated properly
        self.__parent.__init__(irc)

    def rookies(self, irc, nick, channel, number):
        """<number>
        Returns NHL Rookie Leaders, <number> specifies how many results to show.
        """
        url = "http://www.nhl.com/ice/rookies.htm"
        content = requests.get(url)
        soup = BeautifulSoup(content.text, "lxml")

        table = soup.find('table', attrs={'class':'data stats'})
        # find all table rows, exclude first one (column names) and second (table footer, with page numbers)
        stats = table.find_all('tr')[2:]
        playerlist = []
        for i in range(0, 7):
            row = stats[i].find_all('td')
            rank, player, team, pos, gp, goals, assists, points, plusminus, pim, ppg, ppp, shg, shp, gw, ot, shots, pct, toi, shift, fo = tuple(map(lambda r: r.text, row))[:21]
            playerlist.append(player)
        name_l = max(len(x) for x in playerlist)
        name_l = int(name_l) + 1

        fmt = "{:2} {:20} {:4} {:3} {:3} {:3} {:3} {:3} {:8} {:3} {:3} {:4} {:5} {:5}"
        fmth = "\x1F{:2} {:20} {:4} {:3} {:3} {:3} {:3} {:3} {:4} {:3} {:3} {:4} {:5} {:5}\x1F".format("Rk", "Player", "Team", "Pos", "GP", "G", "A", "P", "+/-", "PIM", "PPG", "SOG", "SHOT%", "GWG")
        irc.reply(fmth)

        for i in range(0, 7):
            # row is now list of fields
            row = stats[i].find_all('td')
            # here's trick, similar to perl - apply r -> r.text to every element of row
            # (get field content from field object)
            # then turn it tuple (because result is map object), and truncate tuple to 21 elements
            rank, player, team, pos, gp, goals, assists, points, plusminus, pim, ppg, ppp, shg, shp, gw, ot, shots, pct, toi, shift, fo = tuple(map(lambda r: r.text, row))[:21]
            player = re.sub("<.*?>", "", player)
            team = re.sub("<.*?>", "", team)

            if int(plusminus) > 0:
                plusminus = ircutils.mircColor(plusminus, "green")
            elif int(plusminus) < 0:
                plusminus = ircutils.mircColor(plusminus, "red")
            else:
                plusminus = " E"
                plusminus = ircutils.mircColor(plusminus, "orange")

            msgrow = fmt.format(rank, player, team, pos, gp, goals, assists, points, plusminus, pim, ppg, shots, pct, gw)
            irc.reply(msgrow)

    rookies = wrap(rookies, [optional("positiveInt")])

Class = NHLRookies

# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:

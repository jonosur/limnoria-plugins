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
from bs4 import BeautifulSoup
import requests
import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
import supybot.ircmsgs as ircmsgs
try:
    from supybot.i18n import PluginInternationalization
    _ = PluginInternationalization('NHLLottery')
except ImportError:
    # Placeholder that allows to run the plugin on a bot
    # without the i18n module
    _ = lambda x: x


class NHLLottery(callbacks.Plugin):
    """This plugin fetches NHL Lottery Odds/Results for the NHL Entry Draft"""
    threaded = True

    def __init__(self, irc):
        # set __parent - double _ means that coder really really doesn't it to be accessed out
        # of script. __parent will hold parent class - which is "callbacks.Plugin"
        self.__parent = super(NHLLottery, self)
        # call parent's init method - so plugin is initiated properly
        self.__parent.__init__(irc)

    @wrap
    def lottery(self, irc, msg, args):
        """
        Returns NHL Lottery Odds/Results for Draft from Tankathon.com
        """
        url = "http://www.tankathon.com/nhl/"
        content = requests.get(url)
        soup = BeautifulSoup(content.text, "html.parser")
        msgrow = "\x1F\x02{:1} {:4} {:8} {:3} {:7} {:3} {:8} {:6} {:6}".format('', 'Team', 'Record', 'Pts', 'PPG', 'RW', 'Streak', 'L10', 'Odds')
        irc.reply(msgrow)
        for each in soup.table.find_all('tr')[2:15]:
            try:
                Pick, Team, RecordRec, Pts, PPG, ROW, Streak, L10, Odds, Top3 = each.find_all('td')
                msgrow = "{:1} {:4} {:8} {:3} {:7} {:3} {:8} {:6} \x02{:6}\x0F".format(Pick.text, Team.find('div', {'class':'mobile'}).text, RecordRec.text, Pts.text, PPG.text, ROW.text, Streak.text, L10.text, Top3.text)
                irc.reply(msgrow)
            except:
                pass

Class = NHLLottery

# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:

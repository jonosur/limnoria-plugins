##
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
from bs4 import BeautifulSoup
import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
import supybot.ircmsgs as ircmsgs
try:
    from supybot.i18n import PluginInternationalization
    _ = PluginInternationalization('RotoNews')
except ImportError:
    # Placeholder that allows to run the plugin on a bot
    # without the i18n module
    _ = lambda x: x

class RotoNews(callbacks.Plugin):
    """This plugin fetches recent news information from RotoWire.com""" 
    threaded = True

    def __init__(self, irc):
        # set __parent - double _ means that coder really really doesn't it to be accessed out
        # of script. __parent will hold parent class - which is "callbacks.Plugin"
        self.__parent = super(RotoNews, self)
        # call parent's init method - so plugin is initiated properly
        self.__parent.__init__(irc)

    def remove_duplicates(self, listofElements):
    # Create an empty list to store unique elements
        uniqueList = []
    # Iterate over the original list and for each element
    # add it to uniqueList, if its not already there.
        for elem in listofElements:
            if elem not in uniqueList:
                uniqueList.append(elem)
    # Return the list of unique element
        return uniqueList


    def rotowire(self, irc, nick, args, player):
        """<player>
        Returns Player News from RotoWire.
        """
        surl = "https://www.rotowire.com/frontend/ajax/search-players.php?searchTerm={}".format(player)
        scontent = requests.get(surl).json()
        players = []
        for each in scontent['players']:
            players.append('{}'.format(each['name']))
        if len(players) == 0:
            irc.reply("No RotoWire news found for {}".format(player.title()))
            return
        url = "http://www.rotowire.com/{}".format(scontent['players'][0]['link'])
        content = requests.get(url)
        soup = BeautifulSoup(content.text, "html.parser")
        try:
            name = soup.find("h1", { "class" : "p-card__player-name" }).text
            age = soup.find("div", { "class" : "p-card__player-info" }).div.get_text().split(' ')[0]
            pos = soup.find("div", { "class" : "p-card__player-info" }).span.text
            info = soup.find("div", { "class" : "p-card__player-info" }).a.text
            irc.reply("\x1F\x02{} - {} {} for {}".format(name, age, pos, info))
        except:
            pass
        news = soup.find_all("div", { "class" : "news-update__main" })
        news = self.remove_duplicates(news)
        for item in news[:3]:
            latest_date = item.find("div", { "class" : "news-update__timestamp" })
            date = datetime.strptime(str(latest_date.text), "%B %d, %Y").strftime("%m/%d/%Y")
            latest_news = item.find("div", { "class" : "news-update__news" })
            irc.reply("\x02{}:\x0F {}".format(date, latest_news.text))
    rotowire = wrap(rotowire, (['text']))

Class = RotoNews

# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:

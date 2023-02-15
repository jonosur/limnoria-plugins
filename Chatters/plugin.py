###
# Copyright (c) 2019, grateful
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
import json
import pendulum
from supybot import utils, plugins, ircutils, callbacks, conf, world
from supybot.commands import *
import time, datetime, dateutil.tz, re

TIMEZONE = "USA/Pacific"
TIME_RE = re.compile(r"(\d+-\d+-\d+)")

try:
    from supybot.i18n import PluginInternationalization
    _ = PluginInternationalization('Chatters')
except ImportError:
    # Placeholder that allows to run the plugin on a bot
    # without the i18n module
    _ = lambda x: x

def date_from_stamp_timezone(stamp, timezone):
    return str(datetime.datetime.fromtimestamp(stamp, tz=dateutil.tz.gettz(timezone)))

globaldate = 0
globaltime = ""

def same_day(stamp1, stamp2):
    """returns True if timestamps belong to same day"""
    date1 = date_from_stamp_timezone(stamp1, TIMEZONE)
    date2 = date_from_stamp_timezone(stamp1, TIMEZONE)
    day1 = TIME_RE.match(date1).group(1)
    day2 = TIME_RE.match(date2).group(1)
    return day1 == day2

class ChattersDB(plugins.ChannelUserDB):

    def serialize(self, v):
        return list(v)
    
    def deserialize(self, channel, id, L):
        (wordcount, stamp) = L
        return (int(wordcount), float(stamp))
    
    def increase(self, channel, nick, amount):
        if (channel, nick) in self.keys():
            (count, stamp) = self[channel, nick]
        else:
            (count, stamp) = (0, time.time())

        if same_day(time.time(), stamp):
            self[channel, nick] = (count+amount, stamp)
        else:
            self[channel, nick] = (amount, stamp)

dbfilename = conf.supybot.directories.data.dirize("Chatters.db")

class Chatters(callbacks.Plugin):
    """The plugin stores daily and local channel activity to figure out whom the top chatters are"""
    threaded = True
    def __init__(self, irc):
        self.__parent = super(Chatters, self)
        self.__parent.__init__(irc)
        self.db = ChattersDB(dbfilename)
        world.flushers.append(self.db.flush)

    def die(self):
        self.db.flush()
        self.__parent.die()

    def doPrivmsg(self, irc, msg):
        global globaldate
        global globaltime
        date = pendulum.now().format("YYYYMMDD")
        chatz = []
        if int(globaldate) < int(date):
            open(dbfilename, 'w').close()
            self.db = None
            self.db = ChattersDB(dbfilename)
            globaldate = date
            globaltime = pendulum.now().format("MMM Do hh:MM A zz")

        channel = msg.args[0]
        message = msg.args[1]
        wordcount = len(message.split(" "))
        self.db.increase(channel, msg.nick, wordcount)

    @wrap([optional('text')])
    def topchatters(self, irc, msg, args, chan):
        """[<channel>]
        Returns the top ten most active chatters for specified channel on todays date.
        """
        global globaltime
        chatz = []
        # create a list of current channel (count, username)
        if chan:
            chan = chan.lower()
        else:
            chan = msg.args[0].lower()
        for key in self.db.keys():
            # if our channel
            if key[0].lower() == chan:
                stamp = self.db[key][1]
                amount = self.db[key][0]
                if not same_day(stamp, time.time()):
                    amount = 0
                chatz.append((amount, key[1]))
        chatz.sort(key=lambda item: item[0], reverse = True)
        cnt = 0
        result = []
        # first 10
        for item in chatz:
            cnt +=1
            if cnt > 10:
                break
            nick = item[1]
            nick = nick[0] + '*' + nick[1:]
            result.append("{} (\x02{}\x02)".format(nick, item[0]))

        if len(result) != 0:
            irc.reply("Top Chatters in \x1F\x02{}\x0F by Total Words as of {}: {}".format(chan, globaltime,", ".join(result)))
        else:
            irc.reply("I don't have any data for channel \x02{}\x0F.".format(chan))

Class = Chatters


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:

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
from postalcodes_ca import postal_codes
import pgeocode
import requests
from supybot import utils, plugins, ircutils, callbacks
from supybot.commands import *
from supybot.i18n import PluginInternationalization


_ = PluginInternationalization('OTA')


class OTA(callbacks.Plugin):
    """OTA Finder"""
    pass

    @wrap(['text'])
    def ota(self, irc, msg, args, opt):
        """<zipcode|postalcode> -- Canada and USA only"""
        if opt.isdigit():
            nomi = pgeocode.Nominatim('us')
            query = nomi.query_postal_code(opt)
            data = {
            "lat": query["latitude"],
            "lon": query["longitude"],
            "name": query["place_name"]
            }
            url = "https://www.antennasdirect.com/custom/transmitter-combo-query.php?latty={}&longy={}&action=mapping" 
            url = url.format(data['lat'], data['lon'])
            content = requests.get(url).json()
            ndict = {}
            nlist = []
            for each in content:
                ndict[each['call_sign']] = each
                nlist.append(each)

            kmlist = list('{}'.format(x['distance']) for x in nlist)
            slist = list('{}'.format(x['call_sign']) for x in nlist)
            new = list(zip(kmlist,slist))
            snew = sorted(new)
            sndict = {}
            for x,y in snew:
                sndict[y] = ndict[y]
            outm = ' \x02|\x02 '.join('{}: #{} {}km'.format(x['call_sign'], x['channel'], "{:.0f}".format(float(x['distance']))) for y,x in sndict.items())
            irc.reply('{} OTAS -- {}'.format(data['name'].upper(), outm))
        else:
            data = postal_codes[opt.upper()]
            url = "https://www.antennasdirect.com/custom/transmitter-combo-query.php?latty={}&longy={}&action=mapping"
            url = url.format(data.latitude, data.longitude)
            content = requests.get(url).json()
            ndict = {}
            nlist = []
            for each in content:
                ndict[each['call_sign']] = each
                nlist.append(each)

            kmlist = list('{}'.format(x['distance']) for x in nlist)
            slist = list('{}'.format(x['call_sign']) for x in nlist)
            new = list(zip(kmlist,slist))
            snew = sorted(new)
            sndict = {}
            for x,y in snew:
                sndict[y] = ndict[y]
            outm = ' \x02|\x02 '.join('{}: #{} {}km'.format(x['call_sign'], x['channel'], "{:.0f}".format(float(x['distance']))) for y,x in sndict.items())
            irc.reply('{} OTAS -- {}'.format(data.name.upper(), outm))

Class = OTA


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:

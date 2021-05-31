###
# Copyright (c) 2020, grateful
# All rights reserved.
#
#
###

import supybot.conf as conf
import supybot.registry as registry
try:
    from supybot.i18n import PluginInternationalization
    _ = PluginInternationalization('Runsbot')
except:
    # Placeholder that allows to run the plugin on a bot
    # without the i18n module
    _ = lambda x:x

def configure(advanced):
    # This will be called by supybot to configure this module.  advanced is
    # a bool that specifies whether the user identified himself as an advanced
    # user or not.  You should effect your configuration by manipulating the
    # registry as appropriate.
    from supybot.questions import expect, anything, something, yn
    conf.registerPlugin('Runsbot', True)


Runsbot = conf.registerPlugin('Runsbot')
# This is where your configuration variables (if any) should go.  For example:
conf.registerGlobalValue(Runsbot, 'checkInterval', registry.NonNegativeInteger(5, """Positive Integer in seconds to check."""))
conf.registerGlobalValue(Runsbot, 'delayInterval', registry.NonNegativeInteger(30, """Positive Integer in seconds for delay."""))
conf.registerGlobalValue(Runsbot, 'dateFlip', registry.NonNegativeInteger(400, """Positive Integer which represents time 0400 means 4am"""))
conf.registerGlobalValue(Runsbot, 'isFirst', registry.Boolean(True, """Used to force outputs on reload, debug tool"""))
conf.registerGlobalValue(Runsbot, 'isLoaded', registry.Boolean(False, """Announce Basesloaded"""))
conf.registerGlobalValue(Runsbot, 'isDebug', registry.Boolean(False, """Debug"""))
conf.registerGlobalValue(Runsbot, 'doJSON', registry.String('/home/livescores/public_html/debug.json', _("""File location for debug JSON""")))


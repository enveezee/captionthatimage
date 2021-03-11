###
# Copyright (c) 2021, nvz <enveezee@gmail.com>
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
import re
import urllib.request

import supybot.callbacks
import supybot.ircmsgs as ircmsgs
import supybot.schedule as schedule
import supybot.utils as utils

try:
    from supybot.i18n import PluginInternationalization
    _ = PluginInternationalization('SpiffyWeb')
except ImportError:
    _ = lambda x: x


class CTI(supybot.callbacks.Plugin):
    """Simplified extrapolation of the supybot plugin interface."""
    threaded = True

    def __init__(self, irc):
        self.__parent = super(CTI, self)
        self.__parent.__init__(irc)

        self.gamesInProgress = {}
        self.voteticks = 12


    def _dm(self, irc, cmd):
        if irc.isChannel(channel):
            irc.reply(f'Please do not {cmd} in channel, /msg your {cmd} to me.')
            return False
        return True


    def _image(self, url):
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0')
        try:
            resp = urllib.request.urlopen(req)
        except:
            return False
        if not resp.info().get_content_type().split('/')[0] == 'image':
            return False
        return True


    def _startGame(self, channel, irc, url):
        if channel in self.gamesInProgress:
            irc.reply('A game is already in progress.')
            return
        else:
            if not _image(url):
                irc.reply('Please give a valid direct image link to start a game.')
            # Check for a stale timer.
            try:
                schedule.removeEvent(f'CTImer{channel}')
            except KeyError:
                pass
            # Add a new game tick timer callback every 15 seconds
            schedule.addPeriodicEvent(tick, 15, f'CTImer{channel}')


            def timerEvent():
                self._tick(channel, irc)

    def _tick(self, channel, irc):
        if not 'ticks' in self.gamesInProgress[channel]:
            self.gamesInProgress[channel]['ticks'] = 0
        ticks = self.gamesInProgress[channel]['ticks'] + 1
        if ticks == self.voteTicks:
            
        self.gamesInProgress[channel]['ticks'] = ticks


    def cti(self, irc, msg, args, query):
        """Play CTI for a given Image URL"""
        channel, message = msg.args[0:2]

        urlRe = utils.web._httpUrlRe
        url = re.findall(url_re, message)

        if url:
            _startGame(channel, irc, url[0])
        else:
            irc.reply('Please give a url to an image to start game.')
            return


    cti = wrap(t, ["text"])


    def caption(self, irc, msg, args, query):
        channel, message = msg.args[0:2]
        if not self._dm(irc, 'caption'):
            return


    caption = wrap(t, ["text"])


    def votecap(self, irc, msg, arge, query):
        channel, message = msg.args[0:2]
        if not self._dm('vote'):
            return


    votecap = wrap(t, ["text"])


Class = CTI

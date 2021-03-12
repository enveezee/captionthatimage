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
    _ = PluginInternationalization('CTI')
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


    def _endGame(self, channel, irc):
        schedule.removeEvent(f'CTImer{channel}')
        nicks = {}
        for vote in self.gamesInProgress[channel]['votes']:
            nick = self.nicks[vote - 1]
            if nick in nicks:
                nicks[nick] = nicks[nick] + 1
            else:
                nicks[nick] = 1
        winner = dict(sorted(nicks.items(), key=lambda item: item[1]))[0]
        # FIXME: need to check for ties here.
        irc.reply(f'The winner is {winner}.')
        del self.gamesInProgress[channel]
        

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


    def _openVoting(self, channel, irc)
        self.gamesInProgress[channel]['vote'] = True
        self.gamesInProgress[channel]['votes'] = []
        capts = self.gamesInProgress[channel]['captions']
        captions = dict(sorted(capts.items(), key=lambda item: item[1]))
        capts = list(captions.values())
        self.nicks = list(captions.keys())
        for nick in captions:
            ircmsgs.privmsg(nick, 'Cast your vote with: vote {channel} <num>')
            for capt in capts:
                idx = capts.index(capt) + 1
                ircmsgs.privmsg(nick, f'{idx}: {capt}')


    def _startGame(self, channel, irc, url):
        if channel in self.gamesInProgress:
            irc.reply('A game is already in progress.')
            return
        else:
            if not _image(url):
                irc.reply('Please give a valid direct image link to start a game.')
                return
            else:
                irc.reply(f'Capture That Image, /msg {irc.nick} caption {channel} <your caption>')
            # Check for a stale timer.
            try:
                schedule.removeEvent(f'CTImer{channel}')
            except KeyError:
                pass
            # Add a new game tick timer callback every 15 seconds
            schedule.addPeriodicEvent(tick, 15, f'CTImer{channel}')
            min, sec = divmod(self.ticks * 15, 60)
            msg = '.'
            if sec > 0:
                msg = f' and {sec} seconds.'
            irc.reply(f'Voting opens in {min} minutes{msg}')


            def timerEvent():
                self._tick(channel, irc)


    def _tick(self, channel, irc):
        if not 'ticks' in self.gamesInProgress[channel]:
            self.gamesInProgress[channel]['ticks'] = 0
        ticks = self.gamesInProgress[channel]['ticks'] + 1
        if ticks == self.voteTicks:
            if len(self.gamesInProgress[channel]['captions']) < 3:
                irc.reply('Too few captions entered, ending the game.')
            else:
                irc.reply('Voting open, cast your votes.')
                _openVoting(channel, irc)
            return
        elif ticks > self.voteTicks:
            captions = len(self.gamesInProgress[channel]['captions'])
            votes = len(self.gamesInProgress[channel]['votes'])
            if captions == votes:
                irc.reply('Voting closed, all players have voted.')
                _endGame(channel, irc)
            else:
                irc.reply(
                    f'{votes} of {captions} players have voted, '
                    'if you have not voted yet please vote now.'
                )
        else:
            rem = (voteTicks - ticks) * 15
            if sec in ['60', '30']
            irc.reply(f'{secondsRemain} seconds until voting, enter your captions.')
        self.gamesInProgress[channel]['ticks'] = ticks


    def _vote(self, channel, nick, vote):
        if vote > 0 and vote < len(self.gamesInProgress[channel]['captions']) + 1:
            if self.nicks[vote] == nick:
                return 'You cannot vote for your own caption!'
            else:
                self.gamesInProgress[channel]['votes'][nick] = vote
                return f'Vote cast for {vote}.'
        return 'Invalid caption number.'


    def cti(self, irc, msg, args, query):
        """Play CTI for a given Image URL"""
        channel, message = msg.args[0:2]

        urlRe = utils.web._httpUrlRe
        url = re.findall(url_re, message)

        if url:
            _startGame(channel, irc, url[0])
            self.gamesInProgress[channel]['captions'] = {}
            self.gamesInProgress[channel]['votes'] = {}
            return
        else:
            irc.reply('Please give a url to an image to start game.')
            return


    cti = wrap(cti, ['text'])


    def caption(self, irc, msg, args, query):
        channel, message = args[0:2]
        if not self._dm(irc, 'caption'):
            return
        if channel in self.gamesInProgress:
            self.gamesInProgress[channel]['captions'][msg.nick] = message
            irc.reply(f'Your caption is set to: {message}, you may change until voting opens.')
        else:
            irc.reply('There is no game in progress in that channel.')


    caption = wrap(caption, ['validChannel','text'])


    def votecap(self, irc, msg, args, query):
        channel, message = args[0:2]
        if not self._dm('vote'):
            return
        if channel in self.gamesInProgress:
            if self.gamesInProgress[channel]['voting']:
                if msg.nick in self.gamesInProgress[channel]['captions']:
                    result = self._vote(channel, msg.nick, message):
                    irc.reply(result)
                else:
                    irc.reply('You did not submit a caption, you cannot vote.')
            else:
                irc.reply('Voting has not started yet.')
        else:
            irc.reply('I have no game in progress in that channel')


    votecap = wrap(votecap, ['validChannel','int'])


Class = CTI

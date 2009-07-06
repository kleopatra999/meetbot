# Richard Darst, June 2009

import os
import time

import writers
#from writers import html, rst
import itertools

def inbase(i, chars='abcdefghijklmnopqrstuvwxyz', place=0):
    """Converts an integer into a postfix in base 26 using ascii chars.

    This is used to make a unique postfix for ReStructured Text URL
    references, which must be unique.  (Yes, this is over-engineering,
    but keeps it short and nicely arranged, and I want practice
    writing recursive functions.)
    """
    div, mod = divmod(i, len(chars)**(place+1))
    if div == 0:
        return chars[mod]
    else:
        return inbase2(div, chars=chars, place=place+1)+chars[mod]



#
# These are objects which we can add to the meeting minutes.  Mainly
# they exist to aid in HTML-formatting.
#
class _BaseItem(object):
    itemtype = None
    starthtml = ''
    endhtml = ''
    startrst = ''
    endrst = ''
    def get_replacements(self):
        replacements = { }
        for name in dir(self):
            if name[0] == "_": continue
            replacements[name] = getattr(self, name)
        return replacements
    def makeRSTref(self, M):
        rstref = rstref_orig = "%s-%s"%(self.nick, self.time)
        count = 0
        while rstref in M.rst_refs:
            rstref = rstref_orig + inbase(count)
            count += 1
        M.rst_urls.append(".. _%s: %s"%(rstref, self.link+"#"+self.anchor))
        M.rst_refs[rstref] = True
        return rstref
    @property
    def anchor(self):
        return 'l-'+str(self.linenum)

class Topic(_BaseItem):
    itemtype = 'TOPIC'
    html_template = """<tr><td><a href='%(link)s#%(anchor)s'>%(time)s</a></td>
        <th colspan=3>%(starthtml)sTopic: %(topic)s%(endhtml)s</th>
        </tr>"""
    rst_template = """%(startrst)s%(topic)s%(endrst)s  (%(rstref)s_)"""
    startrst = '**'
    endrst = '**'
    def __init__(self, nick, line, linenum, time_):
        self.nick = nick ; self.topic = line ; self.linenum = linenum
        self.time = time.strftime("%H:%M:%S", time_)
    def html(self, M):
        repl = self.get_replacements()
        repl['nick'] = writers.html(self.nick)
        repl['topic'] = writers.html(self.topic)
        repl['link'] = M.config.basename+'.log.html'
        return self.html_template%repl
    def rst(self, M):
        self.link = M.config.basename+'.log.html'
        self.rstref = self.makeRSTref(M)
        repl = self.get_replacements()
        if repl['topic']=='': repl['topic']=' '
        return self.rst_template%repl

class GenericItem(_BaseItem):
    itemtype = ''
    html_template = """<tr><td><a href='%(link)s#%(anchor)s'>%(time)s</a></td>
        <td>%(itemtype)s</td><td>%(nick)s</td><td>%(starthtml)s%(line)s%(endhtml)s</td>
        </tr>"""
    rst_template = """*%(itemtype)s*: %(startrst)s%(line)s%(endrst)s  (%(rstref)s_)"""
    def __init__(self, nick, line, linenum, time_):
        self.nick = nick ; self.line = line ; self.linenum = linenum
        self.time = time.strftime("%H:%M:%S", time_)
    def html(self, M):
        repl = self.get_replacements()
        repl['nick'] = writers.html(self.nick)
        repl['line'] = writers.html(self.line)
        repl['link'] = M.config.basename+'.log.html'
        return self.html_template%repl
    def rst(self, M):
        self.link = M.config.basename+'.log.html'
        self.rstref = self.makeRSTref(M)
        return self.rst_template%self.get_replacements()


class Info(GenericItem):
    itemtype = 'INFO'
class Idea(GenericItem):
    itemtype = 'IDEA'
class Agreed(GenericItem):
    itemtype = 'AGREED'
class Action(GenericItem):
    itemtype = 'ACTION'
class Halp(GenericItem):
    itemtype = 'HALP'
class Accepted(GenericItem):
    itemtype = 'ACCEPTED'
    starthtml = '<font color="green">'
    endhtml = '</font>'
class Rejected(GenericItem):
    itemtype = 'REJECTED'
    starthtml = '<font color="red">'
    endhtml = '</font>'
class Link(_BaseItem):
    itemtype = 'LINK'
    html_template = """<tr><td><a href='%(link)s#%(anchor)s'>%(time)s</a></td>
        <td>%(itemtype)s</td><td>%(nick)s</td><td>%(starthtml)s<a href="%(url)s">%(url_readable)s</a> %(line)s%(endhtml)s</td>
        </tr>"""
    rst_template = """*%(itemtype)s*: %(startrst)s%(url)s %(line)s%(endrst)s  (%(rstref)s_)"""
    def __init__(self, nick, line, linenum, time_):
        self.nick = nick ; self.linenum = linenum
        self.time = time.strftime("%H:%M:%S", time_)
        self.url, self.line = (line+' ').split(' ', 1)
        # URL-sanitization
        self.url_readable = self.url # readable line version
        self.url = self.url.replace('"', "%22")
        # readable line satitization:
        self.line = writers.html(self.line.strip())
    def html(self, M):
        repl = self.get_replacements()
        repl['nick'] = writers.html(self.nick)
        repl['url'] = writers.html(self.url)
        repl['url_readable'] = writers.html(self.url)
        repl['line'] = writers.html(self.line)
        repl['link'] = M.config.basename+'.log.html'
        self.link = M.config.basename+'.log.html'
        return self.html_template%repl
    def rst(self, M):
        self.link = M.config.basename+'.log.html'
        self.rstref = self.makeRSTref(M)
        return self.rst_template%self.get_replacements()

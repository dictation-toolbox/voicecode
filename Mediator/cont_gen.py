##############################################################################
# VoiceCode, a programming-by-voice environment
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
# (C)2000, National Research Council of Canada
#
##############################################################################

"""Context objects which are not tied to a specific language"""

from Context import Context
import actions_gen 
import debug
import AppStateEmacs
import re

class ContLanguage(Context):
    """Context that applies only if a particular programming language is the
    active one.
    
    **INSTANCE ATTRIBUTES**
    
    *ANY language=None* -- Name of the programming language for this context. If *None*, then this context always applies.

    CLASS ATTRIBUTES**
    
    *none* -- 
    """
    
    def __init__(self, language=None, **args_super):
        self.deep_construct(ContLanguage, \
                            {'language': language}, \
                            args_super, \
                            {})

    def scope(self):
        """returns a string indicating the scope of this context.
        Commands with more specific scopes are checked first.

        See Context for details of the recognized scopes

        **INPUTS**

        *none*

        **OUTPUTS**

        *STR* -- the string identifying the scope
        """
        return "buffer"

    def equivalence_key(self):
        """returns a key used to separate Context instances into
        equivalence classes.  Two contexts which are equivalent (i.e.
        share the same set of circumstances under which they apply)
        should have identical keys.  Two contexts which are not
        equivalent should have distinct keys.

        For example, two instances of ContPy should both return the same
        key.

        See Context for more details.

        **INPUTS**

        *none*

        **OUTPUTS**

        *STR* -- the key
        """
        return "Language: %s" % self.language

    def _applies(self, app, preceding_symbol = 0):
        buff = app.curr_buffer()
        return (self.language == None or (buff != None and  buff.language_name() == self.language))
        

class ContC(ContLanguage):
    """This context applies if current source buffer is in C.

    It is essentially a shortcut for ContLanguage(language='C')
    """
    
    def __init__(self, **args_super):
        self.deep_construct(ContC, {}, args_super, enforce_value={'language': 'C'})


class ContPerl(ContLanguage):
    """This context applies if current source buffer is in Perl.

    It is essentially a shortcut for ContLanguage(language='perl')
    """
    
    def __init__(self, **args_super):
        self.deep_construct(ContPerl, {}, args_super, enforce_value={'language': 'perl'})

class ContPy(ContLanguage):
    """This context applies if current source buffer is in Python.

    It is essentially a shortcut for ContLanguage(language='python')
    """
    
    def __init__(self, **args_super):
        self.deep_construct(ContPy, {}, args_super, enforce_value={'language': 'python'})


class ContAny(Context):
    """This context always applies, UNLESS translation is off."""

    def __init__(self, **attrs):
        self.deep_construct(ContAny, {}, attrs)
        
    def _applies(self, app, preceding_symbol = 0):
        return not app.translation_is_off

    def scope(self):
        """returns a string indicating the scope of this context.
        Commands with more specific scopes are checked first.

        See Context for details of the recognized scopes

        **INPUTS**

        *none*

        **OUTPUTS**

        *STR* -- the string identifying the scope
        """
        return "global"

    def equivalence_key(self):
        """returns a key used to separate Context instances into
        equivalence classes.  Two contexts which are equivalent (i.e.
        share the same set of circumstances under which they apply)
        should have identical keys.  Two contexts which are not
        equivalent should have distinct keys.

        For example, two instances of ContPy should both return the same
        key.

        See Context for more details.

        **INPUTS**

        *none*

        **OUTPUTS**

        *STR* -- the key
        """
        return "Any"


class ContLastActionWas(Context):
    """This context applies if the last action application's command history
    was of a certain type"""

    def __init__(self, types, connector='and', **attrs):
        """**INPUTS**

        *CLASS* types -- A list of class objects (not instance). The
        context applies if the last action is an instance of all them
        (or *one of them* if *self.connector == 'or'*).

        *STR* connector='and' -- If *'and'*, then context applies if
         last action is an instance of all the classes in *types*. If
         *'or'*, then context applies if last action is an instance of
         any of the classes in *types*.
        """
        
        self.deep_construct(ContLastActionWas, {'types': types, 'connector': connector},
                            attrs)
        if self.connector != 'and':
            self.connector = 'or'
        
    def _applies(self, app, preceding_symbol = 0):
        if preceding_symbol:
            last_cont = None
            last_action = actions_gen.ActionInsert('%dummy%')
        else:
            entry = app.get_history(1)
            debug.trace('ContLastActionWas.applies', 'entry=%s' % repr(entry))
            if entry:
                (last_cont, last_action) = entry
            else:
                return 0
        if self.connector == 'and':
            answer = 1
            for a_class in self.types:
                if not isinstance(last_action, a_class):
                    answer = 0
                    break
        else:
            answer = 0
            for a_class in self.types:
                if isinstance(last_action, a_class):
                    answer = 1
                    break
        debug.trace('ContLastActionWas.applies', 'last_cont=%s, last_action=%s, self.types=%s, answer=%s' % (last_cont, last_action, self.types, answer))
        return answer

    def scope(self):
        """returns a string indicating the scope of this context.
        Commands with more specific scopes are checked first.

        See Context for details of the recognized scopes

        **INPUTS**

        *none*

        **OUTPUTS**

        *STR* -- the string identifying the scope
        """
        return "last command"

    def equivalence_key(self):
        """returns a key used to separate Context instances into
        equivalence classes.  Two contexts which are equivalent (i.e.
        share the same set of circumstances under which they apply)
        should have identical keys.  Two contexts which are not
        equivalent should have distinct keys.

        For example, two instances of ContPy should both return the same
        key.

        See Context for more details.

        **INPUTS**

        *none*

        **OUTPUTS**

        *STR* -- the key
        """
        type_names = []
        for t in self.types:
            type_names.append(str(t))
        type_names.sort()
        s = "LastActionWas: %s %s" % (self.connector, type_names)
        return s


class ContBlankLine(Context):
    """This context applies if the cursor is on a blank line."""

    def __init__(self, language=None, **attrs):        
        self.deep_construct(ContBlankLine, {'language': language},
                            attrs)
       
    def _applies(self, app, preceding_symbol = 0):
       if preceding_symbol:
           return 0
       answer = 0
       lang_cont = ContLanguage(language=self.language)
       
       if lang_cont.applies(app):
          buff = app.curr_buffer()
          start = buff.beginning_of_line()
          end = buff.end_of_line()
          line = buff.get_text(start, end)
          if re.match('\s*$', line):
             answer = 1
 
       return answer        

    def scope(self):
        """returns a string indicating the scope of this context.
        Commands with more specific scopes are checked first.

        See Context for details of the recognized scopes

        **INPUTS**

        *none*

        **OUTPUTS**

        *STR* -- the string identifying the scope
        """
        return "immediate"

    def equivalence_key(self):
        """returns a key used to separate Context instances into
        equivalence classes.  Two contexts which are equivalent (i.e.
        share the same set of circumstances under which they apply)
        should have identical keys.  Two contexts which are not
        equivalent should have distinct keys.

        For example, two instances of ContPy should both return the same
        key.

        See Context for more details.

        **INPUTS**

        *none*

        **OUTPUTS**

        *STR* -- the key
        """
        return "BlankLine(%s)" % self.language


class ContTextIsSelected(Context):
    """This context applies if there is some text selected."""

    def __init__(self, **attrs):        
        self.deep_construct(ContTextIsSelected, {},
                            attrs)
       
    def _applies(self, app, preceding_symbol = 0):
        (start, end) = app.get_selection()
        if start != end:
           return True
        else:
           return False

    def scope(self):
        """returns a string indicating the scope of this context.
        Commands with more specific scopes are checked first.

        See Context for details of the recognized scopes

        **INPUTS**

        *none*

        **OUTPUTS**

        *STR* -- the string identifying the scope
        """
        return "immediate"

    def equivalence_key(self):
        """returns a key used to separate Context instances into
        equivalence classes.  Two contexts which are equivalent (i.e.
        share the same set of circumstances under which they apply)
        should have identical keys.  Two contexts which are not
        equivalent should have distinct keys.

        For example, two instances of ContPy should both return the same
        key.

        See Context for more details.

        **INPUTS**

        *none*

        **OUTPUTS**

        *STR* -- the key
        """
        return "ContTextIsSelected"



class ContAnyEvenOff(Context):
    """This context always applies, EVEN IF translation is off."""

    def __init__(self, **attrs):
        self.deep_construct(ContAnyEvenOff, {}, attrs)
        
    def _applies(self, app, preceding_symbol = 0):
        return 1

    def scope(self):
        """returns a string indicating the scope of this context.
        Commands with more specific scopes are checked first.

        See Context for details of the recognized scopes

        **INPUTS**

        *none*

        **OUTPUTS**

        *STR* -- the string identifying the scope
        """
        return "any"

    def equivalence_key(self):
        """returns a key used to separate Context instances into
        equivalence classes.  Two contexts which are equivalent (i.e.
        share the same set of circumstances under which they apply)
        should have identical keys.  Two contexts which are not
        equivalent should have distinct keys.

        For example, two instances of ContPy should both return the same
        key.

        See Context for more details.

        **INPUTS**

        *none*

        **OUTPUTS**

        *STR* -- the key
        """
        return "AnyEvenOff"



class ContTranslationOff(Context):
    """This context only applies when translation of commands is 'off'
    
    **INSTANCE ATTRIBUTES**
    
    *none*-- 
    
    CLASS ATTRIBUTES**
    
    *none* -- 
    """
    
    def __init__(self, **args_super):
        self.deep_construct(ContTranslationOff, \
                            {}, \
                            args_super, \
                            {})
    def _applies(self, app, preceding_symbol = 0):
        return app.translation_is_off

    def scope(self):
        """returns a string indicating the scope of this context.
        Commands with more specific scopes are checked first.

        See Context for details of the recognized scopes

        **INPUTS**

        *none*

        **OUTPUTS**

        *STR* -- the string identifying the scope
        """
        return "global"

    def equivalence_key(self):
        """returns a key used to separate Context instances into
        equivalence classes.  Two contexts which are equivalent (i.e.
        share the same set of circumstances under which they apply)
        should have identical keys.  Two contexts which are not
        equivalent should have distinct keys.

        For example, two instances of ContPy should both return the same
        key.

        See Context for more details.

        **INPUTS**

        *none*

        **OUTPUTS**

        *STR* -- the key
        """
        return "TranslationOff"


class ContNotAfterNewSymb(Context):
    """This context applies if the current buffer is in a particular language
    AND the words being interpreted weren't preceded by words which were
    interpreted as being part of a new symbol."""

    def __init__(self, language, **args_super):
        self.deep_construct(ContNotAfterNewSymb, \
                            {'language': language}, \
                            args_super, \
                            {})
    
    def _applies(self, app, preceding_symbol = 0):
        tmp_cont_lang = ContLanguage(self.language)
        return not preceding_symbol and tmp_cont_lang._applies(app, preceding_symbol)
    
    def scope(self):
        return "last command"
        
    def equivalence_key(self):
        return "NotAfterSymb_in_%s" % self.language
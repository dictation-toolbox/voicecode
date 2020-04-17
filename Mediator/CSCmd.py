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
# (C) 2000, National Research Council of Canada
#
##############################################################################

import sys
import copy

from Object import Object
from debug import trace, config_warning
import Context

class DuplicateContextKeys(RuntimeError):
    def __init__(self, msg):
        RuntimeError.__init__(self, msg)
        self.msg = msg

class CSCmd(Object):
    """Class for Context Sensitive Commands (CSCs).

    A CSC is a phrase which, when uttered into an application, may
    fire a particular action.
    
    A CSC may fire different actions depending on the context of the
    application where it was typed.
        
    **INSTANCE ATTRIBUTES**

    **NOTE:** when CSCs are added to CmdInterp, it stores stores the
    underlying CSCmdDict, rather than the CSC.  Therefore, any
    additional data required by CmdInterp once it concludes that a
    particular CSC applies must be stored in CSCmdDict.
        
    *STR spoken_forms=[]* -- list of alternatives ways that this
     command can be spoken out. 

    *CSCmdDict meanings* -- object which manages the meanings of the
    command

    CLASS ATTRIBUTES**
        
    *none* --

    .. [Context] file:///./Context.Context.html
    .. [Action] file:///./Action.Action.html"""
        
    def __init__(self, spoken_forms=[], meanings={}, docstring=None, 
                 generate_discrete_cmd = 0, **attrs):
        """
        **INPUTS**

        *[STR] spoken_forms* -- list of spoken forms for the command

        *meanings=*{* [Context] *: * [Action] *}* -- Dictionary of
        possible contextual meanings for this command. Key is a context
        and value is an action object to be fired if that context applies.
        
        *BOOL generate_discrete_cmd* -- If true, then generate a discrete command
        for the CSC. Use this for commands like "copy that" whose spoken form
        is already a NatSpeak command, but whose behaviour must be different
        in NatSpeak.

        *STR docstring* -- string documentating the command
        """
        self.deep_construct(CSCmd,
                            {'spoken_forms': spoken_forms,
                             'meanings': CSCmdDict(meanings, generate_discrete_cmd),
                             'generate_discrete_cmd': generate_discrete_cmd
                            },
                            attrs)

    def get_meanings(self):
        """returns a copy of the internal CSCmdDict object.
        """
        return self.meanings.clone()

    def applies(self, app, preceding_symbol = 0):
        """test whether any of its contexts applies, and returns

        **INPUTS**

        [AppState] app is the application into which the command was spoken.

        BOOL *preceding_symbol* indicates if a symbol would be inserted
        at the current cursor position before the action corresponding
        to this context was executed.  

        **OUTPUTS**

        *meaning* -- meaning if a Context applies, return the (context,
        action) pair, otherwise None
        """
        return self.meanings.applies(app, preceding_symbol)
        
    def doc(self):
        """Returns the documentation for that CSC.
        
        **INPUTS**
        
        *none* -- 
        

        **OUTPUTS**
        
        *none* -- 
        """
        
        return self.docstring

    def replace_spoken(self, spoken_forms):
        """replace the spoken forms of the command 

        **INPUTS**

        *[STR] spoken_forms* -- the new spoken forms

        **OUTPUTS**

        *none*
        """
        self.spoken_forms = spoken_forms[:]

    def add_spoken(self, name, spoken_forms):
        """add the given spoken forms to the command 

        **INPUTS**

        *[STR] spoken_forms* -- the spoken forms to add

        **OUTPUTS**

        *none*
        """
        for spoken in spoken_forms:
            self.spoken_forms.append(spoken)

    def remove_spoken(self, name, spoken_forms):
        """remove the given spoken forms of the command 

        **INPUTS**

        *[STR] spoken_forms* -- the spoken forms to remove

        **OUTPUTS**

        *none*
        """
        new_spoken = []
        for spoken in self.spoken_forms:
            if spoken not in spoken_forms:
                new_spoken.append(spoken)
        self.spoken_forms = new_spoken

class CSCmdDict(Object):
    """underlying class used to store CSCmd context and action data 
    internally for CSCmd and also once the commands have been indexed 
    within CmdInterp.
    
    **INSTANCE ATTRIBUTES**

    *{STR: [STR]} by_scope* -- map from scope names to keys of 
    (context, action) pairs with that scope.
        
    *contexts=*{* STR: Context *}* -- Dictionary of contexts in which
    this command applies.  The key is a string returned by
    Context.equivalence_key (see Context for details).

    *actions=*{* STR: Action *}* -- Dictionary of actions to take in
    the corresponding context.  The key is a string returned by
    Context.equivalence_key (see Context for details).
    
    *BOOL generate_discrete_cmd=0* -- If true, then a command should be 
    added to the discrete commands grammar for CSCs.

    CLASS ATTRIBUTES**
        
    *none* --

    .. [Context] file:///./Context.Context.html
    .. [Action] file:///./Action.Action.html"""
        
    def __init__(self, meanings={}, generate_discrete_cmd=0, **attrs):
        """
        **INPUTS**

        *BOOL generate_discrete_cmd* -- If true, then a command should be 
    added to the discrete commands grammar for CSCs.

        *meanings=*{* [Context] *: * [Action] *}* -- Dictionary of
        possible contextual meanings for this command. Key is a context
        and value is an action object to be fired if that context applies.
        """           
        self.deep_construct(CSCmdDict,
                            {'generate_discrete_cmd': generate_discrete_cmd,
                             'by_scope': {},
                             'contexts': {}, 
                             'actions': {}
                            },
                            attrs)
        self._add_meanings(meanings)        

    def clone(self):
        """returns a mixed deep-shallow copy of the object.  The
        object's dictionaries are not shared, but the Context and Action
        objects in those dictionaries are.

        **INPUTS**

        *none*

        **OUTPUTS**

        *CSCmdDict* -- the copy
        """
        meanings = self._extract_meanings()
        generate_discrete_cmd = self.generate_discrete_cmd
        return CSCmdDict(meanings, generate_discrete_cmd)

    def _extract_meanings(self):
        """private method which converts the actions and contexts from a
        CSCmdDict back into the meanings argument expected by the
        constructor and by _add_meanings

        **INPUTS**

        *none*

        **OUTPUTS**

        *meanings=*{* [Context] *: * [Action] *}* -- Dictionary of
        possible contextual meanings for this command. Key is a context
        and value is an action object to be fired if that context applies.
        """
        meanings = {}
        for key, context in self.contexts.items():
            meanings[context] = self.actions[key]
        return meanings
        
    def _add_meanings(self, meanings):
        """private method which adds new meanings to the dictionary

        **INPUTS**

        *meanings=*{* [Context] *: * [Action] *}* -- Dictionary of
        possible contextual meanings for this command. Key is a context
        and value is an action object to be fired if that context applies.

        **OUTPUTS**

        *none*
        """
        duplicates = []
        for context, action in meanings.items():
            key = context.equivalence_key()
            if not key in self.contexts.keys():
                scope = context.scope()
                if not Context.valid_scope(scope):
                    msg = "Scope %s of context %s\n" % (scope, context)
                    msg = msg + "\nis unknown\n"
                    raise RuntimeError(msg)
                try:
                    self.by_scope[scope].append(key)
                except KeyError:
                    self.by_scope[scope] = [key]
                self.contexts[key] = context
                self.actions[key] = action
            else:
                duplicates.append((self.contexts[key], context))
        if duplicates:
            msg = "Duplicate contexts\n"
            for original, duplicate in duplicates:
                msg = msg + "Contexts %s and %s" % (self.contexts[key], context)
                msg = msg + \
                    "\nhave the same key %s\n" % context.equivalence_key()
            raise DuplicateContextKeys(msg)

    def merge(self, cmd_dict):
        """merges another CSCmdDict into this one

        **INPUTS**

        *CSCmdDict cmd_dict* -- the other command dictionary

        **OUTPUTS**

        *none*
        """

        self._add_meanings(cmd_dict._extract_meanings())

    def applies(self, app, preceding_symbol = 0):
        """test whether any of its contexts applies, and returns
        the corresponding meaning (or meanings)

        **INPUTS**

        [AppState] app is the application into which the command was spoken.

        BOOL *preceding_symbol* indicates if a symbol would be inserted
        at the current cursor position before the action corresponding
        to this context was executed.  

        **OUTPUTS**

        *[(Context, Action)]* -- 
        A list of meanings whose contexts apply, or None if no contexts
        apply.  Note: if the list has more than one element, CmdInterp 
        should use the first one, but should print a warning about the 
        ambiguous contexts/meanings for the spoken form
        """
        
        #
        # Try each of the contextual meanings in turn until find one that
        # applies
        #
#        print '-- CSCmd.interpret: self.meanings=%s' % self.meanings
        scopes = Context.scope_order()
        for scope in scopes:
            try:
                keys = self.by_scope[scope]
                applicable_keys = []
                meanings = []
                for key in keys:
                    if self.contexts[key].applies(app, preceding_symbol):
                        applicable_keys.append(key)
                if applicable_keys:
                    return map(lambda k: \
                                  (self.contexts[k], self.actions[k]),
                               applicable_keys)
            except KeyError:
                pass
        return None

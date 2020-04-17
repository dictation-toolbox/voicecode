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

from Object import Object
import sys

class Context(Object):
    """Base class for all application contexts.

    This virtual class is the base class for all context objects.
    
    **INSTANCE ATTRIBUTES**
    
    *STR doc_string=None* -- A string describing the purpose of the
     context. Used to generate "what can I say" help.
    
    *[STR] doc_topics=[]* -- List of topics where this context is
     relevant. Used to generate "what can I say" help.

    CLASS ATTRIBUTES**
    
    *none* -- 
    """
    
    def __init__(self, doc_string=None, doc_topics=[], **attrs):
        self.deep_construct(Context,
                            {'doc_string': doc_string,\
                             'doc_topics': doc_topics},
                            attrs)


    def scope(self):
        """returns a string indicating the scope of this context.
        Commands with more specific scopes are checked first.

        Currently, the recognized return values for scope, in order of
        decreasing specificity, are: 

        "last command": depends on the last command executed
        "immediate": depends on the current line or statement in the
            current buffer 
        "block": depends on a wider range of code around the cursor (for
            example, whether the cursor is inside a for loop)
        "project": depends on whether the current file is part of a
            project
        "buffer": depends only on characteristics of the entire buffer
            (for example, the language or file name)
        "global": depends only on the global state of the mediator
        "any": independent of context

        **INPUTS**

        *none*

        **OUTPUTS**

        *STR* -- the string identifying the scope
        """
        debug.virtual('Context.scope')

    def equivalence_key(self):
        """returns a key used to separate Context instances into
        equivalence classes.  Two contexts which are equivalent (i.e.
        share the same set of circumstances under which they apply)
        should have identical keys.  Two contexts which are not
        equivalent should have distinct keys.

        For example, two instances of ContPy should both return the same
        key, but an instance of ContPy and an instance of ContC should
        not.

        Generally, the equivalence key should be constructed from the
        name of the Context subclass (omitting any Context or Cont
        prefix), followed by ": " and any data required to distinguish 
        inequivalent contexts.  Contexts with multiple pieces of data
        should sort that data by keyname.  If there is no data, the ": " 
        should be omitted.  Subclasses which differ from their parent class 
        only in that they supply or enforce a value for an argument of the
        parent constructor should return the same equivalence key as
        their parent class would if given that value explicitly.  (So
        ContLanguage(language = 'python') and ContPy() should both
        return 'Language: python' (and not 'Py').

        **INPUTS**

        *none*

        **OUTPUTS**

        *STR* -- the key
        """
        debug.virtual('Context.equivalence_key')

    def applies(self, app, preceding_symbol = 0):        
        """Returns *true* iif the context applies given current state
        of an application.

        Do not override this method.  Instead override the private
        method _applies.

        [AppState] *app* is the application in question.

        BOOL *preceding_symbol* indicates if a symbol would be inserted
        at the current cursor position before the action corresponding
        to this context was executed.  
        
        .. [AppState] file:///./AppState.AppState.html"""
        buffer = app.curr_buffer_name()
        position, selection = app.get_pos_selection()
        cursor_at = (position == selection[1])
        answer = self._applies(app, preceding_symbol = preceding_symbol)
        if buffer != app.curr_buffer_name():
            raise RuntimeError("context %s switched buffers" % self)
        newpos, newsel = app.get_pos_selection()
        if position != newpos:
            msg = "Warning: context %s" % self + \
                  "\ndidn't restore the cursor position\n"
            msg = msg + 'old position, selection were %d, (%d, %d)\n' \
                % ((position,) + selection)
            msg = msg + 'new position, selection were %d, (%d, %d)\n' \
                % ((newpos,) + newsel)
            sys.stderr.write(msg)
        if selection != newsel:
            msg = "Warning: context %s" % self + \
                  "\ndidn't restore the selection\n"
            msg = msg + 'old position, selection were %d, (%d, %d)\n' \
                % ((position,) + selection)
            msg = msg + 'new position, selection were %d, (%d, %d)\n' \
                % ((newpos,) + newsel)
            sys.stderr.write(msg)
        app.set_selection(selection, cursor_at)
        return answer
        
    def _applies(self, app, preceding_symbol = 0):        
        """Returns *true* iif the context applies given current state
        of an application.

        [AppState] *app* is the application in question.

        BOOL *preceding_symbol* indicates if a symbol would be inserted
        at the current cursor position before the action corresponding
        to this context was executed.  
        
        .. [AppState] file:///./AppState.AppState.html"""
        
        debug.virtual('Context._applies')

#    Currently, the recognized return values for scope, in order of
#    decreasing specificity, are: 
#
#    "last command": depends on the last command executed
#    "immediate": depends on the current line or statement in the
#        current buffer 
#    "block": depends on a wider range of code around the cursor (for
#        example, whether the cursor is inside a for loop)
#    "project": depends on whether the current file is part of a
#        project
#    "buffer": depends only on characteristics of the entire buffer
#        (for example, the language or file name)
#    "global": depends only on the global state of the mediator
#    "any": independent of context

scope_map = {"last command": 0,
             "immediate": 1,
             "block": 2,
             "project": 3,
             "buffer": 4, 
             "global": 5,
             "any": 6}

def valid_scope(scope):
    """checks whether the scope is a recognized one

    **INPUTS**

    *STR scope* -- the string identifying the scope

    **OUTPUTS**

    *BOOL* -- true if the scope is known
    """
    try:
        scope_map[scope]
        return 1
    except KeyError:
        return 0

def scope_order():
    """returns the list of scope names in order from highest priority to
    lowest

    **INPUTS**

    *none*

    **OUTPUTS**

    *[STR]* 
    """
    pairs = scope_map.items()
    pairs.sort(lambda a, b: cmp(a[1], b[1]))
    return map(lambda a: a[0], pairs)


#  Todo

#  NOTE: This todo list based on old Perl code. Some of it may still
#  be relevant.

#  =head3 ContCompound

#  Create a subclass I<ContCompound> for describing compound contexts
#      e.g my $comp = new ContCompound(cond => or(new ContCFor(), ContCForGeneral()));

#  the L<applies> method would then return a list of parsed contexts
#  which applied in the course of evaluating the condition. This list
#  would be passed to the action function (Q: how does the action method
#  know which item of the list correspond to which part of the compound
#  context? maybe the returned list should be structured in such a way
#  that we know what condition was evaluated and what elements of it
#  applied).

#  Similar idea: ContSeq which describes a sequence of contexts that must
#  be satisfied, with 

#  =head3 @$appName

#  Add attribute I<@$appName> that will store the names of applications
#  to which this context applies. If undef, (or empty?) then it means it
#  applies across all apps.

#  Should add an I<$name> attribute to L<AppState/AppState> that would
#  store the name of the app it keeps status of. Then L<applies> would
#  check that I<$name> is contained in I<@$appName>.

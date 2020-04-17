import debug
import TestCaseWithHelpers
import vc_globals
import os

mediator_used_for_testing = None

class VoiceCodeRootTest(TestCaseWithHelpers.TestCaseWithHelpers):
   """Root class for all VoiceCode PyUnit tests.

   It essentially defines some helper methods needed by most VoiceCode
   unit tests."""

   def __init__(self, name):
      TestCaseWithHelpers.TestCaseWithHelpers.__init__(self, name)
      
      self._set_automatic_buffer_printing(0)
      
      self._test_data_file_pathes = \
              {
               'large_buff_py': vc_globals.test_data + os.sep + 'large_buff.py'
              }
              
   def __del__(self):              
      self._set_automatic_buffer_printing(1)      
      
   def _set_automatic_buffer_printing(self, state=0):   
      app_mgr = self._mediator().editors
      for an_app in app_mgr.instances.values():
         an_app.print_buff_when_changed = state
      
   def _get_test_data_file_path(self, file_name):
      return self._test_data_file_pathes[file_name]
      
   def _mediator_testing_namespace(self):
      return self._mediator().test_space["testing"]
      
   def _app(self):
    instance_name = self._mediator_testing_namespace().instance_name()
    app = self._mediator().editors.app_instance(instance_name)
    return app

      
   def _commands(self):
      debug.trace('VoiceCodeRootTest._commands', 'self._mediator_testing_namespace=%s' % self._mediator_testing_namespace())
      return  self._mediator_testing_namespace().namespace()['commands'] 
      
   def _say(self, utterance):
      self._commands().say(utterance)
      
   def _open_file(self, fpath):
      self._commands().open_file(fpath)    
  
   def _init_simulator_regression(self):
      return self._mediator_testing_namespace().init_simulator_regression()
      
   def _mediator(self):
      global mediator_used_for_testing
      return mediator_used_for_testing
      
   def _goto(self, pos):
      return self._app().goto(pos)   

   def _goto_line(self, line_num, where=-1):
      return self._app().goto_line(line_num, where)   
      
   def _cur_pos(self):
      return self._app().cur_pos()
      
   def _get_text(self, start_pos, end_pos):
      return self._app().get_text(start_pos, end_pos)
      
   def _len(self):
      return self._app().len()      
      
   def _assert_cursor_looking_at(self, exp_looking_at, direction=1, 
                                 message=""):
      start_pos = self._cur_pos()
      end_pos = start_pos + len(exp_looking_at)*direction
      debug.trace('VoiceCodeRootTest._assert_cursor_looking_at', 
                  '** exp_looking_at=%s, start_pos=%s, end_pos=%s' % 
                  (exp_looking_at, start_pos, end_pos))
      actually_looking_at = self._get_text(start_pos, end_pos)
      self.assert_equals(exp_looking_at, actually_looking_at,
             message +"At postion %s, expected to be looking at string '%s' in direction %s, but was actually looking at '%s'" %
             (start_pos, exp_looking_at, direction, actually_looking_at))
             
   def _assert_cur_pos_is(self, exp_pos, mess=""):
      got_pos = self._cur_pos()
      self.assert_equals(exp_pos, got_pos,  
                   mess + "Cursor was at the wrong place")
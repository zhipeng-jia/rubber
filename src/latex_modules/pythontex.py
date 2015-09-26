# This file is part of Rubber and thus covered by the GPL
# (c) Ferdinand Schwenk, 2013
# vim: noet:ts=4
"""
pythontex support for Rubber
"""

from rubber import _, msg

import os.path
import shutil
import subprocess

import rubber.module_interface

class Module (rubber.module_interface.Module):

	def __init__ (self, document, context):
		self.doc = document

	def pre_compile (self):
		pytxcode = self.doc.basename (with_suffix=".pytxcode")
		if not os.path.exists(pytxcode):
			msg.info(_("Need compilation!"), pkg="pythontex")
			self.force_compilation()
		msg.info(_("running pythontex..."), pkg="pythontex")
		self.run_pythontex()
		self.doc.watch_file(pytxcode)
		return True

	def clean (self):
		self.doc.remove_suffixes([".pytxcode"])
		pythontex_files = 'pythontex-files-' + self.doc.basename ()
		if os.path.exists(pythontex_files):
			msg.log(_("removing tree %s") % pythontex_files)
			shutil.rmtree(pythontex_files)

	def run_pythontex(self):
		call = ['pythontex', self.doc.source (), ]
		msg.debug(_("pythontex call is '%s'") % ' '.join(call), pkg="pythontex")
		if not self.doc.env.is_in_unsafe_mode_:
			msg.error(_("the document tries to run external programs which could be dangerous.  use rubber --unsafe if the document is trusted."))
			return
		subprocess.call(call)

	def force_compilation(self):
		self.doc.compile()

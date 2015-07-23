# This file is part of Rubber and thus covered by the GPL
# (c) Emmanuel Beffara, 2004--2006
# vim: noet:ts=4
"""
Common support for makeindex and xindy external tools.
"""
import os.path

import rubber.depend
from rubber.util import _, msg

class Index (rubber.depend.Node):
	"""
	This class represents a single index.
	"""
	def __init__ (self, doc, source, target, transcript):
		"""
		Initialize the index, by specifying the source file (generated by
		LaTeX), the target file (the output of makeindex) and the transcript
		(e.g. .ilg) file.  Transcript is used by glosstex.py.
		"""
		rubber.depend.Node.__init__ (self, doc.set)
		src = os.path.basename (doc.basename (with_suffix = "." + source))
		tgt = os.path.basename (doc.basename (with_suffix = "." + target))
		doc.add_product (src)
		self.add_product (tgt)
		self.add_product (os.path.basename (doc.basename (with_suffix = "." + transcript)))
		self.add_source (src, track_contents=True)
		doc.add_source (tgt, track_contents=True)
		self.doc = doc
		self.tool = "makeindex"
		self.lang = None   # only for xindy
		self.modules = []  # only for xindy
		self.opts = []
		self.path = []
		self.style = None  # only for makeindex


	def do_language (self, lang):
		self.lang = lang

	def do_modules (self, *args):
		self.modules.extend(args)

	def do_order (self, *args):
		for opt in args:
			if opt == "standard": self.opts = []
			elif opt == "german": self.opts.append("-g")
			elif opt == "letter": self.opts.append("-l")
			else: msg.warn(
				_("unknown option '%s' for 'makeidx.order'") % opt)

	def do_path (self, path):
		self.path.append(self.doc.abspath(path))

	def do_style (self, style):
		self.style = style

	def do_tool (self, tool):
		if tool not in ("makeindex", "xindy"):
			msg.error(_("unknown indexing tool '%s'") % tool)
		self.tool = tool

	def run (self):
		if not os.path.exists (self.sources [0]):
			msg.info (_ ("%s not yet generated" % self.sources [0]))
			return True

		cmd = [self.tool, "-q",
			   self.sources [0],
			   "-o", self.products [0],
			   "-t", self.products [1]]
		if self.tool == "makeindex":
			cmd.extend (self.opts)
			if self.style:
				cmd.extend (["-s", self.style])
			path_var = "INDEXSTYLE"
		else:				   # self.tool == "texindy"
			for opt in self.opts:
				if opt == "-g":
					if self.lang != "":
						msg.warn(_("'language' overrides 'order german'"),
							pkg="index")
					else:
						self.lang = "german-din"
				else:		   # opt == "-l"
					self.modules.append("letter-ordering")
					msg.warn(_("use 'module letter-ordering' instead of 'order letter'"),
						pkg="index")
			for mod in self.modules:
				cmd.extend(["--module", mod])
			if self.lang:
				cmd.extend(["--language", self.lang])
			path_var = "XINDY_SEARCHPATH"

		if self.path != []:
			env = { path_var: ':'.join(self.path + [os.getenv(path_var, '')]) }
		else:
			env = {}
		return self.doc.env.execute(cmd, env) == 0

#!/usr/bin/python
#
# txtfmt.py
#
# an ascii formatter
#
# $Date: 2000/04/06 23:09:36 $
# $Id: txtfmt.py,v 1.5 2000/04/06 23:09:36 jpl Exp $
#
# Copyright (c) 2000 Jean-Philippe Langlois <jpl@iname.com>
# Released under the GNU General Public Licence
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#


import sys
import string
import warnings
warnings.filterwarnings(
	'ignore', 'The xmllib module is obsolete.*',
	DeprecationWarning, '.*xmllib', 9)
import xmllib
import os
try:
	from cStringIO import StringIO
except ImportError:
	from StringIO import StringIO


# Constants
#

LEFT	= 0
RIGHT	= 1
CENTER	= 2
JUSTIFY = 3

align_codes = { "left": LEFT, "right": RIGHT, "center": CENTER, 
	"justify": JUSTIFY }


# Utility functions
#

def debug( msg ):
	sys.stderr.write( msg + "\n" )

def sum( list ):
	sum = 0

	for i in list:
		sum = sum + i

	return sum


# Classes
#

class Words:
	"""
	Word data and format methods.
	"""

	def __init__( self, words ):
		if words is None:
			raise ValueError

		self.data = words

	def count( self ):
		return len( self.data )

	def skip( self, nwords ):
		self.data = self.data[nwords:]

	def trim( self, width ):
		self.data[0] = self.data[0][:width]

	def width( self, nwords = -1 ):
		if self.data == []:
			return 0

		if nwords < 0:
			nwords = len( self.data )

		length = len( self.data[0] )

		for w in self.data[1:nwords]:
			length = length + 1 + len( w )

		return length

	def fit( self, width = 79 ):
		# determine how many words can fit on the line
		count = 0

		if self.data == []:
			return 0

		length = len( self.data[0] )
		count = count + 1

		if length > width:
			return count - 1

		if length == width:
			return count

		for word in self.data[1:]:
			length = length + 1 + len( word )
			count = count + 1

			if length > width:
				return count - 1

			if length == width:
				return count

		return count

	def ljust( self, width, nwords ):
		if nwords < 1:
			return " " * width

		return string.ljust( string.join( self.data[:nwords] ), width )

	def rjust( self, width, nwords ):
		if nwords < 1:
			return " " * width

		return string.rjust( string.join( self.data[:nwords] ), width )

	def center( self, width, nwords ):
		if nwords < 1:
			return " " * width

		return string.center( string.join( self.data[:nwords] ), width )

	def justify( self, width, nwords ):
		if self.data == []:
			return " " * width

		if nwords < 1:
			return " " * width

		if nwords > 1:
			extra = ( width - self.width( nwords ) ) / \
				( nwords - 1.0 )
		else:
			extra = 0.0

		count = 0.0

		str = self.data[0]

		for i in range( 1, nwords ):
			word = self.data[i]
			count = count + extra

			while count >= 1.0:
				str = str + " "
				count = count - 1.0

			if i == ( nwords - 1 ) and count > 0.5:
				count = 0.0
				str = str + " "

			str = str + " " + word

		return str

	def format( self, width, alignment, nwords = -1 ):
		# returns a formatted string
		if nwords < 0:
			nwords = self.fit( width )

		if alignment == LEFT:
			return self.ljust( width, nwords )
		elif alignment == RIGHT:
			return self.rjust( width, nwords )
		elif alignment == CENTER:
			return self.center( width, nwords )
		elif alignment == JUSTIFY:
			return self.justify( width, nwords )


class Block:
	"""
	Block data and format methods.
	A block is a list of lines.
	"""

	def __init__( self, lines = [] ):
		self.lines = lines

	def count( self ):
		return len( self.lines )

	def width( self ):
		width = 0

		for line in self.lines:
			if len( line ) > width:
				width = len( line )

		return width

	def center( self, width ):
		new_lines = []
		mywidth = self.width()
		lpadd = ( width - mywidth ) / 2
		rpadd = width - mywidth - lpadd

		for line in self.lines:
			new_line = " " * lpadd + line + " " * rpadd
			new_lines = new_lines + [new_line]

		return Block( new_lines )

	def rjust( self, width ):
		new_lines = []
		mywidth = self.width()
		lpadd = width - mywidth

		for line in self.lines:
			new_line = " " * lpadd + line
			new_lines = new_lines + [new_line]

		return Block( new_lines )

	def ljust( self, width ):
		new_lines = []
		mywidth = self.width
		rpadd = width - mywidth

		for line in self.lines:
			new_line = line + " " * rpadd
			new_lines = new_lines + [new_line]

		return Block( new_lines )

	def output( self, out = sys.stdout ):
		for line in self.lines:
			out.write( string.rstrip( line ) + "\n" )


class Paragraph:
	"""
	Paragraph data and format methods.
	"""

	def __init__( self ):
		self.width = 69

		self.reset_style()

	def reset_style( self ):
		self.lindent = 0	# left identation
		self.rindent = 0	# right identation
		self.findent = 0	# first line left identation
		self.alignment = JUSTIFY
		self.bullet = None	# bullet
		self.bindent = 0	# bullet identation
		self.space_before = 1
		self.space_after = 1

	def set( self, data ):
		self.words = Words( string.split( data ) )

	def format_line( self, first_line = 0 ):
		str = ""

		# branch depending on whether we are taking care of the
		# first line or not (which could have a bullet)
		if first_line and self.bullet is not None:
			str = str + " " * self.bindent +  \
				self.bullet + \
				" " * ( self.lindent + \
					self.findent - \
					self.bindent - \
					len( self.bullet ) )

			lw = self.width - self.lindent - self.findent - \
				self.rindent

		elif first_line:
			str = str + " " * ( self.lindent + self.findent )

			lw = self.width - self.lindent - self.findent - \
				self.rindent

		else:
			str = str + " " * self.lindent

			lw = self.width - self.lindent - self.rindent

		nwords = self.words.fit( lw )

		if nwords == 0:
			self.words.trim( lw )
			nwords = 1

		if nwords == self.words.count() and self.alignment == JUSTIFY:
			alignment = LEFT
		else:
			alignment = self.alignment

		str = str + self.words.format( lw, alignment, nwords )

		# add right indent
		str = str + " " * self.rindent

		# move pointer to words past what we've just formatted
		self.words.skip( nwords )

		return str


	def format( self ):
		lines = []

		# empty space before
		# we're going to use the empty line later again
		empty_line = " " * self.width

		for i in range( self.space_before ):
			lines = lines + [empty_line]

		# first line is special case
		if self.words.count() > 0:
			line = self.format_line( 1 )
		else:
			line = empty_line

		lines = lines + [line]

		while self.words.count() > 0:
			line = self.format_line()

			lines = lines + [line]

		# print space after
		for i in range(self.space_after):
			lines = lines + [empty_line]

		return Block( lines )



class Cell:
	def __init__( self ):
		self.data = ""
		self.alignment = JUSTIFY
		self.space_before = 0
		self.space_after = 0
		self.rindent = 1
		self.lindent = 1

	def set( self, data ):
		self.data = string.join( string.split( data ), " " )

	def length( self ):
		return len( self.data )

	def format( self, width ):
		# Break cell into a list of lines where the words
		# fit into the maximum width and where each line
		# is padded with blanks to be of the right width
		paragraph = Paragraph()
		paragraph.set( self.data )

		paragraph.width = width
		paragraph.alignment = self.alignment
		paragraph.space_before = self.space_before
		paragraph.space_after = self.space_after
		paragraph.lindent = self.lindent
		paragraph.rindent = self.rindent

		block = paragraph.format()

		return block



class Row:
	def __init__( self ):
		self.cells = []
		self.column_separator = " "

	def add( self, cell ):
		self.cells = self.cells + [cell]

	def num_cells( self ):
		return len( self.cells )

	def format( self, col_width ):
		# formats row
		block_row = []
		row_height = 0

		# one exception: if the row is empty, it means we want a 
		# separator
		if self.cells == []:
			line = "-" * ( sum( col_width ) + len( col_width ) - 1 )
			return Block( [line] )

		col_index = 0

		for cell in self.cells:
			block = cell.format( col_width[col_index] )

			block_row = block_row + [block]

			if block.count() > row_height:
				row_height = block.count()

			col_index = col_index + 1

		# combine cell blocks into one big row block
		lines = []

		for line_index in range( row_height ):
			# the first cell does not have a leading
			# column separator
			lstr = ""

			try:
				block = block_row[0]
				str = block.lines[line_index]
			except:
				# maybe this cell does not have
				# all these lines...
				str = " " * col_width[0]

			lstr = lstr + str

			for col_index in range( 1, len( col_width ) ):
				try:
					block = block_row[col_index]
					str = block.lines[line_index]
				except:
					str = " " * col_width[col_index]

				lstr = lstr + self.column_separator + str

			lines = lines + [lstr]

		block = Block( lines )

		return block


class Table:
	def __init__( self ):
		self.rows = []

		self.reset_style()

		self.width = 69

	def reset_style( self ):
		self.space_before = 2
		self.space_after = 2
		self.column_separator = "|"

	def add( self, row ):
		self.rows = self.rows + [row]

	def num_rows( self ):
		return len( self.rows )

	def size( self ):
		num_cols = 0

		for row in self.rows:
			if row.num_cells() > num_cols:
				num_cols = row.num_cells()

		return ( num_cols, self.num_rows() )

	def cell( self, row_index, col_index ):
		return self.rows[row_index].cells[col_index]


	def total_width( self, col_width ):
		return sum( col_width ) + len( col_width ) - 1


	def initial_column_width( self, num_cols ):
		# don't forget the space between the cells...
		col_width = []

		initial_width = ( self.width - num_cols + 1 ) / num_cols

		for i in range( num_cols ):
			col_width = col_width + [initial_width]

		return col_width

	def ideal_column_width( self, num_cols, num_rows ):
		# let's find out the maximum size of each column if each cell
		# could fit on one line
		# we can't use the formatter because it padds everyline with
		# extra blanks, so we need to be smarter here...

		col_max = []

		for col_index in range( num_cols ):
			max = 0

			for row_index in range( num_rows ):
				try:
					cell = self.cell( row_index, col_index )

					length = cell.length() + \
						cell.lindent + cell.rindent

				except:
					length = 0

				if length > max:
					max = length

			col_max = col_max + [max]

		return col_max

	def format( self ):
		# determine size; necessary for future calculations
		( num_cols, num_rows ) = self.size()

		#
		# 1. set column width
		#

		# at first it's all the same, then we try to make it
		# better...
		col_width = self.initial_column_width( num_cols )

		# determine max/ideal column width
		col_max = self.ideal_column_width( num_cols, num_rows )

		# let's make columns smaller where possible
		for i in range( num_cols ):
			if col_max[i] < col_width[i]:
				col_width[i] = col_max[i]

		# now try to make columns larger
		# as long as we have room and some cells want room, 
		# let's expand the columns...
		modified = 1

		while self.total_width( col_width ) < self.width and modified:
			# let's find columns to expand
			modified = 0

			for i in range( num_cols ):
				if self.total_width( col_width ) < \
					self.width and \
					col_max[i] > col_width[i]:
					col_width[i] = col_width[i] + 1
					modified = 1

		# set the new table width according to this last adjustment,
		# just in case the table is still smaller than the maximum
		# allowed
		self.width = self.total_width( col_width )

		#
		# 2. generate table block
		#

		lines = []
		empty_line = " " * self.width

		# space before
		for i in range( self.space_before ):
			lines = lines + [empty_line]

		# row blocks
		for row in self.rows:
			block = row.format( col_width )

			for line in block.lines:
				lines = lines + [line]

		# space after
		for i in range( self.space_after ):
			lines = lines + [empty_line]

		return Block( lines )


class DocFormatter:
	"""
	Document formatter. This class simply holds document properties like
	margins. You give it a block and it formats it according to the
	document's properties.
	"""

	def __init__( self ):
		self.out = sys.stdout
		self.reset_style()

	def reset_style( self ):
		self.width = 79
		self.lmargin = 5
		self.rmargin = 5

	def useableWidth( self ):
		return self.width - self.lmargin - self.rmargin

	def format( self, block ):
		# A block is a list of lines (strings)
		# We don't just simply add margins, we center the
		# block
		# In fact, the margins are more for top-level parts to find
		# out what width they should use...

		return block.center( self.width )


class Parser(xmllib.XMLParser):

	def __init__( self ):
		self.docFormatter = DocFormatter()

		self.data = ""

		xmllib.XMLParser.__init__( self, 0 )

	def handle_data( self, data ):
		# simply concatenate the strings of data
		self.data = self.data + data

	def start_table( self, attrs ):
		# reset table element
		self.table = Table()

		# inherit attributes from doc
		self.table.width = self.docFormatter.useableWidth()

		# parse table attributes
		# well, there are none supported right now...
		pass

	def end_table( self ):
		# a table is a top-level object; we output it right away
		block = self.table.format()
		block = self.docFormatter.format( block )
		block.output()

	def start_tr( self, attrs ):
		# reset row data
		self.row = Row()

		# parse row attributes
		# well, there are none supported right now...
		pass

	def end_tr( self ):
		# append row data to table
		self.table.add( self.row )

	def start_td( self, attrs ):
		# reset data stream
		self.data = ""
		self.cell = Cell()

                if attrs is not None:
                        # parse attributes
                        for attr, value in attrs.items():
                                if attr == "align":
                                        self.cell.alignment = \
                                                align_codes[value]
                                elif attr == "space_before":
                                        self.cell.space_before = \
                                                string.atoi( value )
                                elif attr == "space_after":
                                        self.cell.space_after = \
                                                string.atoi( value )
                                else:
                                        raise "Unknown attribute " + `attr`

	def end_td( self ):
		# add data to cell and cell to row
		self.cell.set( self.data )
		self.row.add( self.cell )

        def start_p( self, attrs ):
		# reset data stream
		self.data = ""

		# parse attributes to set paragraph style
                self.paragraph = Paragraph()

		# inherit attributes from doc
		self.paragraph.width = self.docFormatter.useableWidth()

                if attrs is not None:
                        # parse attributes
                        for attr, value in attrs.items():
                                if attr == "align":
                                        self.paragraph.alignment = \
                                                align_codes[value]
                                elif attr == "space_before":
                                        self.paragraph.space_before = \
                                                string.atoi( value )
                                elif attr == "space_after":
                                        self.paragraph.space_after = \
                                                string.atoi( value )
                                elif attr == "rindent":
                                        self.paragraph.rindent =  \
                                                string.atoi( value )
                                elif attr == "lindent":
                                        self.paragraph.lindent =  \
                                                string.atoi( value )
                                elif attr == "bullet":
                                        self.paragraph.bullet = value
                                elif attr == "bindent":
                                        self.paragraph.bindent =  \
                                                string.atoi( value )
                                else:
                                        raise "Unknown attribute " + `attr`

        def end_p( self ):
		self.paragraph.set( self.data )
                block = self.paragraph.format()
		block = self.docFormatter.format( block )
		block.output()

	def start_doc( self, attrs ):
		# reset document formatter
                self.docFormatter.reset_style()

                if attrs is not None:
                        # parse attributes
                        for attr, value in attrs.items():
                                if attr == "width":
                                        self.docFormatter.width = \
                                                string.atoi( value )
                                elif attr == "lmargin":
                                        self.docFormatter.lmargin = \
                                                string.atoi( value )
                                elif attr == "rmargin":
                                        self.docFormatter.rmargin = \
                                                string.atoi( value )

        def end_doc( self ):
		# really nothing to do here...
		pass

	def unknown_starttag( self, tag, attrs ):
		if tag == "table":
			self.start_table( attrs )
		elif tag == "tr":
			self.start_tr( attrs )
		elif tag == "td":
			self.start_td( attrs )
		elif tag == "p":
			self.start_p( attrs )
		elif tag == "doc":
			self.start_doc( attrs )
		else:
			# really unknown...
			raise "Unknown tag %s." % tag

	def unknown_endtag( self, tag ):
		if tag == "table":
			self.end_table()
		elif tag == "tr":
			self.end_tr()
		elif tag == "td":
			self.end_td()
		elif tag == "p":
			self.end_p()
		elif tag == "doc":
			self.end_doc()
		else:
			print string.join( string.split( self.data ), " " )
			self.data = ""

			print "</" + tag + ">"



if __name__ == '__main__' and 0:

	#
	# Main program
	#

	data = sys.stdin.read()

	parser = Parser()

	for c in data:
		parser.feed( c )

	parser.close()

def make_table(text_array, headers=None, width=80, margin=1):
	width -= 1
	assert margin >= 1, (
		"Zero and negative margins are not allowed (%r)"
		% margin)
	table = Table()
	table.width = width
	table.space_before = table.space_after = 0
	if headers:
		table.add(make_row(headers, margin=margin))
		table.add(make_row(
			['-'*len(name) for name in headers],
			margin=margin))
	for text_row in text_array:
		table.add(make_row(text_row, margin=margin))
	return table

def make_row(texts, margin=1, alignment=LEFT):
	row = Row()
	for text in texts[:-1]:
		row.add(make_cell(text, margin=margin,
				  alignment=alignment))
	row.add(make_cell(texts[-1], margin=0, alignment=alignment))
	return row

def make_cell(text, margin=1, alignment=LEFT):
	cell = Cell()
	cell.lindent = 0
	cell.rindent = margin-1
	cell.alignment=alignment
	cell.set(text)
	return cell

def make_text(paras):
	if not isinstance(paras, (list, tuple)):
		paras = [paras]
	formatter = DocFormatter()
	formatter.lmargin = formatter.rmargin = 0
	out = StringIO()
	for block in paras:
		block = block.format()
		block.output(out=out)
	return out.getvalue()

def example():
	t = make_table(
		[['This is a really long field that goes on with many short words for a long time until there is no end in sight',
		  'another shorty',
		  '5',
		  'last row that is also really long'],
		 ['This is another row, not so long',
		  'formerly',
		  '22',
		  'and here we stop row'],
		 ['again',
		  'whatever',
		  '55',
		  '*'*80],
		 ],
		headers=['Name 1', 'Name 2', 'Name 3', 'Name 4'],
		width=int(os.environ.get('COLUMNS', 80)),
		margin=1,
		)

	print_text([t])

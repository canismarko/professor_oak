#function to generate barcode from input string, defaults to .SVG format, barcodes in CODE-39 format, returns the name of the output SVG or PNG file

import barcode
from barcode.writer import ImageWriter

# string = '0123456789'

# Had to edit 'add_checksum=True' to 'add_checksum=False' in codex.py (line 75) in source code for pybarcode due to add_checksum being an unexpected keyword argument - can't figure this out!
def generate_barcode(string, output_extension):

	if output_extension in ('PNG', 'png'):
		ean = barcode.get('Code39', string, writer=ImageWriter())
	else:
		ean = barcode.get('Code39', string, writer=None)
	ean.default_writer_options['module_height'] = 13.0
	ean.default_writer_options['module_width'] = 0.01
	filename = ean.save(string)
	return filename
#Python script for reading and reporting the digital inventory with the actual inventory
'''First argument is the real life inventory, second argument is the database (digital inventory)

files (as arguments) should be single lists of barcodes as strings or integers'''

import csv, sys

def create_barcode_actual(filename):
	#sets the barcode numbers of the actual_inventory to a single list, barcode_a
	with open(filename, 'r') as file:
		barcode_actual = []
		actual_inventory = csv.reader(file)
		for row in actual_inventory:
			barcode_actual.extend(list(map(int,row)))
		file.close()
	return barcode_actual

def create_barcode_database(filename):
	#sets the barcode numbers of the digital_inventory to a single list, barcode_d
	with open(filename, 'r') as file:
		barcode_database = []
		database_inventory = csv.reader(file)
		for row in database_inventory:
			barcode_database.extend(list(map(int,row)))
		file.close()
	return barcode_database
	
def analyse(barcode_actual, barcode_database):
	#crunches the numbers
	accounted_for, not_in_db, not_in_actual = [],[],[]
	for number in barcode_actual:
		if number in barcode_database:
			barcode_database.remove(number)
			# barcode_a.remove(number)
			accounted_for.append(number)
		else:
			not_in_db.append(number)
	not_in_actual = barcode_database	 
	return accounted_for, not_in_db, not_in_actual
	
if __name__ == "__main__":	
	if str(sys.argv) in ('syntax', 'help'):
		print ('Syntax is: inventory_reader.py ACTUAL_INVENTORY DATABASE_INVENTORY')
		exit()
	elif len(sys.argv) > 3:
		print ('Too many arguments! Syntax is: inventory_reader.py ACTUAL_INVENTORY DATABASE_INVENTORY')
		exit()
	elif len(sys.argv) < 3:
		print ('Not enough arguments! Syntax is: inventory_reader.py ACTUAL_INVENTORY DATABASE_INVENTORY')
		exit()
	
		
	barcode_actual = create_barcode_actual(sys.argv[1])
	barcode_database = create_barcode_database(sys.argv[2])
	
	accounted_for, not_in_db, not_in_actual = analyse(barcode_actual, barcode_database)

	#return accounted_for, not_in_db, not_in_actual

	print ('Analysis complete...')
	print (str(len(accounted_for)) + ' chemicals accounted for')
	print (str(len(not_in_db)) + ' chemicals found but not active in the database')
	print (not_in_db)
	print (str(len(not_in_actual)) + ' chemicals in the database but not found')
	print (not_in_actual)

#dumbDB

#TO-DO
#DONE	make path saved in table relative to directory holding dumbDB.py, to allow use on removable memory
#	use file creation time if no EXIF data
#DONE	for import, display image on screen and then prompt for tags
#	for import, keep focus on terminal, autoclose displayed image after tags are entered
#	for import, suggest tags (autofill suggestions from previously used tags)


import hashlib
import sys, os
from PIL import Image
import subprocess
import datetime


DUMBDBDIR = os.path.dirname(os.path.abspath(sys.argv[0])) + '/dumbDBDir/'
print DUMBDBDIR
DUMBDBTABLE = os.path.dirname(os.path.abspath(sys.argv[0])) + '/dumbDBTable.txt'
MONTHS = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']



def getHash(thefile):
	BLOCKSIZE = 65536
	hasher = hashlib.md5()
	with open(thefile, 'rb') as afile:
		buf = afile.read(BLOCKSIZE)
		while len(buf) > 0:
			hasher.update(buf)
			buf = afile.read(BLOCKSIZE)
		print hasher.hexdigest()
	return hasher.hexdigest()


print sys.argv


if sys.argv[1] == "import":
	for infile in sys.argv[2:]:
		#Get file data
		fullpath = os.path.abspath(infile)
		print fullpath
		filename = fullpath.split('/')[-1]
		print filename
		extension = filename.split('.')[-1]
		print extension
		dirpath = fullpath[:-len(filename)]
		print dirpath
		image = Image.open(fullpath)
		#testing = datetime.datetime.strptime(image._getexif()[36867], "%Y:%m:%d %H:%M:%S")
		#print testing
		try:
			date, time = image._getexif()[36867].split(' ')
			print image._getexif()[36867]
		except:
			print "No EXIF data found!"
			#try:
			#	
			sys.exit()
		image.thumbnail((800,800))
		image.save("./temp.JPG","JPEG")
	#	image.show()
		p = subprocess.Popen(["display","./temp.JPG"])
		input_string = raw_input("Enter space-delimited tags: ")
		p.kill()
		date = date.replace(':','-')
		print date
		print time
		year, month, day = date.split('-')
		month = MONTHS[int(month)-1]
		print month
		taglist = input_string.split(' ')
		tags = ','.join(taglist)
		print tags
	
		#check for existing month directory, create if not exists
		dirContents = os.listdir(DUMBDBDIR)
		print dirContents
		if month+year in dirContents:
			print DUMBDBDIR+month+year+'/'+"  exists!"
		else:
			print "Creating "+DUMBDBDIR+month+year
			os.system("mkdir "+DUMBDBDIR+month+year)
	
		#copy file     filename = last six characters of hashstring
		monthContents = os.listdir(DUMBDBDIR+month+year)
		fullHash = getHash(fullpath)
		newName = fullHash[-6:]+'.'+extension
		if newName in monthContents:
			print "COLLISION!     Quitting..."
			sys.exit()
		else:
			os.system("cp "+fullpath+" "+DUMBDBDIR+month+year+'/'+newName)
	
		#Add entry to table
		with open(DUMBDBTABLE, 'a') as table:
			table.write(newName+'\t'+'./dumbDBDir/'+month+year+'/'+'\t'+date+'\t'+tags+'\n')

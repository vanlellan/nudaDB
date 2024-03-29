## TODO
[X] make path saved in table relative to directory holding nudaDB.py, to allow use on removable memory
[X] use file timestamp if no EXIF data
[X] for import, display image on screen and then prompt for tags
[X] for import, keep focus on terminal, autoclose displayed image after tags are entered
[ ] for import, suggest tags (autofill suggestions from previously used tags)
[ ] check entire db for duplicate files on import? (no, use a separate command, perhaps "status")
[ ] ability to search db and display images and edit tags
[-] implement optparse (nope, keep git-style commands)
[-] add command line option to keep file in inbox upon successful import (...why?)
[X] allow wildcards on command line
[X] save previously entered tag-string history, accessible with up arrow (importing readline makes raw_input do this automatically)
[X] change name to nudusDB/nudaDB/nudumDB. ('nudus' is latin for simple/unadorned/bare)
[X] make it 'standalone' executable
[X] make 'install' command to add it to bin and create ./inbox/ and ./inbox/imported/ directories
[X] write real README
[X] implement tag dictionary for searching
[X] test ability to gracefully abort importing
[X] move collision checking and skip before prompt for tags
[ ] save a thumbnail of each imported image for less RAM-intensive browsing (/nudaDBThumbs/)
[X] python3 compatibility (probably no longer python2 compatible...)
[ ] windows compatibility
[ ] OSX compatibility
[ ] browser-based client?
	[-] how easy is it to write a front-end in something like Dash?
	[-] Jellyfin (or similar) _almost_ works out-of-the-box as a viewer/server for nudaDB
	[X] Flask! super easy
	[ ] implement thumbnails for quicker search results, load full image only when clicked
	[X] make flask page able to serve up a mix of video and image files as the results of a search
	[ ] ability to upload, import, and tag via browser?
[ ] make search succeed on partial matches
[ ] full regex implementation (optional)?
[ ] config file (.nudarc) for specifying optional behaviors
[ ] commandline option to specify a default tag string which will be preloaded on the Entry bar with each picture during import
[ ] gracefully handle a file missing
[ ] ability to pause and resume the slideshow
[ ] fix bug when last file of import is a collision (tag input window doesn't close itself)
[X] slideshow: shuffle all matching images
[ ] slideshow: forward/backward one step
[X] change nudaDBDir subdirectory name format to YYYY-MM rather than "AUG2019" format
[ ] automatically handle files with spaces in the filename
[-] add feature: generate sub-database. output a full nuda database filled with the output of a search
	[X] handled by "subnuda" deploy with custom pickle file
[ ] add feature: GUI command to edit tags during slideshow
[X] add ability to import video, use vlc embedded in tk window
[X] ability to gracefully merge two DBs (nuda merge pulls entries from THAT nuda instance into THIS nuda instance)
[X] add another tkEntry, which is auto-filled with the datetime info, this can be modified by the user, and then send_tags uses it
[ ] add ability to deliberately skip, or even delete, a file during import (button, ctrl-key, and/or command tag)
[ ] add 2nd pickle file, in which keys are filenames and values are lists of tags
[ ] add list of tags to flask page, either as captions under each image or as hover text
[ ] automatically add filename (without suffix) as a tag
[ ] compound tags (e.g. "Genus+Sciurus")
	[ ] add both "Genus+" and "+Scurius" as tags
	[ ] same for searching
	[ ] this allows for a general search of all things with a tagged Genus
[X] strip-down old slideshow class to reimplement a pure slideshow (import stuff is now in importClass.py)
[ ] write a proper man-page and/or command line help
[X] write function to auto-generate flask deployment, and subNuda task deployment (added to nuda tags)
	[ ] add gunicorn deploy stuff to repo
[X] rework "nudaDBDIR" symlink in subNuda flask deployment so that unauthorized files can't be manually accessed
	[X] instead of symlinking entire directory, symlink only individual files
	[X] this then needs to be updated everytime the tags are regenerated
	[X] on subNuda tag generation, check for flask deployment, and rewrite symlinks
[ ] change name to "nuda"
[ ] add man page generation and installation into nuda-install

## Ideas
[ ] change name to 'fresco'
	or 'rat' (Rapid Album Tagger)
	or 'itad' (Image Tag and Display)
	or 'sat' (Simple Album Tagger)
	rapid fast simple easy tag display present show slide-show album gallery 
	or 'hycom' (Hyrule Compendium), or name it after the Lab director or assistant
[ ] fill inbox from external media feature
	-search computer for external media
	-find 'DCIM' directories
	-copy files in DCIM directories into fresco inbox
[X] slideshow feature
	-start a slideshow of all images matching a given tag list
NOPE	-default: only use the tag "show", tag favorite images with "show" so that they appear in slideshow
[ ] consider possible raspberrypi/raspbian optimizations
	-best possible layman-deployment vector
	-raspberry pi + hard drive with flask page and dnsmasq for local network, browser-based access to media

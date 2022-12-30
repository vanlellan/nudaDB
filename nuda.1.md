% NUDA(1) nuda 0.0.3
% Randall Evan McClellan
% December 2022

# NAME
nuda - the simple tagged media database

# SYNOPSIS
**nuda** <*COMMAND*> [*args*]

# DESCRIPTION
**nuda** provides a command-line tool for importing media files (only image and video files so far) into a local directory structure. A GUI is launched during import to allow the user to provide tags (i.e. search keywords) for each imported image or video. The user can also adjust the auto-filled date and time information if necessary. After importing media, **nuda** provides various methods for querying and viewing the contents of the 'database'.

# OPTIONS
Currently, **nuda** has no options, only git-style commands

# COMMANDS
**nuda-init**, **nuda init**
: initialize the current working directory as a nuda instance

**nuda-install**, **nuda install**
: install nuda into the operating system. The current working directory must be a clone of the nuda repo

**nuda-tags**, **nuda tags [keywords]**
: generate the tag dictionary pickle file to facilitate searching by tags. If keyword is provided, generate a subnuda containing only media matching the space-delimited keywords.

**nuda-search**, **nuda search [keywords]**
: **DEPRECATED** Select media from the database matching the keywords, and link them into the /search/ subdirectory.

**nuda-slideshow**, **nuda slideshow [picklefile]**
: Launch the slideshow GUI, optionally selecting images only from a subnuda pickle file.

**nuda-reset**, **nuda reset**
: **DANGER** Reset the nuda instance. All imported files are moved back to /inbox/. All skipped files are moved back to /inbox/. The nudaDBDir subdirectories are removed. The nudaDBTable.txt file is removed. Requires the environment variable **ALLOWNUDARESET** to be set to True.

**nuda-import**, **nuda import [files]**
: Launch import GUI to import all files in the /inbox/ subdirectory. Optionally, provide specific files to be imported instead. Subdirectories within /inbox/ are ignored.

**nuda-merge**, **nuda merge [TARGET]**
: Merge all imported files from TARGET directory into current working directory. Files that already exist in the current database are skipped.

# COPYRIGHT
Copyright 2018 Randall Evan McClellan. License GPLv3+: GNU GPL version 3 or later <https://gnu.org/license/gpl.html>. This is a free softwareL you are free to change and redistribute it. There is NO WARRANTY, to the extent permitted by law.

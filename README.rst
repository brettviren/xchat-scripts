XChat Scripts
=============

These repository holds some Python scripts for extending XChat.  To
use them, put them in ``~/.xchat2``.  In xchat type:

	/py load script.py


memory.py
---------

Augment your own memory by keeping a database of characteristics of
subjects.  This script defines:

``/remember SUBJECT CHARACTERISTIC``
  Remember something about some thing:

``/lookup SUBJECT [NUMBER]`` 
  Look up most recent characteristic about
  subject or specific one based on given NUMBER.

``/remembered``
  List what subjects have been remembered.

``/forget thing [all|number]`` 
  Forget something about thing.  By
  default forget the oldest thing or specify a number to forget a
  specific thing or'all' to forget everything about thing.

Memories are stored in an Sqlite3 datbase file named "memories.db" and
in the same directory as memory.py.

#!/usr/bin/env python
'''

An xchat plugin script to keep a database of things to remember.

To install:

 - stick it in ~/.xchat2/
 - to turn on:
   /py load memory.py
 - to turn off:
   /py unload memory.py 

Database is kept in "memory.db" in the same directory as this file.


Memory operates by hooking in to the commands:

Remember something about some thing:

/remember thing Something to remember about thing.

Look up something remembered about thing.  Most recently remembered
thing is returned by default or specify a specific index

/lookup thing [number]

List what things have been remembered.

/remembered

Forget something about thing.  By default forget the oldest thing or
specify a number to forget a specific thing or'all' to forget everything
about thing.

/forget thing [all|number]
'''

__module_name__ = "memory" 
__module_version__ = "1.0" 
__module_description__ = "Augment your own memory" 

import os
import sqlite3

class MemorySqlite(object):
    '''
    Use Sqlite to remember things about subjects.
    '''

    default_table_name = 'memories'
    schema = 'ts timestamp, subject text, memory text'

    def __init__(self,dbname,table_name = None):
        self.conn = sqlite3.connect(dbname)

        if table_name:
            self.table_name = table_name
        else:
            self.table_name = MemorySqlite.default_table_name

        # Create table if it doesn't exist
        cmd = 'SELECT name FROM sqlite_master WHERE name="%s"' % \
              self.table_name
        c = self.conn.execute(cmd)
        rows = c.fetchall()
        if not rows:
            print 'Table "%s" not found, creating it.' % self.table_name
            c = self.conn.execute('CREATE TABLE %s(%s)' % \
                                  (self.table_name, MemorySqlite.schema))
        else:
            print 'Found table "%s".' % self.table_name
        return

    def select(self, what, where = None, order = None):
        '''
        Do a select on our table.  what is what you select, where is
        optional
        '''
        cmd = 'SELECT %s from %s ' % (what,self.table_name)
        if where: cmd += 'WHERE %s' % where
        if order: cmd += 'ORDER BY %s' % order
        #print cmd
        return self.conn.execute(cmd)

    def insert(self,**kwds):
        keys = []
        values = []
        for key,value in kwds.items():
            keys.append(key)
            values.append(value)
            continue
        cmd = "insert into %s(%s) values (%s)" % (self.table_name,
                                                  ','.join(keys),
                                                  ','.join(['?']*len(keys)))
        cur = self.conn.execute(cmd,values)
        self.conn.commit()
        return cur


    def add(self,subject,memory,timestamp = None):
        '''
        Record memory about subject.  Timestamp should be a
        datetime.datetime or if None then the current time will be
        used.
        '''
        if timestamp:
            ts = timestamp
        else:
            from datetime import datetime
            ts = datetime.now()
        return self.insert(subject=subject,memory=memory,ts=ts)
        
    def subjects(self):
        '''
        Return list of (subject,count) tuples giving the number of
        things remembered about each subject.
        '''
        ret = []
        c = self.select('DISTINCT subject')
        for row in c:
            name = row[0]
            c2 = self.select('count(*)','subject = "%s"'%name)
            ret.append((name,c2.next()[0]))
            continue
        return ret

    def recollect(self,subject):
        '''
        Return rows corresponding to given subject
        '''
        c = self.select("*", where = 'subject = "%s"'%subject, order="ts")
        ret = []
        for row in c:
            ret.append(row)
        return ret
        

import xchat
class XchatMemory(object):

    def __init__(self,database = None):
        '''
        Create an XchatMemory object
        '''
        if database:
            self.db = database
        else:
            dbname = os.path.splitext(__file__)[0] + '.db'
            #print dbname,__file__
            try:
                self.db = MemorySqlite(dbname)
            except sqlite3.OperationalError:
                print 'Failed to open %s' % dbname
                raise
            pass
        return

    def remember(self,word,word_eol,userdata):
        'Remember memory about subject'
        self.db.add(word[1],word_eol[2])
        return xchat.EAT_ALL

    def xprint(self,name,msg):
        #event = 'Channel Message'
        event = 'Private Message'
        if msg:
            #print msg
            xchat.emit_print(event,name,msg)

    def xprint_mem(self,mem):
        'Xchat-print a memory'
        dat = mem[0]
        sub = mem[1]
        msg = mem[2]
        msg += " (%s)" % dat
        self.xprint(sub,msg)

    def lookup(self,word,word_eol,userdata):
        'Look up memory about subject'
        subject = word[1]
        mems = self.db.recollect(subject)
        mems.reverse()

        numbers = map(int,word[2:])     # ignore all but first
        if numbers:
            mems = [mems[numbers[0]-1]]
        for mem in mems:
            self.xprint_mem(mem)
        return xchat.EAT_ALL

    def remembered(self,word,word_eol,userdata):
        'List what things have been remembered.'
        msg = []
        subjects = self.db.subjects()
        #print subjects
        for sub,cnt in subjects:
            msg.append('%s:%d' % (sub,cnt) )
            continue
        self.xprint('memory',', '.join(msg))

        return xchat.EAT_ALL

    def forget(self,word,word_eol,userdata):
        'Forget oldest, numbered or all memory about subject'
        #,subject,what='oldest'):
        return xchat.EAT_ALL

def bind_xchat():
    '''
    Bind to XChat
    '''
    xm = XchatMemory()
    xchat.hook_command('remember',xm.remember)
    xchat.hook_command('lookup',xm.lookup)
    xchat.hook_command('remembered',xm.remembered)
    xchat.hook_command('forget',xm.forget)
    

def do_test(args):
    ms = MemorySqlite(':memory:')
    ms.add('thing1','Thing1 is the first thing')
    ms.add('thing2','Thing2 is the second thing')
    ms.add('thing1','Thing1 is the best thing')
    print ms.subjects()
    for row in ms.recollect('thing1'):
        print row
    return

if __name__ == '__main__':
    import sys
    try:
        cmd = sys.argv[1]
    except IndexError:
        bind_xchat()
        pass
    else:
        func = eval ("do_%s" % cmd)
        func(sys.argv[1:])

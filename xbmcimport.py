#!/usr/bin/env python

# First run tutorial.glade through gtk-builder-convert with this command:
# gtk-builder-convert tutorial.glade tutorial.xml
# Then save this file as tutorial.py and make it executable using this command:
# chmod a+x tutorial.py
# And execute it:
# ./tutorial.py


import os,re,sys,pyinotify,stat

# The directory where your xbmc tv shows are stored, without trailing slash




class XbmcImport():
    
    def __init__(self,dir,file):
        if not os.path.exists (dest_dir_episode):
            os.makedirs (dest_dir_episode)
        print dest_dir_episode
        #shutil.move(file,dest_dir_episode+"/"+tvfile.clean_name)
        print file,dest_dir_episode+"/"+tvfile.clean_name

    

class TVObject():
    """class for tv object"""
    def __init__(self,file):
        self.name = file
        self.clean_name = self.clean().replace(' ','.')
        self.ep_showname, self.ep_number, self.ep_season, self.name = self.tv_parser(self.clean())
        self.dest_dir_episode = dest_dir+"/"+self.ep_showname+"/"+"Season "+str(self.ep_season)

        
    def clean(self):
        """Replace underscores with spaces, capitalise words and remove
        brackets and anything inbetween them.
        """
        s = self.name
        file =  self.name
        opening_brackets = ['(', '[', '<', '{']
        closing_brackets = [')', ']', '>', '}']
        for i in range(len(opening_brackets)):
            b = opening_brackets[i]
            c = closing_brackets[i]

            while b in s:
                start = s.find(b)
                end = s.find(c) + 1

                s = re.sub(re.escape(s[start:end]), '', s)

        results = os.path.splitext(s)
        extension = results[1]
        s = results[0]

        s = s.replace('_', ' ')
        s = s.replace('.', ' ')
        s = s.strip()
        words = s.split(' ')
        s = ' '.join([w.capitalize() for w in words])
        s = s + extension
        s = re.sub('S\d+(e)\d+', self.fix_episode, s)

        return s

    def fix_episode(self,matchobj):
        """Used by the clean function to fix season capitalisation"""
        return matchobj.group(0).upper()

    def tv_parser(self,file):
        """Extract info from the file"""
        def tv_extractor(file):
            ep_season = int(results.groups()[0])
            ep_number = int(results.groups()[1])
            ep_showname = re.match('(.+?)\^s', file)
            ep_showname = ep_showname.groups()[0].strip(' .')
            ep_showname= os.path.basename(ep_showname)
            return (ep_showname, ep_number, ep_season, file)
    
        results = re.search(r'[s|S](\d+)[e|E](\d+)', file)
        if results:
            file = re.sub('[s|S](\d+)[e|E](\d+)', '^s^e', file)
            return tv_extractor(file)

        results = re.search(' (\d)(\d\d) ', file)
        if results:
            file = re.sub(' \d\d\d ', '^s^e', file)
            return tv_extractor(file)

        results = re.search('(\d+)[Xx](\d\d)', file)
        if results:
            file = re.sub('\d+[Xx]\d\d', '^s^e', file)
            return tv_extractor(file)


        return ('', '', '', file)




        


if __name__ == "__main__":
    dir = sys.argv[1]
    dest_dir = sys.argv[2]
    wm = pyinotify.WatchManager()

    mask = pyinotify.IN_ATTRIB |pyinotify.IN_MOVED_TO # watched events

    class EventHandler(pyinotify.ProcessEvent):
        def process_IN_ATTRIB(self, event):
            print event.pathname
            if os.path.isdir(event.pathname) == False:
                self.move(event)
        def process_IN_MOVED_TO(self, event):
            print event.pathname
            if os.path.isdir(event.pathname) == False:
                self.move(event)

        def move(self, event):
            tv=TVObject(event.name)
            dst=tv.dest_dir_episode+"/"+tv.clean_name
            src=event.pathname
            if not os.path.exists (tv.dest_dir_episode):
                os.makedirs (tv.dest_dir_episode)
                st = os.stat(dest_dir)
                my_dir=tv.dest_dir_episode
                while (my_dir != dest_dir):
                    #os.chown(my_dir, st.st_uid, -1)
                    os.chown(my_dir, st.st_uid, st.st_gid)
                    my_dir= os.path.abspath(os.path.join(my_dir, os.path.pardir))
            os.system('mv "%s" "%s"' % (src,dst)) 
    #notifier = pyinotify.ThreadedNotifier(wm, EventHandler())
    notifier = pyinotify.Notifier(wm, EventHandler())
    # Start watching a path
    wdd = wm.add_watch(dir, mask, rec=True)
    # Start the notifier from a new thread, without doing anything as no directory or file are currently monitored yet.
    #notifier.start()
    #notifier.loop()
    try:
        notifier.loop(daemonize=True, pid_file='/var/run/xbmcimport.pid')
    except pyinotify.NotifierError, err:
        print >> sys.stderr, err
    
    
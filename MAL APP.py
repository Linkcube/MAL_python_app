"""
Important
This code requires cURL in order to work.

A guide to download cURL: http://guides.instructure.com/s/2204/m/4214/l/83393-how-do-i-install-and-use-curl-on-a-windows-machine

This code will query myanimelist.net for info pertaining to a certain account (requiring credentials beforehand)
and will allow the user to update their anime list through the python shell as well as load
webpages from various anime stream sites for the user based upon the progress made in the list.
"""
import subprocess # used to make system calls that can be recorded
import cStringIO # record system calls as files to support multiple lines (stored in memory)
import getpass # to hide the password input
import webbrowser # to open default web browser
import urllib # used to interract with http and retrieve status codes
import logging # used for logging.. kinda what it says, ya know?

class Series():
    def __init__ (self, title="", Id="", cE="", tE="", Syn="", Status="", Score=""): # declare variables for the series
        self.title = title
        self.Id = Id
        self.cE = cE
        self.tE = tE
        self.Syn = Syn
        self.Status = Status
        self.Score = Score

    def menuFormat(self): # returns a string in the form suitable for the menu
        return self.title+" ["+self.Id+"] "+self.cE+"/"+self.tE+" "+self.Status

    def getFromID(self, ID, mode): # retrieves info using an id
        logger.info('Retrieving series from ID: %s.' % str(ID))
        bluf = cStringIO.StringIO()
        blah = "?mine=1"
        if mode: typ = "anime"
        else: typ = "manga"
        bluf.write(subprocess.check_output('curl -u "'+username+'":"'+password+'" mal-api.com/'+typ+'/'+str(ID)+blah, shell=True))
        logger.info('getFromID curl request returned: \n%s.' % bluf.getvalue())
        Title, Id, Syn, cE, tE, Score, Stat = Parse(Clean(bluf))
        self.title, self.Id, self.cE ,self.tE, self.Syn, self.Status, self.Score = Title[0], Id[0], cE[0], tE[0], Syn[0], Stat[0], Score[0] # compacting variables
        bluf.close()

    def watch(self): # watches a series onlne by inputting its own variables to WO(...)
        logger.info('Starting watch sequence.')
        titl = self.title.replace(" ","-")
        titl = titl.replace(":","")
        titl = titl+"-episode-"+str(int(self.cE)+1)
        titl = titl.lower()
        dead = True
        sites = ["http://www.animeseason.com/","http://www.gogoanime.com/","http://www.lovemyanime.net/"]
        for site in sites:
            print "Trying "+site
            if urllib.urlopen(site+titl).getcode() == 200:
                logger.info('Connecting to %s.' % site)
                print "Connecting to "+site+"..."
                webbrowser.open_new(site+titl)
                progress = str(raw_input("Did you finish the episode (yes/dead/*): "))
                if progress == "yes": #finished the episode, update mal
                    print self.update(int(self.cE)+1, 2, 1)
                    dead = False
                    break
                elif progress == "dead": # the link is dead
                    logger.info('Link is dead.')
                    pass
                else: # the user didn't watch the episode, don't try other streams
                    logger.info("Didn't watch.")
                    dead = False
                    break
            else:
                logger.info('%s failed.' % site)
                print site+" appears to be dead"
        if dead:
            logger.error('Episode not found, dead or non-existant.')
            print "Not found, episode may not exist."

    def update(self, value, typ, mode): # updates the series with a certain new value for a specified mode
        logger.info('Begining update process with %s, %s, %s.' % str(value), str(typ), str(mode))
        if typ == 1: self.Status = str(value)
        elif typ == 2: self.cE = str(value)
        elif typ == 3: self. Score = str(value)
        b = cStringIO.StringIO() # begins to update with cURL
        if mode == 1: b.write(subprocess.check_output('curl -u "'+username+'":"'+password+'" -X PUT -d status='+self.Status+
                                                ' -d episodes='+self.cE+' -d score='+self.Score+' http://mal-api.com/animelist/anime/'+str(self.Id), shell=True))
        else: b.write(subprocess.check_output('curl -u "'+username+'":"'+password+'" -X PUT -d status='+self.Status+
                                              ' -d chapters='+self.cE+' -d score='+self.Score+' http://mal-api.com/mangalist/manga/'+str(self.Id), shell=True))
        if b.getvalue() == "":
            logger.info('Updated Successfully.')
            print "Updated Successfully"
        else:
            logger.eror('Update Failed.')
            print "Update Failed"
        if self.cE == self.tE and typ == 2:
            self.update(2, 1, mode)

"""
Note to self, the search function grabs a webpage similar to the 502 exception page
that MAL/MML with grab from myanimelist directly, use the parsing found in Search()
instead to remove dependancy on mal-api.com
"""
def Search(search): # performs a search function, returning different values based on search results
    logger.info('Search has been called for %s' % search)
    buf = cStringIO.StringIO()
    if mode == 1: typ = 'anime'
    else: typ = 'manga'
    buf.write(Curl(typ+'/search.xml?q='+search))
    entry = 0 # number of entries found
    IDs = [] # array of id values
    Titles = [] # array of tile values
    Syn = [] # array of synopses
    tBool = False # a boolean that toggles when to continue multiple lines of title
    tmpT = "" # temp for titles spanning longer than one line
    sBool = False # synopsis
    tmpS = "" # temp for synopsis
    result = buf.getvalue().split("\n")
    for lines in result:
        line = lines
        line = line.replace("<"," ") # removes < and > to parse easier
        line = line.replace(">"," ")
        ls = line.split()
        if "entry" in ls: entry += 1 #checks for the number of entries
        if "id" in ls: IDs.append(ls[1]) # checks for what the ID of the result is
        if "title" in ls: tBool = True #  begins the caching of the title lines
        if tBool: tmpT += lines # caching of the title
        if "/title" in ls: # checks for the end of the title sequence
            tBool = False
            Titles.append(tmpT[11:-8])
            tmpT = ""
        if "synopsis" in ls: sBool = True #  begins the caching of the title lines
        if sBool: tmpS += lines # caching of the title
        if "/synopsis" in ls: # checks for the end of the title sequence
            sBool = False
            Syn.append(tmpS[14:-11])
            tmpS = ""
    for i in range(0,len(Titles)):
        print str(i+1)+". "+Titles[i]
    finished = False
    while not finished: # loop until correct name is selected or quit
        name = raw_input("Enter the corresponding number to the anime: ")
        if name == "exit": break # break out of the loop
        if int(name) not in range(1,entry+1):
            print "You entered an invalid input"
        else:
            finished = True
            i = int(name)-1 # corrects for array placement to human numbering
    if finished: 
        print Titles[i]
        print IDs[i]
        print Syn[i]
        answer = str(raw_input("Enter 'yes' if this is the correct anime: "))
        if answer != "yes": finished = False
    if not finished:
        logger.info('Returned 0 for the ID.')
        return 0 # returns that no anime was found
    else:
        logger.info('Returned %s for the ID.' % str(IDs[i]))
        return IDs[i] # returns id of selected anime if user says so

def Curl(args):
    logger.info('cURL has been called for %s.' % args)
    return subprocess.check_output('curl -u "'+username+'":"'+password+'" '+MALapi+args, shell=True)

def Clean(buf): # cleans a string buffer from MAL-API json
    logger.info('Cleaning json from mal-api.')
    page = buf.getvalue() # same steps as search
    page = page.replace(":"," ") # cleaning out the raw string from cURL for parsing
    page = page.replace(","," ")
    page = page.replace("{","")
    page = page.replace("}","")
    page = page.replace("[","")
    page = page.replace("]","")
    page.strip()
    while '  ' in page:
        page = page.replace('  ',' ')
    strings = []
    for i in page.split('"'):
        if i != ' ': strings.append(i)
    tA = [] # the actual array of data that will be analyzed
    for i in strings:
        tA.append(i.strip())
    return tA

def Parse(tA): # parses the split data from MAL
    logger.info('Parsing data from MAL.')
    Titles = []
    IDs = []
    Syns = []
    cEP = []
    tEP = []
    Scores = []
    Status = []
    pos = 0
    for phrase in tA:
        if phrase == "title": # looks for the title
            Titles.append(tA[pos+1])
        if phrase == "synopsis": # looks for the synopsis
            Syns.append(tA[pos+1])
        if phrase == "id": # looks for the id
            IDs.append(tA[pos+1])
        if phrase == "watched_episodes" or phrase == "chapters_read": # looks for the current episode
            cEP.append(tA[pos+1])
        if phrase == "episodes" or phrase == "chapters": # looks for the total episodes
            tEP.append(tA[pos+1])
        if phrase == "watched_status" or phrase == "read_status": # looks for the watching status
            Status.append(tA[pos+1])
        if phrase == "score": # looks for the score given
            Scores.append(tA[pos+1])
        pos += 1
    if Titles == []:
        logger.error('Parse attempt failed and returned no data.')
        if tA[0] != None:
            tt = ""
            for value in tA: tt += value + '\n'
            logger.critical('Parsing error occurred on string buffer: %s.' % tt)
        Titles, IDs, Syns, cEP, tEP, Scores, Status = ["Failed to Access",], ["0",], ["0",], ["0",], ["0",], ["0",], ["0",]
    return Titles, IDs, Syns, cEP, tEP, Scores, Status

"""
I'll document this function more because of the complex situation ive put myself into;
@param buf Takes in a cStringIO.getvalue() string that is xml data retrieved from MAL
@param mode Is told the mode to parse the data in, either as manga or anime
@return Returns the normal output for MAL()/MML()
This is effectively housekeeping to keep the lines of code from piling up especially
after I had fixed the functionality of the 'backup' option and had both MAL() and MML()
running extrememly similar code
"""
def malParse(buf, mode=True):
    logger.info('malParse has been called.')
    if mode == True: toFind = ["series_animedb_id","series_title","my_watched_episodes",
                               "series_episodes","my_status","my_score"]
    else: toFind = ["series_mangadb_id","series_title","my_read_chapters","series_chapters",
                    "my_status","my_score"]
    result = buf.split("><")
    IDs, Titles, cEP, tEP, Scores, Status = [], [], [], [], [], [] # all list holding respective values
    for lines in result:
            line = lines
            line = line.replace("<"," ") # removes < and > to parse easier
            line = line.replace(">"," ")
            ls = line.split()
            if toFind[0] in ls: # checks for the id of a series
                IDs.append(ls[1])
            if toFind[1] in ls: # checks for the title of a series
                Titles.append(" ".join(ls[1:-1]))
            if toFind[2] in ls: # checks for the current episode of a series
                cEP.append(ls[1])
            if toFind[3] in ls: # checks for the total eps of a series
                tEP.append(ls[1])
            if toFind[4] in ls: # checks for the status of a series
                Status.append(int(" ".join(ls[1:-1])))
            if toFind[5] in ls: # checks for current user score of the series
                Scores.append(ls[1])
    return Titles, IDs, ["XML",], cEP, tEP, Scores, Status

def MAL(): # retrieves the anime list of a user
    logger.info('MAL has been called.')
    buf = cStringIO.StringIO()
    try:
        buf.write(subprocess.check_output('curl myanimelist.net/malappinfo.php?u='+username+'&type=anime'))
        return malParse(buf.getvalue(), True)     
    except: return ["Failed to Access",], ["0",], ["0",], ["0",], ["0",], ["0",], ["0",] # if none of the above work

def MML(): # retrieves the manga list of a user
    logger.info('MML has been called.')
    buf = cStringIO.StringIO()
    try:
        buf.write(subprocess.check_output('curl myanimelist.net/malappinfo.php?u='+username+'&type=manga'))
        return malParse(buf.getvalue(), False)   
    except: return ["Failed to Access",], ["0",], ["0",], ["0",], ["0",], ["0",], ["0",] # if none of the above work
    
# the encryption method atm is extremely weak and more along the original intent of this
# program, which was a learning project. Make sure to change if it becomes anything more.
def Encrypt(usr, psw): # encrypts the password using the username
    logger.info('Encrypting password.')
    encr = ""
    for ch in psw:
        encr += chr(ord(ch)+len(usr) % 256)
    try:
        f = open("conf.txt", 'w')
        f.write(encr)
        f.close()
        print "Password saved"
        logger.info('Password wrote successfully')
        return True
    except:
        logger.info('Password write failed')
        return False

def Decrypt(usr, f): # Decrypts the password using the username
    logger.info('Opening file for decryption')
    try:
        nenc = f.read()
    except:
        logger.info('Failed to read file.')
        return False
    dencr = ""
    for ch in nenc:
        dencr += chr(ord(ch)-len(usr) % 256)
    logger.info('Password successfully decrypted.')
    return dencr

#==================================================================================
# Start of program
# Set user specified variables here:
savePassword = True # Will save the password with feeble encryption, your choice (True/False)
# End of user variables, mess with code at your own risk
#==================================================================================

# Set up logging
logger = logging.getLogger('Logging')
logger.setLevel(logging.DEBUG)
ch = logging.FileHandler('MAL_APP_log.txt')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)
logger.info('+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
logger.info('Program started.')

"""if subprocess.check_output('curl') != "curl: try 'curl --help' or 'curl --manual' for more information":
    print "This program requires cURL in order to run, please install and restart this program"
    webbrowser.open_new("http://guides.instructure.com/s/2204/m/4214/l/83393-how-do-i-install-and-use-curl-on-a-windows-machine")
    exit""" # meant to check if curl is installed, find a better method
MALapi = "http://myanimelist.net/api/" # the basis of the url to acess MAL api
cred = False # whether the credentials went through
password = ""
username = str(raw_input("Enter your username: "))
if savePassword: # if the password is set to remember, check for it before asking for pass
    try:
        f = open("conf.txt", 'r')
        password = Decrypt(username, f)
        f.close()
        logger.info('Password accessed from file.')
    except:
        print "Password retrieval failed, file not found"
        logger.info('Password from file retrieval failed.')
while not cred: # get a valid account from the user to use MAL api correctly
    if username == "": username = str(raw_input("Enter your username: "))
    if password == "": password = getpass.getpass()
    output = cStringIO.StringIO()
    try: # Attempts to access myanimelist.net with the credentials
        output.write(Curl('account/veriy_credentials.xml'))
    except: # If the connection fails then don't show the credentials in the terminal window to protect user data
        print "========================================"
        print "Failed to Connect, please check your internet connection. If this problem persists then myanimelist may be down"
        print "========================================"
        logger.error('Failed to connect when verifying credentials.')
        break # Leaves the loop with cred = False
    result = output.getvalue()
    if result == "Invalid credentials":
        logger.error('Failed loggin attempt for %s' % username)
        print "Invalid credentials, try again"
        password = ""
        username = ""
    else: cred = True
    output.close()
actions = ["Search","View My List","Select a Series","Refresh","Set ID","Change Mode","Exit"] # list of actions available to the user
if cred: # If the logon did work, try fetching data through MAL() before proceeding
    if savePassword: Encrypt(username, password)
    logger.info('Login sucessful for %s.' % username)
    print "Login sucess!"
    print "What mode do you want be in? \n1. Anime\n2. Manga"
    while True:
        mode = int(raw_input(": "))
        if mode != 1 and mode !=2: print "Enter a valid option"
        else: break
    if mode == 1:Titles, IDs, Syns, cEP, tEP, Scores, Status = MAL() # begins retrieving data from MAL
    else: Titles, IDs, Syns, cEP, tEP, Scores, Status = MML() # manga version
    p, ID, watching, completed, plan, drop, hold, canrun = 1, 0, [], [], [], [], [], True # compacting lines
    if Titles[0] == "Failed to Access": # The servers are down, end.
        print "The servers are down at the moment for mal-api.com, please try again later"
        canrun = False
        logger.error('Failed access to servers.')
else: # MAL is down, don't run the program any more
    canrun = False
    print "Sorry, offline mode is not implemented yet."
    logger.info('MAL is down, exiting program sequence.')
    exit()
if mode == 1: conv = {2: 'completed', 6: 'plan to watch', 1: 'watching', 3: 'on-hold', 4: 'dropped'}
else: conv = {2: 'completed', 1: 'reading', 3: 'on-hold', 4: 'dropped'}
if canrun: # if servers are up
    Anime = [] # The anime list
    for anime in Titles: # parses data from MAL
        if isinstance(Status[p-1], int): Status[p-1] = conv[Status[p-1]]
        Anime.append(Series(Titles[p-1],IDs[p-1],cEP[p-1],tEP[p-1],"Failed Lookup",Status[p-1],Scores[p-1])) # Fills up the anime list with series as the raw lists are parsed
        string = str(p)+". "+Anime[p-1].menuFormat()
        if Status[p-1] == "completed": completed.append(string)
        if Status[p-1] == "plan to watch": plan.append(string)
        if Status[p-1] == "watching" or Status[p-1] == "reading": watching.append(string)
        if Status[p-1] == "on-hold": hold.append(string)
        if Status[p-1] == "dropped": drop.append(string)
        p += 1
    if mode == 1: print "Data recieved, you are currently watching:"
    else: print "Data recieved, you are currently reading:"
    for anime in watching: # returns the currently watching
        print anime
    while True:
        logger.info('Home, ID = %s' % str(ID))
        if Titles[0] == "Failed to Access": # The servers are down, end.
            print "The servers are down at the moment for mal-api.com, please try again later"
            logger.error('mal-api.com servers were not reached, breaking.')
            break
        print "You currently are selecting ID: "+str(ID)
        if mode == 1: print "Mode: Anime"
        else: print "Mode: Manga"
        tmp = 1
        print "What action do you want to take: "
        for act in actions:
            print str(tmp)+" "+act
            tmp += 1
        action = int(raw_input(""))
        if action == 1: # begins the search for an anime and returning it's id
            logger.info('Selected action: Search')
            search = str(raw_input("What do you want to search: "))
            search = search.replace(" ","+")
            ID = Search(search)
            if ID == 0: print "No anime selected"
        if action == 2: # returns the full anime list
            logger.info('Selected action: View list')
            if mode == 1: print "================Watching================"
            else: print "================Reading================"
            for anime in watching: print anime
            print "================Completed================"
            for anime in completed: print anime
            if mode == 1: print "================Plan to Watch================"
            else: print "================Plan to Read================"
            for anime in plan: print anime
            print "================Dropped================"
            for anime in drop: print anime
            print "================On Hold================"
            for anime in hold: print anime
        if action == 3: # inspect an anime from the list
            logger.info('Selected action: Inspect')
            buf = cStringIO.StringIO()
            blah = "?mine=1"
            if ID == 0: # if no anime selected use default
                while True:
                    number = int(raw_input("Enter the corrosponding number to the anime you want: "))
                    if number in range(0, len(Titles)+1): break
                    else: print "You entered an invalid number"
                print "Series selected, info loading below:"
                selSeries = Anime[number-1] # Reuse existing data if appropriate
            else:
                print "Loading information"
                selSeries = Series()
                selSeries.getFromID(ID, mode) # Creates a new series object with respective variables for inspect actions
            whatToSay = ["Title: "+selSeries.title,"<ID: "+selSeries.Id+">","Progress: "+selSeries.cE+"/"+selSeries.tE+", Status: "+selSeries.Status,"Synopsis: "+selSeries.Syn,"Score: "+selSeries.Score,"What action do you want to take: "]
            for items in whatToSay: print items
            if mode == 1 and (selSeries.cE != selSeries.tE): print "1. Watch online"
            print "2. Update"
            print "3. Nothing"
            r = int(raw_input(""))
            if r == 1: # attempt streams for selected anime
                logger.info('Launching series.watch() for %s' % str(selSeries.title))
                selSeries.watch()
            if r == 2: # show update options
                logger.info('Choices.')
                print "What do you want to update?"
                print "1. Change status"
                if mode == 1: print "2. Change episode progress"
                else: print "2. Change chapter progress"
                print "3. Change score"
                choice = int(raw_input(""))
                if choice == 1: # changes the status
                    logger.info('Changing status')
                    print "What status do you want to change to?"
                    if mode == 1: status = ['Watching', 'Completed', 'On Hold', 'Dropped', 'Plan to Watch']
                    else: status = ['Reading', 'Completed', 'On Hold', 'Dropped']
                    k = 1
                    for modes in status:
                        print str(k)+". "+modes
                        k += 1
                    c = int(raw_input(""))
                    if c > 0 and c < len(status):
                        if c == 5 : c = 6 # to work with mal-api
                        logger.info('Calling update( %s, %s, %s)' % str(c), str(choice), str(mode))
                        selSeries.update(c, choice, mode)
                    else: # kicks the user out
                        logger.error('User chose invalid input')
                        print "Broke out"
                elif choice == 2: # change episode
                    logger.info('Setting current episode.')
                    if mode == 1: c = int(raw_input("Set current episode: "))
                    else: c = int(raw_input("Set current chapter: "))
                    selSeries.update(c, choice, mode)
                elif choice == 3: # change score
                    c = int(raw_input("Enter the score: "))
                    if c > 0 and c < 11: # check for valid number
                        logger.info('Changing the score')
                        selSeries.update(c, choice, mode)
            else: pass # does nothing
                        
        if action == 4: # refreshes anime list and resets selection
            logger.info('Refreshing List.')
            print "Retrieving Data.."
            if mode == 1: Titles, IDs, Syns, cEP, tEP, Scores, Status = MAL() # begins retrieving data from MAL
            else: Titles, IDs, Syns, cEP, tEP, Scores, Status = MML()
            p, ID, watching, completed, plan, drop, hold = 1, 0, [], [], [], [], [] # compacting lines
            if mode == 1: conv = {2: 'completed', 6: 'plan to watch', 1: 'watching', 3: 'on-hold', 4: 'dropped'}
            else: conv = {2: 'completed', 1: 'reading', 3: 'on-hold', 4: 'dropped'}
            if canrun: # if servers are up
                Anime = [] # Clears old list
                for anime in Titles: # parses data from MAL
                    if isinstance(Status[p-1], int): Status[p-1] = conv[Status[p-1]]
                    Anime.append(Series(Titles[p-1],IDs[p-1],cEP[p-1],tEP[p-1],"Failed Lookup",Status[p-1],Scores[p-1])) # Fills up the anime list with series as the raw lists are parsed
                    string = str(p)+". "+Anime[p-1].menuFormat()
                    if Status[p-1] == "completed": completed.append(string)
                    if Status[p-1] == "plan to watch": plan.append(string)
                    if Status[p-1] == "watching" or Status[p-1] == "reading": watching.append(string)
                    if Status[p-1] == "on-hold": hold.append(string)
                    if Status[p-1] == "dropped": drop.append(string)
                    p += 1
            print "Data recieved, you are currently watching:"
            for anime in watching: # returns the currently watching
                print anime
        if action == 5: # sets the id
            ID = int(raw_input("Enter a select ID: "))
            logger.info('Changed ID to %s' % str(ID))
        if action == 6: # changes the mode between anime and manga
            if mode == 1: mode = 2
            else: mode = 1
            logger.info('Changed mode to %s' % str(mode))
            # Cheap code copypasta, fix it up with a function at some point
            logger.info('Refreshing List.')
            print "Retrieving Data.."
            if mode == 1: Titles, IDs, Syns, cEP, tEP, Scores, Status = MAL() # begins retrieving data from MAL
            else: Titles, IDs, Syns, cEP, tEP, Scores, Status = MML()
            p, ID, watching, completed, plan, drop, hold = 1, 0, [], [], [], [], [] # compacting lines
            if mode == 1: conv = {2: 'completed', 6: 'plan to watch', 1: 'watching', 3: 'on-hold', 4: 'dropped'}
            else: conv = {2: 'completed', 1: 'reading', 3: 'on-hold', 4: 'dropped'}
            if canrun: # if servers are up
                Anime = [] # Clears old list
                for anime in Titles: # parses data from MAL
                    if isinstance(Status[p-1], int): Status[p-1] = conv[Status[p-1]]
                    Anime.append(Series(Titles[p-1],IDs[p-1],cEP[p-1],tEP[p-1],"Failed Lookup",Status[p-1],Scores[p-1])) # Fills up the anime list with series as the raw lists are parsed
                    string = str(p)+". "+Anime[p-1].menuFormat()
                    if Status[p-1] == "completed": completed.append(string)
                    if Status[p-1] == "plan to watch": plan.append(string)
                    if Status[p-1] == "watching" or Status[p-1] == "reading": watching.append(string)
                    if Status[p-1] == "on-hold": hold.append(string)
                    if Status[p-1] == "dropped": drop.append(string)
                    p += 1
            print "Data recieved, you are currently watching:"
            for anime in watching: # returns the currently watching
                print anime
        if action == 7: # exits from the program
            logger.info('Exiting the program.')
            break
bleak = raw_input("Thank you for using this app, press enter to exit...")
logger.info('Program has fully ended.')
logger.info('++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')

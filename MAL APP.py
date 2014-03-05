"""
Important
This code requires cURL in order to work, which can be downloaded as well as a tutorial on
installation with a simple google search. Besides that everything else is default python
with the exception of the directory of the webbrowser, which will at some point be changed
to ask the user to location (or at least the name to find the app).

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

class Series():
    def __init__ (self, title, Id, cE, tE, Syn, Status, Score): # declare variables for the series
        self.title = title
        self.Id = Id
        self.cE = cE
        self.tE = tE
        self.Syn = Syn
        self.Status = Status
        self.Score = Score

    def menuFormat(self): # returns a string in the form suitable for the menu
        return self.title+" ["+self.Id+"] "+self.cE+"/"+self.tE+" "+self.Status

    def getFromID(ID, mode): # retrieves info using an id
        blah = "?mine=1"
        if mode: typ = "anime"
        else: typ = "manga"
        buf.write(subprocess.check_output('curl -u "'+username+'":"'+password+'" mal-api.com/'+typ+'/'+str(ID)+blah, shell=True))

    def watch(self): # watches a series onlne by inputting its own variables to WO(...)
        WO(self.title,int(self.cE)+1,self.Id,self.Score,self.Score)

    def update(self, value, typ, mode): # updates the series with a certain new value for a specified mode
        if typ == 1: self.Status = str(value)
        elif typ == 2: self.cE = str(value)
        elif typ == 3: self. Score = str(value)
        b = cStringIO.StringIO() # begins to update with cURL
        if mode == 1: b.write(subprocess.check_output('curl -u "'+username+'":"'+password+'" -X PUT -d status='+self.Status+
                                                ' -d episodes='+self.cE+' -d score='+self.Score+' http://mal-api.com/animelist/anime/'+str(self.Id), shell=True))
        else: b.write(subprocess.check_output('curl -u "'+username+'":"'+password+'" -X PUT -d status='+self.Status+
                                              ' -d chapters='+self.cE+' -d score='+self.Score+' http://mal-api.com/mangalist/manga/'+str(self.Id), shell=True))
        if b.getvalue() == "": print "Updated Successfully"
        else: print "Update Failed"

"""
Note to self, the search function grabs a webpage similar to the 502 exception page
that MAL/MML with grab from myanimelist directly, use the parsing found in Search()
instead to remove dependancy on mal-api.com
"""
def Search(search): # performs a search function, returning different values based on search results
    buf = cStringIO.StringIO()
    if mode == 1: typ = 'anime'
    else: typ = 'manga'
    buf.write(subprocess.check_output('curl -u "'+username+'":"'+password+'" '+MALapi+typ+'/search.xml?q='+search, shell=True))
    entry = 0 # number of entries found
    IDs = [] # array of id values
    Titles = [] # array of tile values
    Syn = [] # array of synopses
    tBool = False # a boolean that toggles when to continue multiple lines of title
    tmpT = "" # temp for titles spanning longer than one line
    sBool = False # synopsis
    tmpS = "" # temp for synopsis
    result = buf.getvalue()
    result = result.split("\n")
    for lines in result:
        line = lines
        line = line.replace("<"," ") # removes < and > to parse easier
        line = line.replace(">"," ")
        ls = line.split()
        if "entry" in ls: #checks for the number of entries
            entry += 1
        if "id" in ls: # checks for what the ID of the result is                
            IDs.append(ls[1])
        if "title" in ls: #  begins the caching of the title lines
            tBool = True
        if tBool: # caching of the title
            tmpT += lines
        if "/title" in ls: # checks for the end of the title sequence
            tBool = False
            Titles.append(tmpT[11:-8])
            tmpT = ""
        if "synopsis" in ls: #  begins the caching of the title lines
            sBool = True
        if sBool: # caching of the title
            tmpS += lines
        if "/synopsis" in ls: # checks for the end of the title sequence
            sBool = False
            Syn.append(tmpS[14:-11])
            tmpS = ""
    i = 1
    for title in Titles:
        print str(i)+". "+title
        i += 1
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
    Id = 0
    if not finished: pass # returns that no anime was found
    else: Id = IDs[i] # returns id of selected anime if user says so
    return Id

def Clean(buf): # cleans a string buffer from MAL-API json
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
        Titles, IDs, Syns, cEP, tEP, Scores, Status = ["Failed to Access",], ["0",], ["0",], ["0",], ["0",], ["0",], ["0",]
    return Titles, IDs, Syns, cEP, tEP, Scores, Status

def findTitle(ls): # Takes in a list of strings, and returns a string of them joined together with spaces
    tmpA = ls[1:-1]
    tmpS = ""
    for item in tmpA:
            tmpS += item+" "
    return tmpS[:-1]

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
    if mode == True: toFind = ["series_animedb_id","series_title","my_watched_episodes",
                               "series_episodes","my_status","my_score"]
    else: toFind = ["series_mangadb_id","series_title","my_read_chapters","series_chapters",
                    "my_status","my_score"]
    result = buf.split("><")
    IDs = []
    Titles = []
    cEP = []
    tEP = []
    Scores = []
    Status = []
    for lines in result:
            line = lines
            line = line.replace("<"," ") # removes < and > to parse easier
            line = line.replace(">"," ")
            ls = line.split()
            if toFind[0] in ls: # checks for the id of a series
                IDs.append(ls[1])
            if toFind[1] in ls: # checks for the title of a series
                Titles.append(findTitle(ls))
            if toFind[2] in ls: # checks for the current episode of a series
                cEP.append(ls[1])
            if toFind[3] in ls: # checks for the total eps of a series
                tEP.append(ls[1])
            if toFind[4] in ls: # checks for the status of a series
                Status.append(int(findTitle(ls)))
            if toFind[5] in ls: # checks for current user score of the series
                Scores.append(ls[1])
    return Titles, IDs, ["XML",], cEP, tEP, Scores, Status

def MAL(): # retrieves the anime list of a user
    buf = cStringIO.StringIO()
    buf.write(subprocess.check_output('curl mal-api.com/animelist/'+username, shell=True))
    if "502" in buf.getvalue(): # if 502 gateway error do xml new api, not working
        print "Mal-api.com is down, initiating Beta program"
        buf.write(subprocess.check_output('curl myanimelist.net/malappinfo.php?u='+username+'&type=anime'))
        Titles, IDs, Syn, cEP, tEP, Scores, Status = malParse(buf.getvalue(), True)
        return Titles, IDs, ["XML",], cEP, tEP, Scores, Status
    else:  # if everything works out fine then use default mal-api.com
        tA = Clean(buf)
        return Parse(tA)     
    buf.close()
    return ["Failed to Access",], ["0",], ["0",], ["0",], ["0",], ["0",], ["0",] # if none of the above work

def MML(): # retrieves the manga list of a user
    buf = cStringIO.StringIO()
    buf.write(subprocess.check_output('curl mal-api.com/mangalist/'+username, shell=True))
    if "502" in buf.getvalue(): # if 502 gateway error do xml new api, not working
        print "Mal-api.com is down, initiating Beta program"
        buf.write(subprocess.check_output('curl myanimelist.net/malappinfo.php?u='+username+'&type=manga'))
        return malParse(buf.getvalue(), False)
    else:  # if everything works out fine then use default mal-api.com
        tA = Clean(buf)
        return Parse(tA)     
    buf.close()
    return ["Failed to Access",], ["0",], ["0",], ["0",], ["0",], ["0",], ["0",] # if none of the above work
    
    

def WO(title,cE,iD,Score,Stat):
    title = title.replace(" ","-")
    title = title+"-episode-"+str(cE)
    title = title.lower()
    dead = True
    if urllib.urlopen("http://www.animeseason.com/"+title).getcode() == 200:
        print "Connecting to animeseason..."
        webbrowser.open_new("www.animeseason.com/"+title)
        progress = str(raw_input("Did you finish the episode (yes/dead/*): "))
        if progress == "yes": #finished the episode, update mal
            print Update(cE,iD,Score,Stat)
        elif progress == "dead": # the link is dead
            pass
        else: # the user didn't watch the episode, don't try other streams
            dead = False
    else: print "animeseason.com appears to either not carry this series or is offline"
    if dead and urllib.urlopen("http://www.gogoanime.com/"+title).getcode() == 200:
        print "Trying gogoanime..."
        webbrowser.open_new("www.gogoanime.com/"+title)
        progress = str(raw_input("Did you finish the episode (yes/*): "))
        if progress == "yes": #finished the episode, update mal
            print Update(cE,iD,Score,Stat)
        elif progress == "dead": # the link is dead
            pass
        else: # the user didn't watch the episode, don't try other streams
            dead = False
    else: print "gogoanime.com appears to either not carry this series or is offline"
    if dead and urllib.urlopen("http://www.lovemyanime.net/"+title).getcode() == 200:
        print "Trying lovemyanime..."
        webbrowser.open_new("www.lovemyanime.net/"+title)
        progress = str(raw_input("Did you finish the episode (yes/*): "))
        if progress == "yes": #finished the episode, update mal
            print Update(cE,iD,Score,Stat)
        else: # didn't finish the episode, don't update mal
            pass
    else: print "Not found on animeseason or gogoanime or lovemyanime, episode may not exist."

#=================================================================
# Start of program
#=================================================================
MALapi = "http://myanimelist.net/api/" # the basis of the url to acess MAL api
cred = False # whether the credentials went through
while not cred: # get a valid account from the user to use MAL api correctly
    username = str(raw_input("Enter your username: "))
    password = getpass.getpass()
    output = cStringIO.StringIO()
    print output.getvalue()
    try: # Attempts to access myanimelist.net with the credentials
        output.write(subprocess.check_output('curl -u "'+username+'":"'+password+'" '+MALapi+'account/veriy_credentials.xml', shell=True))
    except: # If the connection fails then don't show the credentials in the terminal window to protect user data
        print "========================================"
        print "Failed to Connect, please check your internet connection. If this problem persists then myanimelist may be down"
        print "========================================"
        break # Leaves the loop with cred = False
    result = output.getvalue()
    if result == "Invalid credentials": print "Invalid credentials, try again"
    else: cred = True
    output.close()
actions = ["Search","View My List","Select a Series","Refresh","Set ID","Change Mode","Exit"] # list of actions available to the user
if cred: # If the logon did work, try fetching data through MAL() before proceeding
    print "Login sucess!"
    print "What mode do you want be in? \n1. Anime\n2. Manga"
    while True:
        mode = int(raw_input(": "))
        if mode != 1 and mode !=2: print "Enter a valid option"
        else: break
    if mode == 1:Titles, IDs, Syns, cEP, tEP, Scores, Status = MAL() # begins retrieving data from MAL
    else: Titles, IDs, Syns, cEP, tEP, Scores, Status = MML() # manga version
    p = 1
    ID = 0
    watching = []
    completed = []
    plan = []
    drop = []
    hold = []
    canrun = True
    if Titles[0] == "Failed to Access": # The servers are down, end.
        print "The servers are down at the moment for mal-api.com, please try again later"
        canrun = False
else: # MAL is down, don't run the program any more
    canrun = False
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
        if Titles[0] == "Failed to Access": # The servers are down, end.
            print "The servers are down at the moment for mal-api.com, please try again later"
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
            search = str(raw_input("What do you want to search: "))
            search = search.replace(" ","+")
            ID = Search(search)
            if ID == 0: print "No anime selected"
        if action == 2: # returns the full anime list
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
                if mode == 1: buf.write(subprocess.check_output('curl -u "'+username+'":"'+password+'" mal-api.com/anime/'+str(ID)+blah, shell=True))
                else: buf.write(subprocess.check_output('curl -u "'+username+'":"'+password+'" mal-api.com/manga/'+str(ID)+blah, shell=True))
                tA = Clean(buf)
                buf.close()
                Title, Id, Syn, cE, tE, Score, Stat = Parse(tA)
                selSeries = Series(Title[0], Id[0], cE[0], tE[0], Syn[0], Stat[0], Score[0]) # Creates a new series object with respective variables for inspect actions
            print "Title: "+selSeries.title
            print "<ID: "+selSeries.Id+">"
            print "Progress: "+selSeries.cE+"/"+selSeries.tE+", Status: "+selSeries.Status
            print "Synopsis: "+selSeries.Syn
            print "Score: "+selSeries.Score
            print "What action do you want to take: "
            if mode == 1 and (selSeries.cE != selSeries.tE): print "1. Watch online"
            print "2. Update"
            print "3. Nothing"
            r = int(raw_input(""))
            if r == 1: # attempt streams for selected anime
                selSeries.watch()
            if r == 2: # show update options
                print "What do you want to update?"
                print "1. Change status"
                if mode == 1: print "2. Change episode progress"
                else: print "2. Change chapter progress"
                print "3. Change score"
                choice = int(raw_input(""))
                if choice == 1: # changes the status
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
                        selSeries.update(c, choice, mode)
                    else: # kicks the user out
                        print "Broke out"
                elif choice == 2: # change episode
                    if mode == 1: c = int(raw_input("Set current episode: "))
                    else: c = int(raw_input("Set current chapter: "))
                    selSeries.update(c, choice, mode)
                elif choice == 3: # change score
                    c = int(raw_input("Enter the score: "))
                    if c > 0 and c < 11: # check for valid number
                        selSeries.update(c, choice, mode)
            else: pass # does nothing
                        
        if action == 4: # refreshes anime list and resets selection
            print "Retrieving Data.."
            if mode == 1: Titles, IDs, Syns, cEP, tEP, Scores, Status = MAL() # begins retrieving data from MAL
            else: Titles, IDs, Syns, cEP, tEP, Scores, Status = MML()
            p = 1
            ID = 0
            watching = []
            completed = []
            plan = []
            drop = []
            hold = []
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
        if action == 6: # changes the mode between anime and manga
            if mode == 1: mode = 2
            else: mode = 1
            # Cheap code copypasta, fix it up with a function at some point
            print "Retrieving Data.."
            if mode == 1: Titles, IDs, Syns, cEP, tEP, Scores, Status = MAL() # begins retrieving data from MAL
            else: Titles, IDs, Syns, cEP, tEP, Scores, Status = MML()
            p = 1
            ID = 0
            watching = []
            completed = []
            plan = []
            drop = []
            hold = []
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
            break
bleak = raw_input("Thank you for using this app, press enter to exit...")

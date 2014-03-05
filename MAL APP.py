"""
Important
This code requires cURL in order to work, which can be downloaded as well as a tutorial on
installation with a simple google search. Besides that everything else is default python
with the exception of the directory of the webbrowser, which will at some point be changed
to ask the user to location (or at least the name to find the app).
"""
import subprocess # used to make system calls that can be recorded
import cStringIO # record system calls as files to support multiple lines (stored in memory)
import getpass # to hide the password input

def Search(search): # performs a search function, returning different values based on search results
    buf = cStringIO.StringIO()
    buf.write(subprocess.check_output('curl -u "'+username+'":"'+password+'" '+MALapi+'anime/search.xml?q='+search, shell=True))
    #print buf.getvalue()
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

def Clean(buf): # cleans a string buffer from MAL
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
        if phrase == "watched_episodes": # looks for the current episode
            cEP.append(tA[pos+1])
        if phrase == "episodes": # looks for the total episodes
            tEP.append(tA[pos+1])
        if phrase == "watched_status": # looks for the watching status
            Status.append(tA[pos+1])
        if phrase == "score": # looks for the score given
            Scores.append(tA[pos+1])
        pos += 1
    return Titles, IDs, Syns, cEP, tEP, Scores, Status
    
def MAL(): # retrieves the anime list of a user
    buf = cStringIO.StringIO()
    buf.write(subprocess.check_output('curl mal-api.com/animelist/'+username, shell=True))
    if "502" in buf.getvalue(): # if 502 gateway error do xml new api, not working
        IDs = []
        Titles = []
        cEP = []
        tEP = []
        Scores = []
        Status = []
        buf.write(subprocess.check_output('curl http://myanimelist.net/malappinfo.php?u='+username+'&type=anime', shell=True))
        result = buf.getvalue()
        for lines in result:
            line = lines
            line = line.replace("<"," ") # removes < and > to parse easier
            line = line.replace(">"," ")
            ls = line.split()
            if "series_animedb_id" in ls: # checks for the id of a series
                IDs.append(ls[1:-1])
            if "series_title" in ls: # checks for the title of a series
                Titles.append(ls[1:-1])
            if "my_watched_episodes" in ls: # checks for the current episode of a series
                cEP.append(ls[1:-1])
            if "series_episodes" in ls: # checks for the total eps of a series
                tEP.append(ls[1:-1])
            if "my_status" in ls: # checks for the id of a series
                IDs.append(ls[1:-1])
            if "my_score" in ls: # checks for current user score of the series
                Scores.append(ls[1:-1])
        return Titles, IDs, ["XML",], cEP, tEP, Scores, Status
    else:  # if everything works out fine then use default mal-api.com
        tA = Clean(buf)
        return Parse(tA)     
    buf.close()
    return [], [], [] ,[] ,[] ,[], []
    
    

def WO(title,cE,iD):
    title = title.replace(" ","-")
    title = title+"-episode-"+str(cE)
    title = title.lower()
    #try: subprocess.call("C:\Users\AndrewY\AppData\Local\Google\Chrome\Application\chrome.exe www.gogoanime.com/"+title, shell=True)
    try:
        subprocess.call("C:\Users\AndrewY\AppData\Local\Google\Chrome\Application\chrome.exe www.animeseason.com/"+title, shell=True)
        progress = str(raw_input("Did you finish the episode (yes/*): "))
        if progress == "yes": #finished the episode, update mal
            print Update(cE,iD)
        else: # didn't finish the episode, don't update mal
            pass
    except: # if the running the webpage fails
        print "Failed connection run time"

def Update(cE,ID):
    buf = cStringIO.StringIO()
    buf.write(subprocess.check_output('curl -u "'+username+'":"'+password+'" -d data="episode='+str(cE)+'" '+MALapi+'animelist/update/'+str(ID)+'.xml', shell=True))
    return buf.getvalue()

# Start of program
MALapi = "http://myanimelist.net/api/" # the basis of the url to acess MAL api
cred = False # whether the credentials went through
while not cred: # get a valid account from the user to use MAL api correctly
    username = str(raw_input("Enter your username: "))
    password = getpass.getpass()
    output = cStringIO.StringIO()
    """c = pycurl.Curl()
    c.setopt(c.URL, ''+MALapi+'account/veriy_credentials.xml')
    c.setopt(c.POSTFIELDS, 'username='+username+'&password='+password)
    c.setopt(c.WRITEFUNCTION, output.write)
    c.perform()"""
    print output.getvalue()
    output.write(subprocess.check_output('curl -u "'+username+'":"'+password+'" '+MALapi+'account/veriy_credentials.xml', shell=True))
    result = output.getvalue()
    if result == "Invalid credentials": print "Invalid credentials, try again"
    else: cred = True
    output.close()
    
actions = ["Search","View MAL","Select an Anime","Refresh","Set ID","Exit"] # list of actions available to the user
print "Login sucess! Retrieving Data.."
Titles, IDs, Syns, cEP, tEP, Scores, Status = MAL() # begins retrieving data from MAL
p = 1
ID = 0
watching = []
completed = []
plan = []
drop = []
hold = []
for anime in Titles: # parses data from MAL
    string = str(p)+". "+Titles[p-1]+" ["+IDs[p-1]+"] "+cEP[p-1]+"/"+tEP[p-1]+" "+Status[p-1]
    if Status[p-1] == "completed": completed.append(string)
    if Status[p-1] == "plan to watch": plan.append(string)
    if Status[p-1] == "watching": watching.append(string)
    if Status[p-1] == "on-hold": hold.append(string)
    if Status[p-1] == "dropped": drop.append(string)
    p += 1
print "Data recieved, you are currently watching:"
for anime in watching: # returns the currently watching
    print anime
while True:
    print "You currently are selecting ID: "+str(ID)
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
        print "================Watching================"
        for anime in watching: print anime
        print "================Completed================"
        for anime in completed: print anime
        print "================Plan to Watch================"
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
                if number in range(0, len(Titles)): break
                else: print "You entered an invalid number"
            print "Anime selected, info loading below:"
            buf.write(subprocess.check_output('curl -u "'+username+'":"'+password+'" mal-api.com/anime/'+str(IDs[number-1])+blah, shell=True))
        else:
            print "Loading information"
            buf.write(subprocess.check_output('curl -u "'+username+'":"'+password+'" mal-api.com/anime/'+str(ID)+blah, shell=True))
        tA = Clean(buf)
        buf.close()
        Title, Id, Syn, cE, tE, Score, Stat = Parse(tA)
        print "Title: "+Title[0]
        print "<ID: "+Id[0]+">"
        print "Progress: "+cE[0]+"/"+tE[0]+", Status: "+Stat[0]
        print "Synopsis: "+Syn[0]
        print "Score: "+Score[0]
        print "What action do you want to take: "
        print "1. Watch online"
        print "2. Update"
        print "3. Nothing"
        r = int(raw_input(""))
        if r == 1: # attempt streams for selected anime
            WO(Title[0],int(cE[0])+1,Id[0])
        if r == 2: # show update options
            pass
        else: # exit the user from the anime selection
            pass
    if action == 4: # refreshes anime list and resets selection
        print "Retrieving Data.."
        Titles, IDs, Syns, cEP, tEP, Scores, Status = MAL() # begins retrieving data from MAL
        p = 1
        ID = 0
        watching = []
        completed = []
        plan = []
        drop = []
        hold = []
        for anime in Titles: # parses data from MAL
            string = str(p)+". "+Titles[p-1]+" ["+IDs[p-1]+"] "+cEP[p-1]+"/"+tEP[p-1]+" "+Status[p-1]
            if Status[p-1] == "completed": completed.append(string)
            if Status[p-1] == "plan to watch": plan.append(string)
            if Status[p-1] == "watching": watching.append(string)
            if Status[p-1] == "on-hold": hold.append(string)
            if Status[p-1] == "dropped": drop.append(string)
            p += 1
        print "Data recieved, you are currently watching:"
        for anime in watching: # returns the currently watching
            print anime
    if action == 5: # sets the id
        ID = int(raw_input("Enter a select ID: "))
    if action == 6: # exits from the program
        break

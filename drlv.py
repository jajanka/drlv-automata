from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from time import sleep
from BeautifulSoup import BeautifulSoup
import sys,os,urllib2,re,codecs
import jprops
import hashlib
if sys.version_info < (3, 4):
    import sha3


def loginDrlv(browser, e, p):
    try:
        email = browser.find_element_by_id('email')
        print email.text
        email.send_keys(e)

        passw = browser.find_element_by_id('password')
        print passw.text
        passw.send_keys(p)
        sleep(1)

        login = browser.find_element_by_name('login')
        print login.text
        login.submit()
  
    except Exception, e:
        print e
        print "Nevar ielogoties"

def newMsg(browser):
    try:
        msgHref = browser.find_elements_by_class_name('buttonC')
        if 'jaunu' not in msgHref[0].text:
            return False

        print msgHref[0].text
        msgHref[0].click()
        return True
    except Exception, e:
        print e
        print "Nevar nospiest pogu sutit jaunu vestuli"
        return False

def writeMsg(browser, msg):
    try:
        textareaDiv = WebDriverWait(browser, 80).until(EC.presence_of_element_located((By.CLASS_NAME , "textareaAutoHeight")))
        textarea = textareaDiv.find_element_by_tag_name('textarea')
        textarea.send_keys(msg)
        return True
    except Exception, e:
        print e
        print "Nevar ierakstit vestules tekstu"
        return False

def sendMsg(browser):
    try:
        bttnSendDiv = browser.find_element_by_class_name("right")
        bttnSend = bttnSendDiv.find_element_by_class_name("buttonC") # send msgHref
        print bttnSend.text
        bttnSend.click();
    except Exception, e:
        print e
        print "Nevar aizsutit vestuli"

def closeMsgSentModal(browser):
    try:
        bttnCloseDiv = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.CLASS_NAME , "InfoBoxContentWrap")))
        bttnOpenClose = bttnCloseDiv.find_elements_by_tag_name("button") # close sent msg success modal
        print bttnOpenClose[1].text
        bttnOpenClose[1].click();
        return True
    except Exception, e:
        print e
        print "Nevar aizvert modal pec nosutitas vestules"
        return False

def logoutDrlv(browser):
    try:
        logout = WebDriverWait(browser, 80).until(EC.presence_of_element_located((By.ID , 'logout')))
        logoutHref = logout.find_element_by_tag_name("a")   # logout
        print logoutHref.text
        logoutHref.click()
    except Exception, e:
        print e
        print "Nevar izlogoties"

def attachFileToMsg(browser,file_name):
    print 'Augsupielade pielikumu'
    print os.getcwd()+'\\'+''+file_name
    attachDiv = browser.find_element_by_class_name("attachSIcon")
    attachBttn = attachDiv.find_element_by_tag_name("input") 
    attachBttn.send_keys(os.getcwd()+'\\info\\'+file_name)

def getEmails(properties):
    p = re.compile("^\w+([-+.']\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$")
    return [key for key in properties.iterkeys() if p.match(key)]

def getMsgToSend(msg_file_dir):
    try:
        msg = ''
        with codecs.open(msg_file_dir, 'r', encoding='windows-1257') as fp:
            msg = fp.read()
        return msg
    except Exception, e:
        print e
        print "Kaut kas netaa ar vestules teksta failu"

def getUids(g, p):
    try:
        link = 'http://www.draugiem.lv/'+g+'/fans/?pg='+str(p)

        soup = BeautifulSoup(urllib2.urlopen(link).read())
        raw_uids = soup.findAll('div', attrs={'class': 'aboutInfo'})
        return [ uid.find('a').get('href') for uid in raw_uids ]
    except Exception, e:
        print e
        print "Iespejams noradits nekorekts grupas nosaukums"

def getLastFanPageNumber(g):
    try:
        link = 'http://www.draugiem.lv/'+g+'/fans/?pg=0'

        soup = BeautifulSoup(urllib2.urlopen(link).read())
        page_table = soup.findAll('table', attrs={'class': 'navig'})
        h = ''.join([ str(e) for e in page_table ])
        soup = BeautifulSoup(h)
        
        page_nav = [ uid.get('href') for uid in soup.findAll('a') ]
        pages = [ int(page.split('?pg=')[1]) for page in page_nav ]

        return max(pages)
    except Exception, e:
        print e
        print "Nevar ieguut pedejo lapu"

def RepresentsInt(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False

def Timeout(minutes):
    print 'Vestules nosutitas ar visiem loginiem. Iestajas gaidishanas rezims uz',minutes, 'minutem'
    for i in range(minutes):
        print 'Gaida:', i+1,'no',minutes, 'minutem'
        sleep(60)
    print 'Gaidishana beigusies. Sakas vestulu sutishana'


def main():

    # -----------------------------------------------------------------
    # Variables

    # Constants
    INI_FILE_NAME = "info\data.ini"
    MSG_FILE_NME = "info\message.txt"
    MSGS_PER_LOGIN = 9

    msg_file_dir = os.getcwd()+'\\'+MSG_FILE_NME
    msgToSend = getMsgToSend(msg_file_dir)

    #print 'Vestule: '+msgToSend
    # Data from file
    ini_file_dir = os.getcwd()+'\\'+INI_FILE_NAME
    properties = {}
    with open(ini_file_dir) as fp:
        properties = jprops.load_properties(fp)
    print 'data.ini fails',properties

    # all emails
    loginEmails = getEmails(properties)
    print 'Tavi profili',loginEmails
    group = properties['group']
    emailCount = len(loginEmails)

    # vars for keeping track of current login, fan page, msgs sent
    page = 0
    lastPage = 0
    if RepresentsInt( properties['groupStart'] ): page = int(properties['groupStart'])
    else:
        print 'Nekorekts grupas lapas numurs ieks fails'
        sys.exit()

    lastPage = int(getLastFanPageNumber(group))
    print 'Grupas ['+group+'] sekotaju lapu skaits:',lastPage

    TEST = '1'
    if properties['test'] == '0':
        TEST = '0'
    print "test:",TEST

    loadImages = '0'
    if properties['loadImages'] == '1':
        loadImages = '1'

    timeout = 25
    if RepresentsInt( properties['timeout'] ): timeout = int(properties['timeout'])
    else:
        print 'Nekorekts timeout failaa'
        print 'Timeouts tiek uzstadits uz 25 minutem'

    print 'Timeouts:',timeout

    attachFile = properties['attachFile']
    attachFileName = properties['attachFileName']

    attachTime = 10
    if RepresentsInt( properties['attachTime'] ): attachTime = int(properties['attachTime'])
    else:
        print 'Nekorekta vertiba pie \'augsupladeshanas laika \''

    currentLoginProfile = 0
    currentUid = 0
    msgsSent = 0
    totalUsersVisited = 0
    lastUser = False
    isMsgSent = False
    isModalClose = True

    # get user ids from group page 
    uids = getUids(group, page)

    print 'Lietotaju celi lapaa',page,':',uids
    print 'To skaits:',len(uids)

    # End of variables
    # ------------------------------------------------------------------------
    # Sart browser
    browser = 0
    if properties['browser'] == 'Chrome':
        if loadImages == '0':
            chromeOptions = webdriver.ChromeOptions()
            prefs = {"profile.managed_default_content_settings.images":2}
            chromeOptions.add_experimental_option("prefs",prefs)
            browser = webdriver.Chrome(chrome_options=chromeOptions)
            print 'ImagesOff'
        else:
            browser = webdriver.Chrome()
            print 'ImagesOn'

    elif properties['browser'] == 'Firefox':
        firefoxProfile = FirefoxProfile()
        firefoxProfile.set_preference('permissions.default.image', 3)
        browser = webdriver.Firefox(firefoxProfile)
    else:
        print "Nepareiza parlukprogrammas opcija"
        sys.exit()
    # ------------------------------------------------------------------------

    while True: # main loop
        for email in loginEmails: # email loop

            if currentUid >= len(uids):
                page +=1 
                uids = getUids(group, page)
                currentUid = 0

            browser.get('http://www.draugiem.lv'+uids[currentUid])
            print 'LietotajaUid:',currentUid, uids[currentUid]
            
            print 'Ielogojas ar ['+email+']'
            loginDrlv(browser, email, properties[email])

            while True: # message loop
                print 'lappuse:', page
                if newMsg(browser):

                    if writeMsg(browser, msgToSend):
                        isModalClose = False
                        if attachFile == '1':
                            attachFileToMsg(browser,attachFileName)
                            sleep(attachTime)
                        if TEST == '0': 
                            sendMsg(browser)
                            sleep(3) # for modal refresh
                            if closeMsgSentModal(browser):
                                isModalClose = True

                        msgsSent += 1
                        isMsgSent = True
                        print "Nosutitas zinas ar tekoso loginu:",msgsSent

                else: 
                    isMsgSent = False

                if msgsSent >= MSGS_PER_LOGIN or lastUser: break

                currentUid += 1
                totalUsersVisited += 1

                if currentUid >= len(uids):
                    page +=1 
                    if page > lastPage:
                        print 'Sasniegts pedejais grupas sekotajs. Beigas'
                        lastUser = True
                        currentUid = 0
                        break
                    uids = getUids(group, page)
                    currentUid = 0

                browser.get('http://www.draugiem.lv'+uids[currentUid])
                print 'LietotajaUid:',currentUid, uids[currentUid]


            msgsSent = 0

            print 'Logina vestulu limits sasniegts'
            print 'Izlogojas no ['+email+']'

            if not isModalClose: 
                print 'Modal pec vestules izsutisana nav aizverts. Parlade lapu un izlogojas...'
                browser.get('http://www.draugiem.lv'+uids[0])

            logoutDrlv(browser)
            sleep(2)

            if lastUser:
                break

        if lastUser:
            print 'Beigas'
            break

        Timeout(timeout)


if __name__ == '__main__':
    main()

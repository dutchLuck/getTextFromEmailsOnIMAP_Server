#! /usr/bin/python3
#
# G E T T E X T F R O M E M A I L S O N I M A P _ S E R V E R
#
# This script prints out text from emails to stdout
#
# Last Modified on Sun Aug 28 21:58:51 2022
#
# 0v2 Use better defaults to handle missing config info
# 0v1 Reworked the code to make it less monolithic
#
# This code is an expansion of demo code provided by
# Dr Sreenivas Bhattiprolu (a.k.a. "bnsreenu" or "DigitalSreeni")
# ( see video https://youtu.be/K21BSZPFIjQ )
# https://github.com/bnsreenu/python_for_microscopists/tree/master/AMT_02_extract_gmails_from_a_user
"""
Additional considerations if your account is a gmail account
1. Make sure you enable IMAP in your gmail settings
(Log on to your Gmail account and go to Settings, See All Settings, and select
 Forwarding and POP/IMAP tab. In the "IMAP access" section, select Enable IMAP.)
2. If you have 2-factor authentication, gmail requires you to create an application
specific password that you need to use. 
Go to your Google account settings and click on 'Security'.
Scroll down to App Passwords under 2 step verification.
Select Mail under Select App. and Other under Select Device. (Give a name, e.g., python)
The system gives you a password that you need to use to authenticate from python.
"""
# Other sources of somewhat similar imap demo code are; -
# https://www.geeksforgeeks.org/python-fetch-your-gmail-emails-from-a-particular-user/
#
# For Search categorys other than Subject: https://gist.github.com/martinrusev/6121028#file-imap-search
#
import sys
import imaplib
import email
import json  #Load config from a json format file
from datetime import datetime
import sys  # sys.argv
import getopt  # getopt()
import getpass  #getpass()
#
# Set up items that can be specified from the command line
# Items specified on the command line over-ride config data
# that may be supplied from a json file.
options = {
    "debug": False,
    "file" : "",
    "help": False,
    "category": "",
    "mailbox": "",
    "password": "",
    "port": "",
    "server": "",
    "term": "",
    "user": "",
    "verbose": False,
    "wait": float(2),
}
# Set up dummy configuration data, but expect
# actual config to be read-in from a json file
configData = [
  {
    "user" : "localuser",
    "password" : "",
    "server" : "localhost",
    "port" : "143",
    "mailbox" : "Inbox",
    "category" : "Subject",
    "term" : "Test"
  }
]


def outputMessageText( msgs ):
    #Now we have all messages, but with a lot of details
    #we can extract the text and print it on the screen

    #In a multipart e-mail, email.message.Message.get_payload() returns a 
    # list with one item for each part. The easiest way is to walk the message 
    # and get the payload on each part:
    # https://stackoverflow.com/questions/1463074/how-can-i-get-an-email-messages-text-content-using-python

    # NOTE that a Message object consists of headers and payloads.

    cnt = 1
    for msg in msgs[::-1]:
        for response_part in msg:
            if type(response_part) is tuple:
                # print( response_part )
                # print( email.message_from_bytes((response_part[0])))
                my_msg=email.message_from_bytes((response_part[1]))
                print("_________________________________________________.#(%05d)#._________" % cnt )
                # print(my_msg)
                cnt = cnt + 1
                print("Subject:", my_msg['subject'])
                print("To:", my_msg['to'])
                print("From:", my_msg['from'])
                print("Date:", my_msg['date'])
                print("Body:")
                for part in my_msg.walk():  
                    # print(part.get_content_type())
                    if part.get_content_type() == 'text/plain':
                        print(part.get_payload())
    print("_________________________________________________.#(00000)#._________")


def getIMAP_AccountEmailText( server, port, user, password, mbox, category, term, verboseFlag ):    
    #
    # Set up an IMAP capability set with zero members
    capabilitySet = {}
    # Establish connection with mail server using SSL if using port 993
    #  otherwise establish connetion and then establish SSL later
    try:
        if port == "993":
            my_mail=imaplib.IMAP4_SSL( server )
        else:
            my_mail=imaplib.IMAP4( server, port )
    except OSError as err:
        print("OS error: {0}".format(err), file=sys.stderr)
        print('?? Unable to connect to "%s" on port "%s"?' % ( server, port ), file=sys.stderr)
    else:
        # Show Protocol version if verbose output is selected
        response, data = my_mail.capability()
        if verboseFlag:
            print( 'Capability response was: "%s"' % response, file=sys.stderr )
        if response == "OK" :
            capabilitySet = set( str( data[0], 'utf-8' ).split())
            if verboseFlag:
                print( 'Capabilility Set is: %s' % capabilitySet )
        else:
            print( '?? Capability response was: "%s"' % response, file=sys.stderr )
        if verboseFlag:
            print( 'Server "%s" runs protocol version: "%s"' % ( server, my_mail.PROTOCOL_VERSION ), file=sys.stderr)
    # If port 143 and the server has the capability then do STARTTLS step
        if port == "143":
            if "STARTTLS" in capabilitySet:
                response, data = my_mail.starttls()
                if verboseFlag:
                    print( 'STARTTLS response was: "%s"' % response, file=sys.stderr )
            else:
                print( '? Port 143 in use, but no STARTTLS available: Connection is not encrypted' )
        try:
        # Log in using your credentials
            my_mail.login( user, password )
        except imaplib.IMAP4.error as err:
            print("imaplib.IMAP4.error: {0}".format(err), file=sys.stderr)
            print( '?? Login to server "%s" as "%s" failed?' % ( server, user ), file=sys.stderr)
        else:
            # Select the mailbox (read-only) from which to fetch messages
            response, data = my_mail.select( mbox, True)
            if response != 'OK' :
                print( 'Select response was: "%s"' % response, file=sys.stderr )
                print( '?? Select mailbox "%s" failed?' % mbox, file=sys.stderr )
            else:
                if verboseFlag:
                    print( 'Mailbox "%s" select response was: "%s"' % ( mbox, response), file=sys.stderr )
                    print( 'Mailbox "%s" message count is: "%s"' % ( mbox, data ), file=sys.stderr )
                try:
                    if category == "" or term == "":
                        response, data = my_mail.search(None, 'ALL' )  #Search for all emails
                    else:
                        response, data = my_mail.search(None, category, term )  #Search for emails with specific category and terms
                except imaplib.IMAP4.error as err:
                    print( "imaplib.IMAP4.error: {0}".format(err), file=sys.stderr)
                    print( '?? Search "%s" for "%s" failed?' % ( category, term ), file=sys.stderr)
                else:
                    if verboseFlag:
                        print( 'Searching "%s": "%s" for "%s"' % ( mbox, category, term ), file=sys.stderr)
                    mail_id_list = data[0].split()  #IDs of all emails that we want to fetch 

                    msgs = [] # empty list to capture all messages
                    #Iterate through messages and extract data into the msgs list
                    for num in mail_id_list:
                        typ, data = my_mail.fetch(num, '(RFC822)') #RFC822 returns whole message (BODY fetches just body)
                        msgs.append(data)

                    #Unselect the mailbox with close as unselect() wasn't available
                    my_mail.close()
                    #
                    outputMessageText( msgs )
                    
        #Logout of the server
        response, data = my_mail.logout()
        if verboseFlag:
            print( 'IMAP Server response to logout request was "%s"' % response, file=sys.stderr )


def printOutAllTheOptions():
    print( "Command line options are; -" )
    print( ' Debug Flag is: "%s"' % options["debug"] )
    print( ' File name is: "%s"' % options["file"] )
    print( ' Help Flag is: "%s"' % options["help"] )
    print( ' category descriptor is: "%s"' % options["category"] )
    print( ' Mailbox name is: "%s"' % options["mailbox"] )
    print( ' Password string is: "%s"' % options["password"] )
    print( ' Port number is: "%s"' % options["port"] )
    print( ' Server name is: "%s"' % options["server"] )
    print( ' Term to search for is: "%s"' % options["term"] )
    print( ' User account name is: "%s"' % options["user"] )
    print( ' Verbose Flag is: "%s"' % options["verbose"] )
    print( ' Wait time is: "%s"' % options["wait"] )


def printOutAllConfigFileOptions():
    print( "Config File specified options are; -" )
    print( ' Category descriptor is: "%s"' % configData[0]["category"] )
    print( ' Mailbox name is: "%s"' % configData[0]["mailbox"] )
    print( ' Password string is: "%s"' % configData[0]["password"] )
    print( ' Port number is: "%s"' % configData[0]["port"] )
    print( ' Server name is: "%s"' % configData[0]["server"] )
    print( ' Term to search for is: "%s"' % configData[0]["term"] )
    print( ' User account name is: "%s"' % configData[0]["user"] )


def usage():
    print( "Usage:\n%s [ -cABC -D -fA.B -h -mABC -pABC -Pxyz -sABC -tABC -uABC -v ]" % sys.argv[0])
    print( " where; -")
    print( "   -cABC            specify category to search; e.g. Subject, To, From, Body")
    print( "   -D or --debug    prints out Debug information")
    print( "   -fABC.DEF        specify configuration json file")
    print( "   -h or --help     outputs this usage message")
    print( "   -mABC            specify name of mailbox; e.g. Inbox, Sent")
    print( "   -pABC            specify login password")
    print( "   -Pxyz            specify IMAP port number; e.g 993, 143")
    print( "   -sABC            specify IMAP server name or IP address; e.g. imap.gmail.com")
    print( "   -tABC            specify term to search with")
    print( "   -uABC            specify user account name")
    print( "   -v or --verbose  prints verbose output")
#    print( "   -wX.X            wait X.X sec instead of default 2 sec before timing-out")
    print( " E.g.; -")
    print( "   ", sys.argv[0], " -v -s imap.gmail.com -u ozzie193 -m Inbox -c From -t mrcat84")


def processCommandLine():
    try:
        opts, args = getopt.getopt(
            sys.argv[1:],
            "c:Df:hm:p:P:s:t:u:vw:",
            [
                "",
                "debug",
                "",
                "help",
                "",
                "",
                "",
                "",
                "",
                "",
                "verbose",
                "",
            ],
        )
    except getopt.GetoptError as err:
        print( str(err))
        usage()
        sys.exit()
    for o, a in opts:
        if o in ("-c", "--category"):
            options["category"] = a
        elif o in ("-D", "--debug"):
            options["debug"] = True
        elif o in ("-f", "--file"):
            options["file"] = a
        elif o in ("-h", "--help"):
            options["help"] = True
        elif o in ("-m", "--mailbox"):
            options["mailbox"] = a
        elif o in ("-p", "--password"):
            options["password"] = a
        elif o in ("-P", "--port"):
            options["port"] = a
        elif o in ("-s", "--server"):
            options["server"] = a
        elif o in ("-t", "--term"):
            options["term"] = a
        elif o in ("-u", "--user"):
            options["user"] = a
        elif o in ("-v", "--verbose"):
            options["verbose"] = True
        elif o in "-w":
            options["wait"] = float(a)
            if options["wait"] < 0.0:
                options["wait"] = 0.0
    if options["debug"]:
        options["verbose"] = True  # Debug implies verbose output
    return args


def getEmailText( optionList, debugFlag ):
    # Define the email user name
    user = optionList["user"]
    # Define the email user passwd
    password = optionList["password"]
    # Define Server name for IMAP connection
    imapServer = optionList["server"]
    # Define Server port for IMAP connection
    imapPort = optionList["port"]
    # Define the mailbox for IMAP connection
    mbox = optionList["mailbox"]
    # Define search category IMAP connection
    category = optionList["category"]
    # Define search term for IMAP connection
    term = optionList["term"]
    # Setup default port if none specified
    if imapPort == "":
        imapPort = "993"
    # Setup default search for emails from the current day
    # searching the inbox for datestamp containing
    # todays date.
    if mbox == "":
        mbox = "Inbox"
#    if category == "":
#        category = 'ALL'
#    if term == "":
#        now = datetime.now()			# current date and time
#        term = "\"" + "\\" + "\"" + now.strftime("%d %b %Y") + "\\" + "\"" + "\""	# DayOfMonth Month Year
    #
    if debugFlag:
        print( 'User: "%s"; Password: "%s"' % ( user, password))
        print( 'Server: "%s"; Port: "%s"' % ( imapServer, imapPort))
        print( 'MailBox: "%s"; category: "%s"; Term: "%s"' % ( mbox, category, term))
        print()
    #
    # Login then get the EMail Texts IMAP Server
    getIMAP_AccountEmailText( imapServer, imapPort, user, password, mbox, category, term, debugFlag )


def main():
    #
    # Handle any config details specified in the command line
    # Set global options from information that maybe in the command line
    args = processCommandLine()
    #
    # If help is requested in the command line then print them & exit
    if options["help"]:
        usage()
        exit(0)
    #
    # Print out the options if the Debug option has been set
    if options["debug"]:
        printOutAllTheOptions()
        print()
    #
    # If command line options have at least the server and user specified
    # then try to get the password if it hasn't already been specified
    if( options["server"] != "") and (options["user"] != ""):
        if options["password"] == "":
            promptStr = 'Enter ' + options["user"] + ' Password: '
            options["password"] = getpass.getpass( prompt=promptStr, stream=None )
        getEmailText( options, options["debug"] )
       
    # If command line options specify a json file then
    # Read config details from external json file
    if options["file"] != "":
        try:
            with open( options[ "file" ], "r" ) as f:
                configData = json.load(f)
        except (FileNotFoundError) as e:
            print(e, file=sys.stderr)
            exit()
        else:
        # If json file info has at least the server and user specified
        # then try to get the password if it wasn't specified
            if( configData[0]["server"] != "") and (configData[0]["user"] != "" ):
                if configData[0]["password"] == "":
                    promptStr = 'Enter ' + configData[0]["user"] + ' Password: '
                    configData[0]["password"] = getpass.getpass( prompt=promptStr, stream=None )
                getEmailText( configData[0], options["debug"] )

        
if __name__ == "__main__":
    main()

#! /usr/bin/python3
#
# G E T T E X T F R O M E M A I L S O N I M A P _ S E R V E R
#
# This script prints out text from emails to stdout
#
# Last Modified on Mon Aug 15 22:23:05 2022
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
# For Search keys other than Subject: https://gist.github.com/martinrusev/6121028#file-imap-search
#
import sys
import imaplib
import email
import json  #Load config from a json format file
from datetime import datetime
import sys  # sys.argv
import getopt  # getopt()
#
options = {
    "debug": False,
    "file" : "getTextFromEmailsOnIMAP_Server.json",
    "help": False,
    "verbose": False,
    "wait": float(2),
}
# Set up dummy configuration data, but expect
# actual config to be read-in from a json file
configData = [
  {
    "user" : "localuser",
    "password" : "",
    "url" : "localhost",
    "port" : "143",
    "mailbox" : "Inbox",
    "key" : "Subject",
    "value" : "Test"
  }
]
#
#
def usage():
    print( "Usage:\n%s [-DfA.BhvwX.X]" % sys.argv[0])
    print( " where; -")
    print( "   -D or --debug    prints out Debug information")
    print( "   -fABC.DEF        specify configuration in a json file")
    print( "   -h or --help     outputs this usage message")
    print( "   -v or --verbose  prints verbose output")
    print( "   -wX.X            wait X.X sec instead of default 2 sec before timing-out")
    print( " E.g.; -")
    print( "   ", sys.argv[0], " -v -w5")
#
#
def processCommandLine():
    try:
        opts, args = getopt.getopt(
            sys.argv[1:],
            "Df:hvw:",
            [
                "debug",
                "",
                "help",
                "verbose",
                "",
            ],
        )
    except getopt.GetoptError as err:
        print( str(err))
        usage()
        sys.exit()
    for o, a in opts:
        if o in ("-D", "--debug"):
            options["debug"] = True
        elif o in ("-f", "--file"):
            options["file"] = a
        elif o in ("-h", "--help"):
            options["help"] = True
        elif o in ("-v", "--verbose"):
            options["verbose"] = True
        elif o in "-w":
            options["wait"] = float(a)
            if options["wait"] < 0.0:
                options["wait"] = 0.0
    if options["debug"]:
        options["verbose"] = True  # Debug implies verbose output
    return args

def main():
    capabilitySet = {}
    args = processCommandLine()
    if options["help"]:
        usage()
        exit(0)
    #
    # Read config details from external json file
    try:
        with open( options[ "file" ], "r" ) as f:
            configData = json.load(f)
    except (FileNotFoundError) as e:
        print(e, file=sys.stderr)
    else:
        # 
        # Define the email user name and passwd
        user, password = configData[0]["user"], configData[0]["password"]
        # Define URL and port for IMAP connection
        imap_url, imap_port = configData[0]["url"], configData[0]["port"]
        # Define the mailbox for IMAP connection
        mbox = configData[0]["mailbox"]
        # Define search key and map for IMAP connection
        key, value = configData[0]["key"], configData[0]["value"]

    if len(user) == 0:
        print("?? User Account name is not specified?", file=sys.stderr)
        exit(1)
    if len(password) == 0:
        print("?? User Password is not specified?", file=sys.stderr)
        exit(2)
    # Setup default search for emails from the current day
    # searching the inbox for datestamp containing
    # todays date.
    if len(mbox) == 0:
        mbox = "Inbox"
    if len(key) == 0:
        key = "Date"
    if len(value) == 0:
        now = datetime.now()			# current date and time
        value = now.strftime("%Y-%m-%d")	# Year-Month-DayOfMonth

    # Establish connection with mail server using SSL if using port 933
    #  otherwise establish connetion and then establish SSL later
    try:
        if imap_port == "993":
            my_mail=imaplib.IMAP4_SSL( imap_url )
        else:
            my_mail=imaplib.IMAP4( imap_url, imap_port )
    except OSError as err:
        print("OS error: {0}".format(err), file=sys.stderr)
        print('?? Unable to connect to "%s" on port "%s"?' % ( imap_url, imap_port ), file=sys.stderr)
    else:
        # Show Protocol version if verbose output is selected
        response, data = my_mail.capability()
        if response == 'OK' :
            capabilitySet = set( str( data[0], 'utf-8' ).split())
            if options["verbose"]:
                print( 'Capabilility Set is: %s' % capabilitySet )
        else:
            print( '?? Capability response was: "%s"' % response, file=sys.stderr )
        if options["verbose"]:
            print( 'Server "%s" runs protocol version: "%s"' % ( imap_url, my_mail.PROTOCOL_VERSION ), file=sys.stderr)
            print( 'Capability response was: "%s"' % response, file=sys.stderr )
    # If port 143 and the server has the capability then do STARTTLS step
        if imap_port == "143":
            if "STARTTLS" in capabilitySet:
                response, data = my_mail.starttls()
                if options["verbose"]:
                    print( 'STARTTLS response was: "%s"' % response, file=sys.stderr )
            else:
                print( '? Port 143 in use, but no STARTTLS available: Connection is not encrypted' )
        try:
        # Log in using your credentials
            my_mail.login(user, password)
        except imaplib.IMAP4.error as err:
            print("imaplib.IMAP4.error: {0}".format(err), file=sys.stderr)
            print( '?? Login to server "%s" as "%s" failed?' % ( imap_url, user ), file=sys.stderr)
            exit( 3 )
        else:
            # Select the mailbox (read-only) from which to fetch messages
            response, data = my_mail.select( mbox, True)
            if response != 'OK' :
                print( 'Select response was: "%s"' % response, file=sys.stderr )
                print( '?? Select mailbox "%s" failed?' % mbox, file=sys.stderr )
            else:
                try:
                    response, data = my_mail.search(None, key, value)  #Search for emails with specific key and value
                except imaplib.IMAP4.error as err:
                    print("imaplib.IMAP4.error: {0}".format(err), file=sys.stderr)
                    print( '?? Search "%s" for "%s" failed?' % ( key, value ), file=sys.stderr)
                else:
                    if options["verbose"]:
                        print( 'Searching "%s" "%s" for "%s"' % ( mbox, key, value ), file=sys.stderr)
                    mail_id_list = data[0].split()  #IDs of all emails that we want to fetch 

                    msgs = [] # empty list to capture all messages
                    #Iterate through messages and extract data into the msgs list
                    for num in mail_id_list:
                        typ, data = my_mail.fetch(num, '(RFC822)') #RFC822 returns whole message (BODY fetches just body)
                        msgs.append(data)

                    #Unselect the mailbox with close as unselect() wasn't available
                    my_mail.close()

                    #Now we have all messages, but with a lot of details
                    #Let us extract the right text and print on the screen

                    #In a multipart e-mail, email.message.Message.get_payload() returns a 
                    # list with one item for each part. The easiest way is to walk the message 
                    # and get the payload on each part:
                    # https://stackoverflow.com/questions/1463074/how-can-i-get-an-email-messages-text-content-using-python

                    # NOTE that a Message object consists of headers and payloads.

                    cnt = 1
                    for msg in msgs[::-1]:
                        for response_part in msg:
                            if type(response_part) is tuple:
                                my_msg=email.message_from_bytes((response_part[1]))
                                print("_________________________________________________.#(%05d)#._________" % cnt )
                                cnt = cnt + 1
                                print ("subj:", my_msg['subject'])
                                print ("from:", my_msg['from'])
                                print ("date:", my_msg['date'])
                                print ("body:")
                                for part in my_msg.walk():  
                                    #print(part.get_content_type())
                                    if part.get_content_type() == 'text/plain':
                                        print (part.get_payload())

    #Logout of the server
    response, data = my_mail.logout()
    print("_________________________________________________.#(00000)#._________")
    if options["verbose"]:
        print( 'IMAP Server response to logout request was "%s"' % response, file=sys.stderr )

if __name__ == "__main__":
    main()

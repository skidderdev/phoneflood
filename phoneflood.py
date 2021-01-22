##    Hi there, this program was created by yukki!
##    Questions or problems, message me on twitter or discord
##    Twitter: @bojamhorsejack
##    Discord: yukki#0495
##    ver. 1.2
##    MAKE SURE YOU HAVE AN UPGRADED TWILIO ACCOUNT TO USE THIS PROGRAM!!!
##    also have a github account to use phone mode, OR just host the xml files yourself :]

import time, threading, json, os
from datetime import datetime
from tkinter import *
from tkinter import filedialog
from tkinter import simpledialog

#tries to import modules, if they aren't found then pip installs them
try:
    import github
    from twilio.rest import Client
except:
    import subprocess, sys
    import pip

    packages = ['twilio', 'PyGithub']

    for package in packages:
        print("Attempting to install packages")
        p = subprocess.call([sys.executable, "-m", "pip", "install", package, "--user", "--upgrade"])
        print(p)
        if p == 0:
            print("Installed {} Successfully.".format(package))
        else:
            print("There was an error with installing the package {}".format(package))
            input("Press Enter to exit...")
            exit()

#json check
try:
    with open('config.json', 'r') as read:
        config = json.load(read)
        account_sid = str(config['twil_sid']).strip("[']")
        auth_token = str(config['twil_auth']).strip("[']")
        git_auth = str(config['github_auth']).strip("[']")
        #print(account_sid, auth_token, git_auth)
except:
    sid = input('Enter your Twilio SID: ')
    auth = input('Enter your Twilio Auth: ')
    print("If you don't have a github token, create one here (enable GIST only!) https://github.com/settings/tokens")
    github_auth = input('Input a github token: ')

    with open('config.json', 'w+') as outfile:
        data = {}
        data['twil_sid'] = str(sid).strip('[]'),
        data['twil_auth'] = str(auth).strip('[]'),
        data['github_auth'] = str(github_auth).strip('[]')
        json.dump(data, outfile)

    with open('config.json', 'r') as handle:
        config = json.load(handle)
        account_sid = str(config['twil_sid']).strip("[']")
        auth_token = str(config['twil_auth']).strip("[']")
        git_auth = str(config['github_auth']).strip("[']")


#just some basic setup shit
mode = 'SMSMode' #sets default mode, you could change this, im not sure if it would break anything lol

while True:
    try:
        client = Client(account_sid, auth_token)
        phone_numbers = client.incoming_phone_numbers.list()
        break
    except:
        print('idk')
        sid = input('Enter your Twilio SID: ')
        auth = input('Enter your Twilio Auth: ')
        print("If you don't have a github token, create one here (enable GIST only!) https://github.com/settings/tokens")
        github_auth = input('Input a github token: ')

        with open('config.json', 'w') as outfile2:
            data = {}
            data['twil_sid'] = str(sid).strip('[]'),
            data['twil_auth'] = str(auth).strip('[]'),
            data['github_auth'] = str(github_auth).strip('[]')
            json.dump(data, outfile2)

        with open('config.json', 'r') as handle2:
            config = json.load(handle2)
            account_sid = str(config['twil_sid']).strip("[']")
            auth_token = str(config['twil_auth']).strip("[']")
            git_auth = str(config['github_auth']).strip("[']")

num_list = []

for x in phone_numbers:
    num_list.append(x.phone_number)

active_num_list = num_list

try:
    with open('gistlog.txt', 'r'):
        pass
except:
    with open('gistlog.txt', 'w'):
        pass

try:
    with open('recent_targets.txt', 'r'):
        pass
except:
    with open('recent_targets.txt', 'w'):
        pass
   
#tkinter root start

root = Tk()
root.lift()
big_font = ("Courier", 24, "bold")
num_choice = 0
text = ''
target = ''
activated = False

phoneFrame = LabelFrame(root, bg='#737373')
        
def make_gist():
    if mode == 'CallMode':
        global gist_url
        gh = github.Github(git_auth)
        gh_auth_user = gh.get_user()
        gist = gh_auth_user.create_gist(True, {"twiliosay.xml": github.InputFileContent('<?xml version="1.0" encoding="UTF-8"?><Response><Say>' + text_field.get() + '</Say></Response>')})
        gist_url = 'https://gist.githubusercontent.com/' + gh_auth_user.login + '/' + str(gist.id) + '/raw/twiliosay.xml'
        with open('gistlog.txt', 'a') as file:
            file.write(gist.id + '\n')

def log_target():
    global target
    if target == "Invalid":
        pass
    else:
        with open('recent_targets.txt', 'a') as recent:
            recent.write(target + ': ' + mode + ' ' + str(datetime.now()) + '\n')

#make message function necesary for telling Twilio to create the message
  
def make_message(number):
    message = client.messages.create(body=text_field.get(), from_=number, to=target_field.get())

def make_call(number):
    try:
        call = client.calls.create(
             to = target_field.get(),
             from_ = number,
             url = gist_url,
             method = "GET",
       )
        print('---------------------------------------------------------')
        print('Started call to %s from %s' % (target, number))
        print('---------------------------------------------------------')
    except Exception as err:
        print('Error making call from %s: %s' % (number, err))

def check_target():
    global slider_num
    if slider_num.get() == 0:
        print("Set slider amount")
        stop_attack()
    else:
        global target
        target = target_field.get()
        if len(target) == 10:
            target = "+1" + target
            activated = True
        elif len(target) == 11:
            target = "+" + target
            activated = True
        elif len(target) == 12:
            pass
            activated = True
        else:
            print('Target entered is invalid, enter a valid target...')
            target = "Invalid"
            stop_attack()

def batch():
    choose_nums = int(slider_num.get())
    amount = 3 * int(choose_nums)
    make_gist()
    log_target()
    while activated == True:
        if mode == 'SMSMode':
            for num in active_num_list[:choose_nums]:
                make_message(num)
                print('---------------------------------------------------------')
                print(str(choose_nums) + " message(s) sent to: " + str(target))
                print('Waiting ' + str(amount) + ' seconds...')
                print('---------------------------------------------------------')
                time.sleep(amount)
            
        elif mode == 'CallMode':
            print('Starting in 3 seconds...') 
            time.sleep(3) #buffer time for gist to create on github! /// will be switching over to twilio TwiML soon, because I just figured that out lol
            for num in active_num_list[:choose_nums]:
                make_call(num)
                time.sleep(1)

def start_button():
    global activated
    activated = True
    start.config(state=DISABLED)
    stop.config(state=NORMAL)
    check_target()
    threading.Thread(target=batch).start()

def stop_attack():
    global activated
    activated = False
    stop.config(state=DISABLED)
    start.config(state=NORMAL)

def set_sms_mode():
    global mode
    mode = 'SMSMode'
    sms_button.config(state=DISABLED)
    phone_button.config(state=NORMAL)
    mode_label.config(text=str(mode))
    print(mode)
    
def set_call_mode():
    global mode
    mode = 'CallMode'
    sms_button.config(state=NORMAL)
    phone_button.config(state=DISABLED)
    mode_label.config(text=str(mode))
    print(mode)
    
#tkinter start //// yes it's very unorganized ¯\_(ツ)_/¯

root.title('PhoneFlood --- Created by yukki :)')
screen_w = root.winfo_screenwidth()
screen_h = root.winfo_screenheight()
screen_w = screen_w / 2
screen_h = screen_h  / 2
screen_w = int(screen_w)
screen_h = int(screen_h)

#MENU START
my_menu = Menu(root)
root.config(menu=my_menu)

def stop_all():
    global activated
    if activated == False:
        print('No attacks to stop!')
    else:
        stop_attack()
        print('Totally stopped all your attacks :]')
    #meh I'll add this later, first need to add concurrent attacks into the program anyways :]]]

input_data = ''
sd = simpledialog

def change_auth():
    global auth_token
    input_data = sd.askstring(title='Change Twilio Auth', prompt='Please enter your Twilio Auth token')    
    with open('config.json', 'w') as file:
        data1 = {}
        data1['twil_sid'] = str(account_sid).strip('[]'),
        data1['twil_auth'] = str(input_data).strip('[]'),
        data1['github_auth'] = str(git_auth).strip('[]')
        auth_token = input_data
        json.dump(data1, file)

def change_sid():
    global account_sid
    input_data = sd.askstring(title='Change Account SID', prompt='Please enter your Twilio Account SID')    
    with open('config.json', 'w') as file:
        data2 = {}
        data2['twil_sid'] = str(input_data).strip('[]'),
        data2['twil_auth'] = str(auth_token).strip('[]'),
        data2['github_auth'] = str(git_auth).strip('[]')
        account_sid = input_data
        json.dump(data2, file)

def change_gist():
    global git_auth
    input_data = sd.askstring(title='Change Github Token', prompt='Please enter your Github token')    
    with open('config.json', 'w') as file:
        data3 = {}
        data3['twil_sid'] = str(account_sid).strip('[]'),
        data3['twil_auth'] = str(auth_token).strip('[]'),
        data3['github_auth'] = str(input_data).strip('[]')      
        git_auth = input_data        
        json.dump(data3, file)

def del_gists():
    gh = github.Github(git_auth)
    gh_auth_user = gh.get_user()
    gistlist = open('gistlog.txt', 'r').read().splitlines()
    for gist in gistlist:
        gh_gist = gh.get_gist(gist)
        gh_gist.delete()
    with open('gistlog.txt', 'w') as file:
        file.write('')

def clear_target_logs():
    with open('recent_targets.txt', 'w') as recent:
        recent.write('')

def print_info():
    print('---------------------------------------------------------')
    print('Account SID: ' + str(account_sid).strip('[]'))
    print('Auth Token: ' + str(auth_token).strip('[]'))
    print('Github Token: ' + str(git_auth).strip('[]'))
    print('---------------------------------------------------------')

def print_nums():
    print(active_num_list)

def clear_output():
    os.system('cls')
    
action_item = Menu(my_menu, tearoff=0)

my_menu.add_cascade(label='Actions', menu=action_item)
action_item.add_command(label='Stop all attacks', command=stop_all)
action_item.add_command(label='Delete all created gists', command=del_gists)
action_item.add_command(label='Clear target logs', command=clear_target_logs)
action_item.add_separator()
action_item.add_command(label='Exit', command=quit)

options_item = Menu(my_menu, tearoff=0)

my_menu.add_cascade(label='Options', menu=options_item)
options_item.add_command(label='Change Twilio Auth', command=change_auth)
options_item.add_command(label='Change Twilio SID', command=change_sid)
options_item.add_command(label='Change Github token', command=change_gist)
options_item.add_separator()
options_item.add_command(label='Print info to console', command=print_info)
options_item.add_command(label='Print active numbers', command=print_nums)
options_item.add_command(label='Clear output', command=clear_output)
#MENU END

inv_frame = LabelFrame(root, bg='#a6a6a6').pack(pady=5)

sms_button = Button(root, text='SMS Mode', command=set_sms_mode, bg='#a6a6a6')
phone_button = Button(root, text='Call Mode', command=set_call_mode, bg='#a6a6a6')

sms_button.config(state=DISABLED)

#slider section
def num_up():
    current = slider_num.get()
    slider_num.set(current + 1)

def num_down():
    current = slider_num.get()
    slider_num.set(current - 1)


#Recent target
def recent_popup():
    global target_field

    def choose_target():
        clicked_target("<Button-1>")
        target_field.insert(INSERT, str(listbox.get(ACTIVE)))
        popup.destroy()
    
    popup = Tk()
    popup.title('Recent Targets')
    popup.lift()
    popup.attributes('-topmost',True)
    listbox = Listbox(popup)
    popup.geometry('200x300')
    popup.resizable(width=False, height=False)
    label = Label(popup, text="Recent Targets")
    label.pack(side='top', fill='x', pady=10)
    button1 = Button(popup, text='Choose', command=choose_target)
    button2 = Button(popup, text='Cancel', command=popup.destroy)
   
    recents_list = []
    recent_targets_file = open('recent_targets.txt', 'r').read().splitlines()
    for line in recent_targets_file:
        if line[:12] not in recents_list:
            recents_list += [line[:12]]
        print(line[:12])

   # listbox.insert(END)

    for target in recents_list:
        listbox.insert(END, target)

    listbox.pack()
    button1.pack()
    button2.pack()
    popup.mainloop()
#end recent target

selected_numbers_list = []

#Choose amount of numbers to use
def numbers_popup():
    global num_list
    def choose_nums():
        global active_num_list
        global selected_numbers_list
        active_num_list = []
        selected_numbers_list = [listbox.get(i) for i in listbox.curselection()]
        active_num_list = selected_numbers_list
        slider_num.configure(to=len(active_num_list))
        popup.destroy()

    def choose_all():
        global active_num_list
        active_num_list = num_list
        slider_num.configure(to=len(active_num_list))
        popup.destroy()
    popup = Tk()
    popup.title('Twilio Numbers')
    popup.lift()
    popup.attributes('-topmost',True)
    yscrollbar = Scrollbar(popup) 
    yscrollbar.pack(side = RIGHT, fill = Y) 
    listbox = Listbox(popup, selectmode=MULTIPLE, yscrollcommand = yscrollbar.set)
    popup.geometry('250x300')
    popup.resizable(width=False, height=False)
    label = Label(popup, text='Choose Twilio numbers to use')
    label.pack(side='top', fill='x', pady=10)

    button1 = Button(popup, text='Choose', command=choose_nums)
    button2 = Button(popup, text='Choose all', command=choose_all)
    button3 = Button(popup, text='Cancel', command=popup.destroy)

    for num in num_list:
        listbox.insert(END, num)
        
    listbox.pack()
    button1.pack()
    button2.pack()
    button3.pack()
    popup.mainloop()

slider_frame = LabelFrame(root, bg='#a6a6a6')
slider_num = Scale(root, from_=0, to=len(active_num_list), orient=HORIZONTAL, bg='#a6a6a6')
slider_up = Button(slider_frame, text='>', command=num_up)
slider_down = Button(slider_frame, text='<', command=num_down)

recent_button = Button(slider_frame, text='Recent', command=recent_popup) #shh i dont want to rebuild the whole gui section so im just throwing this here shhhhh

#end slider section

root.configure(bg='#a6a6a6')
root.geometry(str(screen_w) + 'x' + str(screen_h))
root.resizable(width=False, height=False)
start = Button(phoneFrame, text='Start', command=start_button)
stop = Button(phoneFrame, text='Stop', command=stop_attack)
stop.config(state=DISABLED)
target_field = Entry(phoneFrame)
target_field.insert(0, 'Enter your target here')
text_field = Entry(phoneFrame)
text_field.insert(0, 'Enter your text here')
mode_label = Label(root, text=str(mode), font= big_font, bg = '#a6a6a6')
slider_label = Label(root, text='Choose how many Twilio numbers to use:', font=('Courier', 10, 'bold') , bg = '#a6a6a6')

number_button = Button(root, text='Choose Numbers to use', command=numbers_popup)

count1 = 0

def clicked_target(event):
    global count1
    if count1 < 1:
        target_field.delete(0, END)
        count1 +=1

count2 = 0
def clicked_text(event):
    global count2
    if count2 < 1:
        text_field.delete(0, END)
        count2 +=1

target_field.bind("<Button-1>", clicked_target)
text_field.bind("<Button-1>", clicked_text)

sms_button.pack()
phone_button.pack()
mode_label.pack()
target_field.pack(pady=5)
text_field.pack(pady=5)

slider_label.pack()
slider_num.pack(pady=5)
slider_frame.pack()
slider_down.grid(column='0', row='0')
slider_up.grid(column='1', row='0')
recent_button.grid(column='2', row='0')

number_button.pack(pady='6')

start.pack()
stop.pack()
phoneFrame.pack()
root.mainloop()

#end tkinter code                                                                                                                                                                                                                                                                           hi :)

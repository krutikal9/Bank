from PySimpleGUI.PySimpleGUI import Button, Window, popup_error
import mysql.connector
import PySimpleGUI as sg
import random
import hashlib
import string


mydb = mysql.connector.connect(
    host='localhost', user='root', passwd='Test', database='bank')
cursor = mydb.cursor()
print('done')

layout_home =[
    [sg.Button('Create account', key='-CREATE_ACC-')],
    [sg.Button('Login into account',key='-LOGIN-')],
    [sg.Button('Exit',key='-EXIT_MAIN-')]
]

layout_createuser =[
    [sg.Text('Name :',size=(10,1)),sg.Input("",key="-Name-",size=(15,1))],
    [sg.Text('Phone no:',size=(10,1)),sg.Input('',key='-PHONE_NO-',size=(10,1))],
    [sg.Text('Password :',size=(10,1)),sg.Input('',key='-PASSWORD-',size=(10,1))],
    [sg.Button('SAVE',key='-SAVE_C-'),sg.Button('Exit',key='-EXIT-')]
]   

layout_login =[
    [sg.Text('Account No :'), sg.Input('',key='-L_ACC-',size=(10,10))],
    [sg.Text('Password :'), sg.Input('',key='-PASSWORD_W-',size=(10,10),password_char='*')],
    [sg.Button('LOGIN',key='-LOGIN_USER-'),sg.Button('BACK',key='-BACK-')]

]

layout_tab1 =[
    [sg.T('Deposit Tab')],
    [sg.Text('Amount :',),sg.Input('',key='-DEPOSIT_A-',size=(10,1))],
    [sg.Button('Deposit',key='-SAVE_D-')]

]

layout_tab2 =[
    [sg.T('Withdraw Tab')],

    [sg.Text('Amount :'),sg.Input('',key='-WITHDRAW_A-',size=(10,1))],
    [sg.Button('Withdraw',key='-SAVE_W-')]
]

layout_tab3 =[
    [sg.T('Transfer Tab')],
    [sg.Text('Account No :',size=(10,1)),sg.Input('',key='-TRANSFER_AC-',size=(10,1))],
    [sg.Text('Amount :',size=(10,1)),sg.Input('',key='-TRANSFER_A-',size=(10,1))],
    [sg.Button('Transfer',key='-SAVE_T-')]
]

layout_logged =[
    [sg.Text('',key='-DATA-',size=(25,1))],
    [sg.Text('',key='-DATA1-',size=(25,1))],
    [sg.TabGroup(
        [
            [sg.Tab('Desposit',layout_tab1)],
            [sg.Tab('Withdraw',layout_tab2)],
            [sg.Tab('Transfer',layout_tab3)]
        ],
        size=(200,125)
    )],
    [sg.Button('LOGOUT',key='-EXIT1-')]
]

main_layout =[
    [sg.Column(layout_home,key="-COL1-",visible=True),
    sg.Column(layout_createuser,key="-COL2-",visible=False),
    sg.Column(layout_login,key="-COL3-",visible=False),
    sg.Column(layout_logged,key="-COL4-",visible=False)]
]        

def create_user():
    

    name = values['-Name-']
    p_no = int(values['-PHONE_NO-'])
    password =values['-PASSWORD-']
    
    cursor.execute('select max(account_no) from users')
    a_no = cursor.fetchone()
    if a_no:
        a_no = a_no[0] + 1
    else:
        a_no = 50000000 + 1
    try:
        cursor.execute(f"insert into users (name,phone_no,account_no,balance) values('{name}',{p_no},{a_no},0)")
        
        mydb.commit()
    except mysql.connector.errors.IntegrityError:
        
        popup_error('Mobile no already in use')
    
    salt_len =5
    salt ='';
    password1 =password
    random1 = string.ascii_letters + string.digits
    for i in range(salt_len):
        salt += random.choice(random1)
    
    hash_p = salt+password1
    hash_p= hash_p.encode('utf-8')
    sha = hashlib.sha256(hash_p)
    hash=sha.hexdigest()
    cursor.execute(f"insert into password (account_no,password,salt,hash) values({a_no},'{password}','{salt}','{hash}')")
    mydb.commit()


def getdata(acc_no):
    cursor.execute(f"select * from users where account_no={acc_no}")
    data = cursor.fetchone()
    return data

def validate(acc_no):
    cursor.execute(f"select salt,hash from password where account_no={acc_no}")
    sh = cursor.fetchone()
    return sh

def withdraw(data):
    amount = int(values['-WITHDRAW_A-'])
    if data[3] > amount:
        new_balance = data[3] - amount
        cursor.execute(
            f"update users set balance ={new_balance} where (account_no ={data[2]})")
        mydb.commit()
        data =getdata(data[2])
        window['-DATA-'].update(f'Name :{data[0]} | Phone : {data[1]} ')
        window['-DATA1-'].update(f'Balance :{data[3]} | Account No : {data[2]}')
        return data
        print('-----Withdrawal completed !!-----')
    else:
        popup_error('Not enough balance')


def deposit(data):
    amount = int(values['-DEPOSIT_A-'])
    new_balance = data[3] + amount
    cursor.execute(
        f"update users set balance ={new_balance} where (account_no ={data[2]})")
    mydb.commit()
    data =getdata(data[2])
    window['-DATA-'].update(f'Name :{data[0]} | Phone : {data[1]} ')
    window['-DATA1-'].update(f'Balance :{data[3]} | Account No : {data[2]}')
    return data
    print('-----Amount Deposited !!-----')


def transaction(data):
    t_ac_no = int(values['-TRANSFER_AC-'])
    
    other_data = getdata(t_ac_no)
    if other_data:
        amount = int(values['-TRANSFER_A-'])
        if data[3] > amount:
            new_balance = data[3] - amount
            cursor.execute(
                f"update users set balance ={new_balance} where (account_no ={data[2]})")
            current_balance = other_data[3] + amount
            cursor.execute(
                f"update users set balance ={current_balance} where (account_no ={t_ac_no})")
            mydb.commit()
            data =getdata(data[2])
            window['-DATA-'].update(f'Name :{data[0]} | Phone : {data[1]} ')
            window['-DATA1-'].update(f'Balance :{data[3]} | Account No : {data[2]}')
            print('-----Transaction completed !!-----')
            return data
        else:
            popup_error('You dont have enough balance')

    else:
        popup_error('Account does not exist')


def session():
    acc_no = int(values['-L_ACC-'])
    data = getdata(acc_no)
    sh =validate(acc_no)
    print(sh)
    # print(sh[0])
    print(values['-PASSWORD_W-'])
    print(data)
    if data :
        # e_password = values['-PASSWORD_W-']
        hash1 = sh[0]+ values['-PASSWORD_W-']
        hash1= hash1.encode('utf-8')
        print(hash1)
        sha = hashlib.sha256(hash1)
        hash=sha.hexdigest()
        print(hash)
        if hash == sh[1]:
            window['-COL1-'].update(visible=False)
            window['-COL2-'].update(visible=False)
            window['-COL3-'].update(visible=False)
            window['-COL4-'].update(visible=True)
            window['-DATA-'].update(f'Name :{data[0]} | Phone : {data[1]} ')
            window['-DATA1-'].update(f'Balance :{data[3]} | Account No : {data[2]}')
            return data  
        else :
            popup_error('Password in correct !!')     
    else:
        popup_error("User not found")

window =sg.Window("Wellcom to Bank !! ",main_layout)
while True:
    event ,values =window.read()
    print(event)
    print(values)
    if event == sg.WIN_CLOSED:
        break
    
    if event == '-CREATE_ACC-':
        window['-COL1-'].update(visible=False)
        window['-COL3-'].update(visible=False)
        window['-COL2-'].update(visible=True)
        window['-COL4-'].update(visible=False)
    
    if event == '-SAVE_C-':
        create_user()

    if event == '-LOGIN-':
        window['-COL1-'].update(visible=False)
        window['-COL2-'].update(visible=False)
        window['-COL3-'].update(visible=True)
        window['-COL4-'].update(visible=False)

    if event == '-LOGIN_USER-':
        data =session()
    if event in ('-EXIT1-', '-EXIT-','-BACK-') :
        window['-COL1-'].update(visible=True)
        window['-COL2-'].update(visible=False)
        window['-COL3-'].update(visible=False)
        window['-COL4-'].update(visible=False)

    if event == '-SAVE_D-':
        data = deposit(data)
    if event == '-SAVE_W-':
        data = withdraw(data)

    if event == '-SAVE_T-':
        data = transaction(data)

    

        


# user account -name , p_no, bal=0
# a_no - class variable
# withdraw
# deposit

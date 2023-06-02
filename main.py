"""

This is Divar leacher Coded by Arash Mohammadi at 4/21/23

"""

import os
import logging
import sqlite3
import requests
import uuid

from PyQt6.QtWidgets import QApplication, QMainWindow ,QPushButton , QLineEdit , QTextEdit , QComboBox , QMessageBox , QGroupBox , QVBoxLayout , QWidget , QLabel , QToolButton,QFileDialog
from PyQt6 import uic
from PyQt6.QtGui import QIntValidator


logging.basicConfig(format='[%(name)s] %(message)s',level=logging.INFO)

logger = logging.getLogger('Divar Leacher')

accounts = dict()

db = sqlite3.connect('datas.session')

cursor = db.cursor()

def add_account_to_sql(phone,token):
    
    cursor.execute('INSERT INTO accounts VALUES (?,?,?)',(token,str(accounts[phone]['uuid']),int(phone),))
    
    db.commit()
    
    return True

def delete_account(phone):
    
    cursor.execute('DELETE FROM accounts WHERE phone = ?;',(int(phone),))
    
    db.commit()
    
    return True

def send_code(phone):
    
    _uuid = uuid.uuid4()
    
    accounts[phone] = {'uuid' : _uuid}
    
    # Request data
    url = "https://api.divar.ir/v8/auth/authenticate"
    headers = {
        "Host": "api.divar.ir",
        "Content-Type": "application/octet-stream",
        "X-API-VERSION": "8057",
        "X-CITY": "1",
        "X-STANDARD-DIVAR-ERROR": "true",
        "Connection": "keep-alive",
        "Accept": "application/octet-stream",
        "User-Agent": f"5255|0|iOS16.4|fa|{_uuid}|iPhone",
        "Accept-Language": "fa;q=1.0",
        "Accept-Encoding": "br;q=1.0, gzip;q=0.9, deflate;q=0.8"
    }
    payload = f"\n\x0b{phone}"

    # Send request using requests.post()
    response = requests.post(url, headers=headers, data=payload)
    
    return response.text == '\x08\x01'

def login_account(phone,code):
    
    # Request data
    url = "https://api.divar.ir/v8/auth/confirm"
    headers = {
        "Host": "api.divar.ir",
        "Content-Type": "application/octet-stream",
        "X-API-VERSION": "8057",
        "X-CITY": "1",
        "X-STANDARD-DIVAR-ERROR": "true",
        "Connection": "keep-alive",
        "Accept": "application/octet-stream",
        "User-Agent": f"5255|0|iOS16.4|fa|{accounts[phone]}|iPhone",
        "Accept-Language": "fa;q=1.0",
        "Accept-Encoding": "br;q=1.0, gzip;q=0.9, deflate;q=0.8",
        "Content-Length": "21"
    }
    payload = f"\n\x0b{phone}\x12\x06{code}"

    # Send request using requests.post()
    response = requests.post(url, headers=headers, data=payload)

    # Print response
    if 'GrpcValidationError' not in response.text:
        
        add_account_to_sql(phone,response.text.encode())
        
        return True
    
    else:
        
        return False


class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        Form, _ = uic.loadUiType("divar.ui")
        self.ui = Form()
        self.ui.setupUi(self)
        self.setWindowTitle("Divar Leacher")
        
        self.widget_functions = {
            "phone": [QLineEdit, self.func1],
            "code": [QLineEdit, self.func2],
            "send" : [QPushButton , self.func3],
            "myphones" : [QComboBox , self.func4],
            "Delete" : [QPushButton , self.func5],
            "accounts" : [QGroupBox , None],
            "allaccounts" : [QLabel, None],
            "restricted" : [QLabel, None],
            "nonlimit" : [QLabel, None],
            "filters" : [QGroupBox, None],
            "start" : [QPushButton , self.func12],
            "browse" : [QToolButton , self.func13],
            "pathb" : [QLabel , None],
            
        }

        self.widgets = {}
        self.init_ui()
        
        self.directory_path = ''

    def init_ui(self):
        for widget_name, (widget_type, widget_func) in self.widget_functions.items():
            widget = getattr(self.ui, widget_name)  # Access widget from self.ui
            self.widgets[widget_name] = widget
            setattr(self, widget_name, widget)
            widget.setEnabled(True)  # Enable the widget
            if isinstance(widget, QLineEdit):
                widget.textChanged.connect(widget_func)
            elif isinstance(widget, QPushButton):
                widget.clicked.connect(widget_func)
            elif isinstance(widget, QComboBox):
                widget.currentTextChanged.connect(widget_func)
            elif isinstance(widget, QLabel):
                # QLabel doesn't emit signals, so we can't connect a signal to it.
                # You can directly access and modify its properties in the function.
                pass
            elif isinstance(widget, QToolButton):
                widget.clicked.connect(widget_func)

                    
    def load_accounts(self):
        
        self.code.setText('')
        
        all_accounts = cursor.execute('SELECT * FROM accounts;')
        
        all_accounts = all_accounts.fetchall()
        
        if all_accounts:
            
            self.widgets['filters'].setEnabled(True)
            
            self.start.setEnabled(True)
            
            self.widgets['allaccounts'].setText(f'All Accounts : {len(all_accounts)}')
            
            self.widgets['restricted'].setText(f'Restricted Accounts : {len(all_accounts)}')
            
            self.widgets['nonlimit'].setText(f'Non-Limit Accounts : {len(all_accounts)}')
            
            self.widgets['myphones'].clear()
            
            self.widgets['accounts'].setEnabled(True)
            
            for token , uuid , phone in all_accounts:
                
                self.widgets['myphones'].addItem(str(phone))
                
        else:
            
            self.widgets['accounts'].setEnabled(False)
            
    def func1(self,text):
        
        if not text.isdigit():
            
            self.phone.setText(text[:-1])
             
    def func2(self,text):
        
        if not text.isdigit():
            
            self.phone.setText(text[:-1]) 
        
    def func3(self):
        
        if self.send.text() == 'Send Code':
        
            phone = self.phone.text()
            
            if phone and len(phone) == 11:
            
                self.setWindowTitle("Sending Code ...") 
                
                result = send_code(phone)
                
                if result:
                    
                    self.setWindowTitle("Code Sent.") 
                    
                    QMessageBox.information(self, "Code Sent.", "Code sent to your phone number successfully.")
                    
                    self.code.setEnabled(True)
                    
                    self.phone.setEnabled(False)
                    
                    self.send.setText("Login")
                
            else:
                
                QMessageBox.information(self, "Phone Number", "Please enter phone number first.")
                
        else:
            
            code = self.code.text()
            
            if code and len(code) == 6:
            
                self.setWindowTitle("Please Wait ...") 
                
                result = login_account(self.phone.text(),code)
                
                if result:
                    
                    self.code.setEnabled(False)
                    
                    self.phone.setEnabled(True)
                    
                    self.send.setText("Send Code")
                    
                    self.phone.setText('') 
                    
                    self.code.setText('')
                    
                    self.load_accounts()
                    
                    QMessageBox.information(self, "Success", f"Account {self.phone.text()} Added To database.")
                    
                else:
                    
                    QMessageBox.warning(self, "Code wrong", "Code is wrong !")
            
            else:
                
                QMessageBox.information(self, "Code missing", "Please enter the code first.")
                
    def func4(self,phone):
        
        logger.info(phone)
        
    def func5(self):
        
        phone = self.widgets['myphones'].currentText()
        
        delete_account(phone)
        
        self.load_accounts()
        
        QMessageBox.information(self, "Account Deleted", f"Account {phone} Deleted Successfully.")
        
    def func12(self):
        
        if self.directory_path:
            
            pass
        
        else:
            
            QMessageBox.information(self, "Select folder", f"Please select folder for output files.")
        
    def func13(self):
        
        file_dialog = QFileDialog()
        
        directory_path = file_dialog.getExistingDirectory(self, "Select Directory")
        
        if directory_path:
            
            self.directory_path = directory_path
            
            self.widgets['pathb'].setText(f'.../{"/".join(directory_path.split("/")[-2:])}')
                

def main():
    
    logger.info('Application Started !')
    
    try:
        
        cursor.execute('CREATE TABLE IF NOT EXISTS accounts (token BLOB , uuid TEXT , phone INTEGER)')
        
        db.commit()
        
    except:
        
        logger.debug('Table Already Exists.')
    
    if not os.path.exists('functions'):
        
        logger.info('Functions are missing.')
        
        exit()
    
    for _dir in ['functions','outputs']:
        
        if not os.path.exists(_dir):
            
            os.mkdir(_dir)
            
    logger.info('Plugins Loaded Successfully.')
    
if __name__ == "__main__":
    main()
    app = QApplication([])
    window = MyWindow()
    window.load_accounts()
    window.show()
    app.exec()
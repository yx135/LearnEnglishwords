import streamlit as st
import logging
import toml
import subprocess
import os
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


# 获取script.py所在的绝对路径
#script_dir = os.path.dirname(os.path.abspath(__file__))

# 获取secrets.toml的绝对路径
#secrets_path = os.path.join(script_dir, '../secrets.toml')

# 加载文件
#secrets = toml.load(secrets_path)
#mysql_config = secrets["connections"]["mysql"]
#host=mysql_config["host"]
#user=mysql_config["username"]
#password=mysql_config["password"]
#database=mysql_config["database"]
#port=mysql_config["port"]
path=os.path.dirname(os.path.abspath(__file__))
host=st.secrets.host,
user=st.secrets.user,
password=st.secrets.password,
database=st.secrets.database,
port=st.secrets.port

def backup_database(user, password, db_name, backup_path):
    try:
        # 构建备份命令
        command = f"mysqldump -u {user} -p{password} {db_name} > {os.path.join(backup_path, f'{db_name}_backup.sql')}"
        
        # 使用 subprocess 执行命令
        subprocess.run(command, shell=True, check=True)
        
        print(f"Backup completed successfully. Backup stored at {os.path.join(backup_path, f'{db_name}_backup.sql')}")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred: {str(e)}")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")


def download_mysql_database():
        backup_database(user=user, password=password, db_name=database, backup_path=path)
        with open(os.path.join(path, f'{database}_backup.sql'), 'rb') as f:
            st.download_button(
                'Download  Database',
                f.read(),
                #file_name=f'{database}_backup.sql',
                mime='application/octet-stream'
            )

def upload_sqlite_database(uploaded_file):
    pass

def url_key():
    with st.form(key='url_key_form'):
        with open('key.txt', 'r') as f:
            st.session_state.base_url = f.readline().strip()  # 读取第一行并去除可能的前后空格或换行
            st.session_state.key = f.readline().strip() 
            st.session_state.model=f.readline().strip()
        base_url = st.text_input("Base URL:", st.session_state.get('base_url'))
        key = st.text_input("Key:", st.session_state.get('key'))
        modle=st.text_input("model",st.session_state.get('model'))
        
        if st.form_submit_button('确认'):
            logging.info(f'''button click: 确认''')
            st.session_state.base_url = base_url
            st.session_state.key = key
            st.session_state.modle=modle
            st.session_state.show_message = True
            logging.info(f'''date设置的Base URL是: {st.session_state.get("base_url")}''')
            logging.info(f'''date设置的Key是: {st.session_state.get("key")}''')
            logging.info(f'''date设置的model是:{st.session_state.get("model")}''')
            with open('key.txt', 'w') as f:
                f.write(st.session_state.get('base_url'))
                f.write('\n')
                f.write(st.session_state.get('key'))  
                f.write('\n')
                f.writte(st.session_state.get('model'))
     
def check_password(pw):
    return pw == 'hi'

# 初始化session_state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# 密码验证部分
if not  st.session_state.authenticated:
    password = st.text_input("请输入密码:", type='password')
    if st.button('验证'):
        if check_password(password):
            st.session_state.authenticated = True
            st.success('密码验证成功')
        else:
            st.error('密码错误')

# 如果密码验证成功，显示主应用
if st.session_state.authenticated:
    st.header('Download SQLite Database')
    #download_mysql_database()
    st.header('Upload SQLite Database')
    uploaded_file = st.file_uploader('Select a SQLite database file', type=['db'])
    if uploaded_file:
        upload_sqlite_database(uploaded_file)
    url_key()
    logging.info(f'{st.session_state.get("show_message")}')
    if st.session_state.get("show_message"):
        st.write(f'设置的Base URL是: {st.session_state.get("base_url")}')
        st.write(f'设置的Key是: {st.session_state.get("key")}')
        st.write(f'设置的model是:{st.session_state.get("modle")}')

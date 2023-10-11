import streamlit as st
import action
import models
import logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


with open('key.txt', 'r') as f:
    st.session_state.base_url = f.readline().strip()  # 读取第一行并去除可能的前后空格或换行
    st.session_state.key = f.readline().strip() 
    st.session_state.model=f.readline().strip()
#models.setup_database()
st.sidebar.markdown("# 首页 🎈")
logging.info(f"首页openaiapi-url: {st.session_state.base_url}")
logging.info(f"首页openaiapi-key: {st.session_state.key}")
logging.info(f"首页openaiapi-modle: {st.session_state.model}")


placeholder = st.empty()
wordlist = models.get_all_words()
placeholder.header(f'welcome! you have lenarned {len(models.get_all_words())} words')

# 获取用户输入
word = st.text_input('请输入单词:')
user_input = word


if user_input=='':
    pass
else:
    #word=""
    #st.experimental_rerun()
    print(user_input)
    example=action.process_word(user_input)
    logging.info(f'''首页获取的example：{example}''')
    st.title(user_input)
    st.text(f'''词频:{example.get('frequency')}''')
    st.caption('中文：')
    st.subheader(f'''{example.get('chinese_translation')}''')
    st.caption('例句：')
    st.subheader(f'''{example.get('example_sentence')}''')
    roots=example.get('roots')
    print(roots)
    if not roots:
        st.write('没有词根')
    else:
        st.caption('词根：')
        for root in roots:
            st.subheader(f'''{root.get('text')+'    '+root.get('chinese_translation')}''')
    prefixes=example.get('prefixes')
    if not prefixes:
        st.write('没有词前缀')
    else:
        st.caption('前缀：')
        for prefix in prefixes:
            st.subheader(f'''{prefix.get('text')+'    '+prefix.get('chinese_translation')}''')
    suffixes=example.get('suffixes')
    if not suffixes:
        st.write('没有词后缀')
    else:
        st.caption('后缀：')
        for suffix in suffixes:
            st.subheader(f'''{suffix.get('text')+'    '+suffix.get('chinese_translation')}''')
    wordlist = models.get_all_words()
    placeholder.header(f'welcome! you have lenarned {len(models.get_all_words())} words')

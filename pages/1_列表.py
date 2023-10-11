import streamlit as st
import models
import logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# 常量
ITEMS_PER_PAGE = 9
# 初始化
st.sidebar.markdown("# 列表 ❄️")
wordlist = models.get_all_words()
wordlist.reverse()
total_items = len(wordlist)
if total_items == 0:
    st.subheader("。。。。。。还没有学习词汇")
else:
    #
    total_pages = -(-total_items //ITEMS_PER_PAGE)  # 使用两个负号进行向上取整

    # 分页
    page = st.session_state.get('page',0)
    logging.info('列表：初始化时page：{}'.format(page))
    start_index = page * ITEMS_PER_PAGE
    end_index = start_index + ITEMS_PER_PAGE
    st.session_state.current_page_wordlist = wordlist[start_index:end_index]

    # 初始数据
    if wordlist not in st.session_state:
        st.session_state.data = wordlist
        st.title("  all Words  ❄️：  "+str(len(wordlist)))
    st.write(f"当前页： {page + 1}/{total_pages}")

    # 用于删除特定单词的函数
    def remove_word(word):
        models.delete_word(word=word)


    # 显示单词列表、链接和删除按钮
    for entry in st.session_state.current_page_wordlist:
        if entry['word']:
            col1, col2 = st.columns(2)
            with col1:
                if st.button(entry['word']):
                    # 将选择的单词存储在session_state中
                    st.session_state.selected_word = entry['word']
                    with st.expander('详细信息'):
                        #st.write('这里是详细信息')
                        if 'selected_word' in st.session_state:
                            selected_data = next((item for item in wordlist if item['word'] == st.session_state.selected_word), None)
                            if selected_data:
                                st.write(f"Details for: {selected_data['word']}")
                                example=models.get_word_details(selected_data['word'])
                                print(example)
                                st.write(f'''译文:\n{example.get('chinese_translation')}''')
                                st.write(f'''例句:\n{example.get('example_sentence')}''')
                                roots=example.get('roots')
                                if not roots:
                                    st.write('没有词根')
                                else:
                                    for root in roots:
                                        st.write(f'''词根： {root.get('text')+'   '+root.get('chinese_translation')}''')
                                prefixes=example.get('prefixes')
                                if not prefixes:
                                    st.write('没有词前缀')
                                else:
                                    for prefix in prefixes:
                                        st.write(f'''前缀： {prefix.get('text')+'   '+prefix.get('chinese_translation')}''')
                                suffixes=example.get('suffixes')
                                if not suffixes:
                                    st.write('没有词后缀')
                                else:
                                    for suffix in suffixes:
                                        st.write(f'''后缀： {suffix.get('text')+'   '+suffix.get('chinese_translation')}''')
                                st.write(f'''词频:{example.get('frequency')}''')
        
            with col2:
                if st.button(f"Delete {entry['word']}"):
                    remove_word(entry['word'])
                    st.experimental_rerun()

    # 创建一个空行来区分数据和翻页按钮
    st.write("")
    # 创建四个列，这里假设我们需要它们的宽度大致相等
    col_prev,col_go, col_next = st.columns([1,3,1])

    with col_prev:
        if page > 0:
            if st.button('上一页'):
                st.session_state.page = page - 1
                st.experimental_rerun()

    # 跳转到指定页功能
    with col_go:
        col_input, col_button = st.columns([2, 2])  # 您可以调整这些数字以更改列的宽度比例
        with col_input:
            specific_page = st.number_input('', min_value=1, max_value=total_pages, step=1)
        with col_button:
            st.write("", style="margin-top: 100%;") 
            if st.button('Go'):
                st.session_state.page = specific_page - 1
                st.experimental_rerun()


    with col_next:  
        if len(wordlist) > end_index:   
            if st.button('下一页'):
                st.session_state.page = page + 1
                st.experimental_rerun()

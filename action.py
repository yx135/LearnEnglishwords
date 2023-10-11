from models import  insert_word, insert_root_or_affix, link_word_to_ra, get_word_details,update_word,word_exit
from openaiapi import identify_roots_and_affixes
import logging
import json
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def process_word(word):
    if word_exit(word):
                logging.info(f'''word存在数据库中：{word}''')
                update_word(word)
                #details = get_word_details(word)
    else:
        # 从GPT API获取该单词的中文翻译、组成部分以及例句
        components =identify_roots_and_affixes(word)
        logging.info(f'action.py compenents: {components}')
        example_sentence = components.get('example_sentence', '')

        # 插入主要单词并获取其ID
        word_id = insert_word(word, "English", example_sentence, components["chinese_translation"])

        # 分别为前缀、词根和后缀插入记录，并建立与单词的关联
        for prefix in components["prefix"]:
            ra_id = insert_root_or_affix(prefix['text'], "prefix", prefix['chinese_translation'])
            link_word_to_ra(word_id, ra_id)

        for root in components["root"]:
            ra_id = insert_root_or_affix(root['text'], "root", root['chinese_translation'])
            link_word_to_ra(word_id, ra_id)

        for suffix in components["suffix"]:
            ra_id = insert_root_or_affix(suffix['text'], "suffix", suffix['chinese_translation'])
            link_word_to_ra(word_id, ra_id)

        # 返回该单词及其组成部分的详细信息
    details = get_word_details(word)
    logging.info(f'''数据库完成处理API接口数据：{details}''')

   # print(details)
    return details

"""
if __name__ == '__main__':
    setup_database()
    
    with open("word.txt", "r") as f:
        lines = f.readlines()
        stripped_lines = [line.strip() for line in lines]
        #print(stripped_lines)
        for word in stripped_lines:
            details = process_word(word)
            if details:
                print(f"Word: {details['word']}")
                print(f"Chinesetranslation: {details['chinese_translation']}")
                print(f"Example Sentence: {details['example_sentence']}")
                print(f"Roots: {details['roots']}")
                print(f"Prefixes: {details['prefixes']}")
                print(f"Suffixes: {details['suffixes']}")
                print(f"Frequency: {details['frequency']}")

"""


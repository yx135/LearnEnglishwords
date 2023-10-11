import openai
import streamlit as st
import logging
import json
logging.basicConfig(level=logging.INFO,

                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
'''
gpt={
    'url':'https://ai.fakeopen.com/v1',
    'key':'fk-imRhfDx5Q-w5pN9uNJ5D_gSauf1-T10qDqo85tDL41o'
}
if 'base_url' not in st.session_state:
        st.session_state.base_url =gpt.get('url')
if 'key' not in st.session_state:
        st.session_state.key = gpt.get('key')
'''



def identify_roots_and_affixes(word):
    openai.api_base=st.session_state.get('base_url')
    openai.api_key=st.session_state.get('key')
    modle=st.session_state.get('model')
    logging.info(f"openaiapi.py: {openai.api_base}")
    logging.info(f"openaiapi.py: {openai.api_key}")
    logging.info(f"openaiapi.py: {modle}")
    response = openai.ChatCompletion.create(
      model=modle,
      messages=[
          {"role": "system", "content": """You are a helpful assistant that identifies the root(s), prefix(es), and suffix(es) of given English words. Make sure to provide their definitions in English and ensure that prefixes and suffixes do not have special characters,like "-"" and "_"."""},
          {"role": "user", "content": f'''For the English word '{word}', please provide its Chinese translation, identify its components, and give an English example sentence in the  format : {{"word": word, "chinese_translation": chinese_translation, "example_sentence": english_example_sentence, "root": [{{"text": root_text, "chinese_translation": root_translation}}], "prefix": [{{"text": prefix_text, "chinese_translation": prefix_translation}}], "suffix": [{{"text": suffix_text, "chinese_translation": suffix_translation}}]}},Do not have any reply other than this!'''}
      ]
    )
    logging.info(f"api接口返回原始response:\n {response}")

    try :
        content_value = response['choices'][0]['message']['content']
        # 使用字符串方法找到 JSON 数据的开始和结束位置
        start_index = content_value.find("{")
        end_index = content_value.rfind("}") + 1  # 加 1 是为了包括最后的 "}"
        # 提取 JSON 数据
        json_str = content_value[start_index:end_index]
        logging.info(f"api接口response解析后数据:  {json_str}")
        return json.loads(json_str)
    except:
        logging.info(f"api接口response fail")
        return {"chinese_translation": "", "example_sentence": "", "root": [], "prefix": [], "suffix": []}


if __name__=='__main__':
    #print(openai.api_key)
    print(identify_roots_and_affixes("agriculture"))

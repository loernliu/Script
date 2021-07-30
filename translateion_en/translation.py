import os
import re


def generate_translate_dict():
    translate_dict = {}
    with open('C:/Users/lwp/Desktop/work/translateion_en/中英文对照词典.md', 'r', encoding='utf8') as f:
        while True:
            replace_str = f.readline().strip()
            if not replace_str:
                break
            replace_list = replace_str.split(':')
            ch_str = replace_list[0]
            en_str = replace_list[-1].replace("_", ' ')
            translate_dict[ch_str] = en_str

    return translate_dict


def replace_file_str(file_str):
    translate_dict = generate_translate_dict()
    new_file_str = file_str
    for i in translate_dict.items():
        ch_str, en_str = i[0], i[1]
        regex_str = r"{}".format(ch_str)
        new_file_str = re.sub(regex_str, en_str, new_file_str)

    return new_file_str


def find_file(src_path):
    items = os.listdir(src_path)
    for item in items:
        item = os.path.join(src_path, item)
        if os.path.isdir(item):
            find_file(item)
        try:
            last_name = os.path.splitext(item)[-1]
            if last_name == '.py' or last_name == '.yml':
                f = open(item, 'r', encoding='utf8')
                file_str = f.read()
                f.close()
                print(item)
                new_file_str = replace_file_str(file_str)
                f = open(item, 'w', encoding='utf8')
                f.write(new_file_str)
                f.close()

        except Exception as e:
            print(e)


if __name__ == "__main__":
    src_path = 'E:/gitee/el_app/src'
    find_file(src_path)

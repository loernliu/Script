import os
import platform

PIP_CONFIG = '''[global]
index-url = http://mirrors.aliyun.com/pypi/simple/
trusted-host=mirrors.aliyun.com
'''

def create_file():
    file_name = get_file_path()
    dirname = os.path.dirname(file_name)
    filename = os.path.basename(file_name)
    if os.path.isfile(file_name):
        back_name = filename + '.bak'
        if os.path.isfile(os.path.join(dirname, back_name)):
            os.remove(os.path.join(dirname, back_name))
        os.rename(file_name, os.path.join(dirname, back_name))
        print('生成配置文件备份 %s' % os.path.join(dirname, back_name))
    else:
        if not os.path.isdir(dirname):
            os.mkdir(dirname)
    with open(file_name, 'w', encoding='utf-8') as f:
        f.write(PIP_CONFIG)
    print('生成配置文件 %s' % file_name)


def get_file_path():
    user_dir = expanduser('~')
    SYSTEM = platform.system()
    print('当前系统类型是 %s' % SYSTEM)
    if SYSTEM.lower() == 'windows':
        config_basename = 'pip.ini'
        legacy_storage_dir = os.path.join(user_dir, 'pip')
    else:
        config_basename = 'pip.conf'
        legacy_storage_dir = os.path.join(user_dir, '.pip')
    legacy_config_file = os.path.join(
        legacy_storage_dir,
        config_basename,
    )
    return legacy_config_file


def expanduser(path):
    expanded = os.path.expanduser(path)
    if path.startswith('~/') and expanded.startswith('//'):
        expanded = expanded[1:]
    return expanded


if __name__ == '__main__':
    create_file()
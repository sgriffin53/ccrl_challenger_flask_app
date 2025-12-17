import requests
import ast

def get_release_date_and_lang(url):
    page = requests.get(url)
    text = page.text
    lines = text.split("\n")
    main_language = 'None'
    for line in lines:
        if "<span class=\"color-fg-default text-bold mr-1\">" in line:
            main_language = line.split("mr-1\">")[1].split("<")[0]
            #print(line.split("mr-1\">")[1].split("<")[0])
            print(main_language)
            break
    page = requests.get(url + "/releases")
    text = page.text
    f = open('test.html', 'w', encoding='utf-8')
    f.write(text)
    f.close()
    lines = text.split("\n")
    last_release = 'None'
    for line in lines:
        if 'datetime="' in line:
            last_release = line.split("datetime=\"")[1].split("\"")[0].split("T")[0]
            print(last_release)
            break
    return (main_language, last_release)


#get_release_date_and_lang('https://www.github.com/sgriffin53/raven')
#get_release_date_and_lang('https://github.com/Mauritz8/Vividmind')
f = open('engine_list_complete_new.txt', 'r', encoding='utf-8')
lines = f.readlines()
f.close()
new_lines = []
for line in lines:
    info = ast.literal_eval(line)
    github = info[1]
    print(github)
    value = get_release_date_and_lang(github)
    language = value[0]
    release_date = value[1]
    new_lines.append(str((info[0], info[1], info[2], info[3], info[4], language, release_date)))
f = open('engine_list_complete_new_with_RDandLang.txt', 'w', encoding='utf-8')
for line in new_lines:
    f.write(line + "\n")
f.close()
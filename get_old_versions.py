import requests
import time
import re
def get_engines():
    url = 'http://computerchess.org.uk/ccrl/404/cgi/compare_engines.cgi?class=Open+source+engines&print=Rating+list&print=Results+table&print=LOS+table&table_size=12&cross_tables_for_best_versions_only=1'
    page = requests.get(url)
    text = page.text
    lines = text.split("\n")
    engine_names = []
    engine_urls = []
    engines = []
    current_rank = 1
    current_rating = 0
    for line in lines:
        if '<td rowspan=2 class="number"' in line and "<b>" in line:
            rank = line.split("<b>")[1].split("</b>")[0].replace("&#8209;", "-")
            if rank[0].isdigit():
                current_rank = rank
        if "class=\"rating\"><b>" in line:
            current_rating = line.split('class="rating"><b>')[1].split("<")[0]
        if '<span class="oss">' in line:
            if 'href="' not in line: continue
            temp = line.split("href=\"")[1]
            engine_url = temp.split("\"")[0]
            engine_name = temp.split(">")[1].split("<")[0]
            if 'Open source' in engine_name: continue
            #print(line)
            if engine_name == 'Stock': continue
            if engine_name == 'Sto': continue
            if engine_name in engine_names: continue
            engine_names.append(engine_name)
            if engine_url in engine_urls: continue
            engine_urls.append(engine_url)

            #print(engine_name, engine_url)
            engines.append((engine_name, engine_url, current_rank, current_rating))
    #print(page.text)
    return engines

def get_new_engines(engines):
    f = open('engine_list_complete.txt','r',encoding='utf-8')
    lines = f.readlines()
    f.close()
    old_engines = []
    for line in lines:
        engine_name = line.split("\'")[1].split("\'")[0]
        old_engines.append(engine_name.split(" ")[0])
    new_engines = []
    for engine in engines:
        if engine[0].split(" ")[0] not in old_engines:
            new_engines.append(engine)
    return new_engines

def get_lowest_rated_version_old(engine):
    engine_url = engine[1]
    engine_name = engine[0]
    engine_url = 'https://computerchess.org.uk/ccrl/404/' + engine_url
    attempt = 0
    while attempt < 3:
        attempt += 1
        try:
            page = requests.get(engine_url)
        except:
            time.sleep(attempt ** 2)
    text = page.text
    lines = text.split("\n")
    comparison_url = ''
    for line in lines:
        #print(line)
        if "Compare them!" in line:
            comparison_url = line.split("href=\"")[1].split("\"")[0].replace("&amp;", "&")
            comparison_url = 'https://computerchess.org.uk/ccrl/404/' + comparison_url
            break
            #print(line)
    if comparison_url == '': return None
    return None

def get_lang(url):
    attempt = 0
    text = ''
    while attempt < 8:
        attempt += 1
        try:
            page = requests.get(url)
            text = page.text
            break
        except:
            time.sleep(attempt ** 2)
    lines = text.split("\n")
    main_language = 'None'
    for line in lines:
        if "<span class=\"color-fg-default text-bold mr-1\">" in line:
            main_language = line.split("mr-1\">")[1].split("<")[0]
            return main_language

def get_github_links(engines):
    all_links = []
    tried = 0
    tot_bytes = 0
    i = 0
    language = None
    for engine in engines:
        i += 1
        if i >= 10000000000000000: break
        tried += 1
        name = engine[0]
        url = engine[1]
        rank = engine[2]
        rating = engine[3]
     #   if "Raven" not in name: continue
        #if 'Lc0' not in name: continue
    #    if 'Velvet' not in name: continue
        print(engine)
        url = 'https://computerchess.org.uk/ccrl/404/cgi/' + url
        attempt = 0
        text = ''
        while attempt < 8:
            attempt += 1
            try:
                page = requests.get(url)
                text = page.text
                break
            except:
                time.sleep(attempt ** 2)
        lines = text.split("\n")
        author = ''
        do_break = False
        for line in lines:
            #print(line)
            #print(line)
            if 'Authors: ' in line:
                author = line.split("Authors: ")[1].strip()
            if 'Author: ' in line:
                author = line.split("Author: ")[1].strip()
            if "a href=\"https" in line or "a href=\"http" in line and "kirill" not in line:
                print(line)
                links = []
                if 'https' in line: links = line.split("a href=\"https")
                else: links = line.split("a href=\"http")
                #print(links[1])
                #return
             #   print(links)
                #print(line, "------", links)
                link = ''
                #print(links)
                for link in links:
                    link = link.split("\"")[0]
                    if 'Raven' in name: link = '://github.com/sgriffin53/raven'
                    if 'github' not in link: do_continue = True
                    else:
                        do_continue = False
                        break
                if do_continue: continue
                if link.count('/') > 4:
                    link = "/".join(link.split('/')[:5])
                link = 'https' + link
                print(link)
                language = get_lang(link)
                is_windows = check_for_windows(name, link)
                print(is_windows)
                if is_windows is None: continue
                if is_windows[0] is None: continue
                if len(is_windows[0]) == 0: continue
                release_date = is_windows[2]
                license = check_for_license(link)
                if not license: continue
                # is_windows returns (filenames (list), sizes (list))
                for size in is_windows[1]:
                    suffix = size.split(" ")[1]
                    size = size.split(" ")[0]
                    bytes = float(size)
                    if suffix == 'GB': bytes *= 1024 * 1024 * 1024
                    if suffix == 'MB': bytes *= 1024 * 1024
                    if suffix == 'KB': bytes *= 1024
                    #   print(size, suffix, bytes)
                    tot_bytes += bytes
                filenames = is_windows[0]
                # time.sleep(60)
                to_add = (name, link, author, rank, rating, filenames, release_date, language)
                print(to_add)
                if to_add not in all_links:
                    all_links.append(to_add)
                print(len(all_links), tried)
    return all_links


def check_for_license(orig_link):
    suffixes = ['/blob/master/LICENSE.md', '/blob/master/LICENSE', '/blob/master/LICENSE.txt']
    for suffix in suffixes:
        link = orig_link + suffix
        attempt = 0
        text = ''
        while attempt < 8:
            attempt += 1
            try:
                page = requests.get(link)
                text = page.text
                break
            except:
                time.sleep(attempt ** 2)
        lines = text.split("\n")
        found = False
        #print(text)
        if 'This is not the web page you are looking for' not in text and 'Not Found' not in text and 'File not found' not in text:
            if 'CC' not in text and 'Creative Commons' not in text and 'GPL' not in text and 'MIT' not in text: continue
            found = True
            print("Found license")
            return True
    link = orig_link
    attempt = 0
    while attempt < 8:
        attempt += 1
        try:
            page = requests.get(link)
            text = page.text
            break
        except:
            time.sleep(attempt ** 2)
    lines = text.split("\n")
    found = False
    # print(text)
    if 'This is not the web page you are looking for' not in text and 'Not Found' not in text and 'File not found' not in text:
        if 'license' in text.lower():
            if 'CC' not in text and 'Creative Commons' not in text and 'GPL' not in text and 'MIT' not in text: found = False
            else:
                found = True
            if found:
                print("Found license")
                return True
    print("No license")
    return False

def check_for_windows(name, link):
    #return ('test', 'test')
    filenames = []
    sizes = []
    last_added = False
    page_num = 0
    orig_link = link
    f = open('test.html', 'w', encoding='utf-8')
    for page_num in range(25):
        link = orig_link + '/releases?page=' + str(page_num)
        release_link = orig_link + '/releases'
        attempt = 0
        text = ''
        while attempt < 8:
            attempt += 1
            try:
                page = requests.get(link)
                text = page.text
                break
            except:
                time.sleep(attempt ** 2)
        #f.write(text.replace("</html>","<br>new page<br>"))
        lines = text.split("\n")
        current_release = None
        asset_url = None
        num_found = 0
        found = False
        release_date = ''
        for line in lines:
            #print(line)
            if '"Link--primary Link"' in line:
                num_found += 1
                current_release = line.split("Link\">")[1].split("<")[0]
                short_name = get_short_name(name)
                print(current_release, short_name)
                if short_name is None: continue
                match = False

                for word in current_release.split(" "):
                    if "-v" in word: word = word.split("-v")[1]
                  #  print(":::", word.replace("v",""), short_name.split(" ")[-1])
                    if word.replace("v", "").replace("V", "").startswith(short_name.split(" ")[-1]):
                        #print("---", word.replace(short_name.split(" ")[-1], "").replace(".","").replace("0",""))
                        if word.replace("v","").replace("V", "").replace(short_name.split(" ")[-1], "").replace(".","").replace("0","") == '':
                            match = True
                        break
                if match:
                    # matches the version we're looking for
                    print("found it:", current_release)
                    found = True
                    #asset_url = release_link + line.split("href=\"")[1].split("\"")[0].split("/releases")[1
                    #print(asset_url)
            if '<relative-time class="no-wrap" prefix="" datetime="' in line:
                release_date = line.split('datetime="')[1].split("\"")[0]
                #print(release_date)
            if found:
                if '<include-fragment loading="lazy"' in line:
                    asset_url = line.split('<include-fragment loading="lazy" src="')[1].split("\"")[0]
                    break
                   # return
        if asset_url is not None: break
        if num_found == 0: break
    if asset_url is None: return None
    link = asset_url
   # return
    attempt = 0
    text = ''
    while attempt < 8:
        attempt += 1
        try:
            page = requests.get(link)
            text = page.text
            break
        except:
            time.sleep(attempt ** 2)
    lines = text.split("\n")
    last_added = False
    for line in lines:
        if "a href=" in line and "/releases/download" in line:
            download_link = "/releases/download" + line.split("/releases/download")[1].split("\"")[0].split("<")[0]
            #print(line)
            filename = line.split("\"")[1]
            filename = filename.split("/")[-1]
            if ".zip" in filename.lower() or ".exe" in filename:
                last_added = True
                filenames.append((filename, download_link))
        if last_added and '<span style="white-space: nowrap;" data-view-component="true" class="color-fg-muted text-sm-left flex-auto ml-md-3">' in line:
            size = line.split(">")[1].split("<")[0]
            suffix = size.split(" ")[1]
            size = size.split(" ")[0]
            sizes.append(size + " " + suffix)
            last_added = False
    return (filenames, sizes, release_date)


def get_all_engines():
    url = 'http://computerchess.org.uk/ccrl/404/cgi/compare_engines.cgi?class=Open+source+engines&print=Rating+list&print=Results+table&print=LOS+table&table_size=12&cross_tables_for_best_versions_only=1'
    page = requests.get(url)
    text = page.text
    lines = text.split("\n")
    for line in lines:
        pass
    pass

def get_short_name(name):
    match = re.match(r"([\S]+(?:\s+\S+)*?)\s+(v?\d+\.\d+|v?\d+)", name)
    return f"{match.group(1)} {match.group(2)}" if match else None

start_time = time.time()
#print(get_short_name("Black Marlin 1.0 64-bit"))
engines = get_engines()
links = get_github_links(engines)
f = open('engine_list_all_versions_to_test.txt','w', encoding='utf-8')
#to_add = (name, link, author, rank, rating, filenames, release_date, language)
for link in links:
    name = link[0]
    github = link[1]
    author = link[2]
    rank = link[3]
    rating = link[4]
    filenames = link[5]
    release_date = link[6]
    language = link[7]
    f.write(str(link) + '\n')
f.close()


#for engine in engines:
#    print(engine[2], engine[3], engine[0], engine[1])
#print(check_for_windows('Obsidian 13.0 64-bit 8CPU', 'https://github.com/gab8192/Obsidian'))


#print(len(engines))
duration = round(time.time() - start_time, 2)
print("Time taken: ", duration)
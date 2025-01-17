import requests
import time
def get_engines():
    url = 'https://computerchess.org.uk/ccrl/404/index.html'
    page = requests.get(url)
    text = page.text
    lines = text.split("\n")
    engine_names = []
    engine_urls = []
    engines = []
    for line in lines:
        if '<span class="oss">' in line:
            if 'href="' not in line: continue
            temp = line.split("href=\"")[1]
            engine_url = temp.split("\"")[0]
            engine_name = temp.split(">")[1].split("<")[0]
            if 'Open source' in engine_name: continue
            #print(line)
            if engine_name == 'Stock': continue
            if engine_name in engine_names: continue
            engine_names.append(engine_name)
            if engine_url in engine_urls: continue
            engine_urls.append(engine_url)

            print(engine_name, engine_url)
            engines.append((engine_name, engine_url))
    #print(page.text)
    return engines

def get_github_links(engines):
    all_links = []
    tried = 0
    tot_bytes = 0
    for engine in engines:
        tried += 1
        engine_name = engine[0]
        engine_url = engine[1]
        engine_url = 'https://computerchess.org.uk/ccrl/404/' + engine_url
        page = requests.get(engine_url)
        text = page.text
        lines = text.split("\n")
        author = ''
        rating = 0
        do_break = False
        for line in lines:
            if '<td class="hrank">' in line:
                rating = line.split('<td class="hrank">')[1]
           #     print("r", rating)
                rating = rating.split("<")[0]
            #    print("g",rating)
                rating = rating.replace("&nbsp;"," ").replace("  "," ").strip()
                rating += ")"
                if ';' in rating:
                    rating = "#" + rating.split(";")[1]
                print(rating)
            if 'Authors: ' in line:
                author = line.split("Authors: ")[1].strip()
            if 'Author: ' in line:
                author = line.split("Author: ")[1].strip()
            if "a href=\"https" in line:
                links = line.split("a href=\"https")
                #print(line, "------", links)
                for link in links:
                    link = link.split("\"")[0]
                    if 'github' not in link: continue
                    if link.count('/') > 4:
                        link = "/".join(link.split('/')[:5])
                    link = 'https' + link
             #       print(link)
                    #is_linux = check_for_linux(link)
                    #is_linux = True
                    #if not is_linux: continue
                    is_windows = check_for_windows(link)
                    print(is_windows)
                    if len(is_windows[0]) == 0: continue
                    this_bytes = 0
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
                    #time.sleep(60)
                    to_add = (engine_name, link, author, rating)
                    if to_add not in all_links:
                        all_links.append(to_add)
                    print(all_links)
                    print(len(all_links), "/", tried)
                    tot_bytes += check_file_sizes(link)
                    print("Total size:", (tot_bytes / 1024 / 1024), "MB")
                    if len(all_links) > 5000000000000000:
                        do_break = True
                        break
        if do_break: break
    for engine in all_links:
        print(engine[0], "-", engine[3])

def check_for_license(orig_link):
    suffixes = ['/blob/master/LICENSE.md', '/blob/master/LICENSE', '/blob/master/LICENSE.txt']
    for suffix in suffixes:
        link = orig_link + suffix
        page = requests.get(link)
        text = page.text
        lines = text.split("\n")
        found = False
        #print(text)
        if 'This is not the web page you are looking for' not in text and 'Not Found' not in text and 'File not found' not in text:
            if 'CC' not in text and 'Creative Commons' not in text and 'GPL' not in text and 'MIT' not in text: continue
            found = True
            print("Found license")
            print(link)
            return True
    link = orig_link
    page = requests.get(link)
    text = page.text
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
                print(link)
                return True
    print("No license")
    return False

def check_file_sizes(link):
    link = link + '/releases'
    page = requests.get(link)
    text = page.text
    lines = text.split("\n")
    backup_link = ''
    for line in lines:
        if "<include-fragment loading=\"lazy\"" in line:
            if not backup_link:
                backup_link = line.split("lazy\" src=\"")[1].split("\"")[0]
        if '<span style="white-space: nowrap;" data-view-component="true" class="color-fg-muted text-sm-left flex-auto ml-md-3">' in line:
            size = line.split(">")[1].split("<")[0]
            suffix = size.split(" ")[1]
            size = size.split(" ")[0]
            bytes = float(size)
            if 'suffix' == 'GB': bytes *= 1024*1024*1024
            if 'suffix' == 'MB': bytes *= 1024*1024
            if 'suffix' == 'KB': bytes *= 1024
            return bytes
    #return False
    #print(backup_link)
    if not backup_link: return False
    link = backup_link
    page = requests.get(link)
    text = page.text
    lines = text.split("\n")
    for line in lines:
        if '<span style="white-space: nowrap;" data-view-component="true" class="color-fg-muted text-sm-left flex-auto ml-md-3">' in line:
            size = line.split(">")[1].split("<")[0]
            suffix = size.split(" ")[1]
            size = size.split(" ")[0]
            print(size)
            bytes = float(size)
            if 'suffix' == 'GB': bytes *= 1024*1024*1024
            if 'suffix' == 'MB': bytes *= 1024*1024
            if 'suffix' == 'KB': bytes *= 1024
            return bytes
    return 0

def check_for_windows(link):
    filenames = []
    sizes = []
    last_added = False
    link = link + '/releases'
    page = requests.get(link)
    text = page.text
    lines = text.split("\n")
    backup_link = ''
    for line in lines:
        if "<include-fragment loading=\"lazy\"" in line:
            if not backup_link:
                backup_link = line.split("lazy\" src=\"")[1].split("\"")[0]
        if "a href=" in line and "/releases/download" in line:
            #print(line)
            filename = line.split("\"")[1]
            print(filename)
            filename = filename.split("/")[-1]
            if ".7z" in filename.lower() or ".tar" in filename or ".tar.gz" in filename.lower() or ".zip" in filename.lower() or ".exe" in filename:
                print(filename)
                filenames.append(filename)
                last_added = True
        if last_added and '<span style="white-space: nowrap;" data-view-component="true" class="color-fg-muted text-sm-left flex-auto ml-md-3">' in line:
            size = line.split(">")[1].split("<")[0]
            suffix = size.split(" ")[1]
            size = size.split(" ")[0]
            sizes.append(size + " " + suffix)
            last_added = False

    # get backup link
    if not backup_link: return (filenames, sizes)
    link = backup_link
    page = requests.get(link)
    text = page.text
    lines = text.split("\n")
    last_added = False
    for line in lines:
        if "a href=" in line and "/releases/download" in line:
            #print(line)
            filename = line.split("\"")[1]
            print(filename)
            filename = filename.split("/")[-1]
            if (".tar" in filename or ".tar.gz" in filename.lower() or ".zip" in filename.lower() or ".exe" in filename or ".7z" in filename) and "mac" not in filename.lower() and "linux" not in filename.lower():
                print(filename)
                last_added = True
                filenames.append(filename)
        if last_added and '<span style="white-space: nowrap;" data-view-component="true" class="color-fg-muted text-sm-left flex-auto ml-md-3">' in line:
            size = line.split(">")[1].split("<")[0]
            suffix = size.split(" ")[1]
            size = size.split(" ")[0]
            sizes.append(size + " " + suffix)
            last_added = False
    return (filenames, sizes)
    return False

def check_for_linux(link):
    link = link + '/releases'
    page = requests.get(link)
    text = page.text
    lines = text.split("\n")
    backup_link = ''
    for line in lines:
        if "<include-fragment loading=\"lazy\"" in line:
            if not backup_link:
                backup_link = line.split("lazy\" src=\"")[1].split("\"")[0]
        if "a href=" in line and "/releases/download" in line:
            #print(line)
            filename = line.split("\"")[1]
            print(filename)
            filename = filename.split("/")[-1]
            if ".tar" in filename or "linux" in filename.lower() or "ubuntu" in filename.lower() or "." not in filename:
                print(filename)
                return True
    # get backup link
    if not backup_link: return False
    link = backup_link
    page = requests.get(link)
    text = page.text
    lines = text.split("\n")
    for line in lines:
        if "a href=" in line and "/releases/download" in line:
            #print(line)
            filename = line.split("\"")[1]
            print(filename)
            filename = filename.split("/")[-1]
            if (".tar" in filename or "linux" in filename.lower() or "ubuntu" in filename.lower() or "." not in filename or ".zip" in filename or ".7z" in filename) and "mac" not in filename.lower() and "windows" not in filename.lower():
                print(filename)
                return True
    return False

engines = get_engines()
github_links = get_github_links(engines)
#check_for_license('https://github.com/carlospolop/PurplePanda/')
#check_file_sizes('https://github.com/PGG106/Alexandria/')
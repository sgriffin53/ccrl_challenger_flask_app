import os
import requests
import ast
import zipfile
import time
from pathlib import Path
import chess, chess.engine

def find_all_files(folder_path):
    folder = Path(folder_path)
    all_files = []
    for exe_file in folder.rglob('*'):  # Search recursively for .exe files
        all_files.append(exe_file)
        #return exe_file  # Return the first .exe file found
    return all_files
    #return None  # If no .exe file is found

# test executable

def test_exe(filename):
    if "ubuntu" in filename: return False
    if "RukChess.4.0.0.NNUE2.exe" in filename: return False
    if "4ku-" in filename: return False
    if "lishex" in filename: return False
    if "Ara_" in filename: return False
    if "Mr Bob 0.7" in filename: return False
    if 'smallbrain_1.1-' in filename: return False
    if "linux" in filename: return False
    if "Raphael1.7.5" in filename: return False
    if "tinman.exe" in filename: return False
    if "eques-1.0.0" in filename: return False
    print("test")
    try:
        board = chess.Board()

        # Set up the chess engine
        with chess.engine.SimpleEngine.popen_uci(filename) as engine:
            # Set the engine options
            try:
                engine.configure({"Hash": 32})  # Example engine option (adjust as needed)
            except:
                pass
            pv = ''
            # Stream analysis as the engine processes the position
            pv = None
            start_time = time.time()
            with engine.analysis(board, chess.engine.Limit(time=0.5)) as analysis:
                for info in analysis:
                    pv_value = info.get("pv", None)
                    print("pv value:", pv_value)
                    #  if info.get("pv", None) is not None: pv = str(info.get("pv", None)[0])
                    # Check if pv_value is not None, is a list or tuple, and has elements
                    if pv_value is not None and isinstance(pv_value, (list, tuple)):
                        # Now check if it's empty
                        if len(pv_value) > 0:
                            pv = str(pv_value[0])
                        else:
                            print("pv_value is empty.")  # Debugging empty list/tuple
                    else:
                        print("pv_value is either None or not a list/tuple.")  # Debugging invalid type
                    duration = time.time() - start_time
                    print(":::", duration, pv)
                    if duration > 3: return False
                engine.quit()
            if chess.Move.from_uci(pv) not in board.legal_moves:
                return False
            return True
    except Exception as e:
        print("EXCEPTION::::", str(e))
        return False

def test_engine(engine_info):
    info = ast.literal_eval(f"{engine_info}")
    name = info[0]
    github_link = info[1]
    author = info[2]
    print(author)
    rank = info[3]
    rating = info[4]
    files = info[5]
    release_date = info[6]
    language = info[7]
    print(files)
    print(name, info)
    files_list = ast.literal_eval(f"{files}")
    print(files_list)
    for file in files_list:
        filename = file[0]
        #if "lc0" in filename: continue

        '''
        if "lc0" in filename: continue
        if "bread" in name.lower(): continue
        if "zevra" in name.lower(): continue
        if "peacekeeper" in name.lower(): continue
        if "midnight" in name.lower(): continue
        if "nalwald" in name.lower(): continue
        if "Aras_" in filename: continue
        '''
        ##print(file[1])
        #return
        download_url = github_link + file[1]
        print(filename)
        if ".zip" in filename or ".exe" in filename:
            save_path = os.path.join("downloads", filename)

            # Download file
            try:
                print(f"Downloading {filename} from {download_url}...")
                if "Ara_" in filename: continue
                response = requests.get(download_url, timeout=(20, 1200))
                response.raise_for_status()
                with open(save_path, "wb") as f:
                    f.write(response.content)
                exe_file = None
                engine_path = None
                # Handle zip files
                all_files = []
                if filename.endswith(".zip"):
                    engine_path = "downloads\\unzipped\\" + name
                    with zipfile.ZipFile(save_path, 'r') as zip_ref:
                        zip_ref.extractall(os.path.join(engine_path))
                    os.remove(save_path)
                    all_files = find_all_files(engine_path)
                else:
                    all_files = [filename]
                for file in all_files:
                    exe_file = str(file)
                    if 'downloads' not in exe_file: exe_file = 'downloads\\' + exe_file
                    if ".exe" not in exe_file: continue
                    print("testing", exe_file)
                    result = test_exe(exe_file)
                    if result:
                        #new_dir = "saved_engines\\" + name
                        old_dir = engine_path
                        if engine_path:
                            new_dir = engine_path.replace("downloads\\unzipped\\" + name, "saved_engines\\" + name)
                            copy_string = "xcopy \"" + old_dir + "\" \"" + new_dir + "\" " + "/E /I /H"
                            os.system(copy_string)
                            new_exe = exe_file.replace("downloads\\unzipped", "saved_engines")
                        else:
                            new_exe = exe_file.replace("downloads\\", "saved_engines\\" + name + "\\")
                            os.system("mkdir \"" + "saved_engines\\" + name + "\\" + "\"")
                            copy_string = "copy \"" + save_path + "\" \"" + new_exe + "\""
                            print(copy_string)
                            os.system(copy_string)
                        return((name, github_link, author, rating, new_exe, rank, release_date, language))
            except Exception as e:
                print(f"Failed to download {filename}: {e}")
        #print(file)
        #break # only test first file
    return None

def test_all_engines():
    os.system("mkdir downloads")
    os.system("mkdir downloads\\unzipped")
    os.system("mkdir saved_engines")
    f = open('engine_list_all_versions_to_test.txt', 'r', encoding='utf-8')
    lines = f.readlines()
    f.close()
    f = open('engine_list_complete.txt')
    done_lines = f.readlines()
    f.close()
    done_engines = []
    for line in done_lines:
        name = line.split("'")[1].split("'")[0]
        done_engines.append(name)
    new_lines = []
    for line in lines:
        name = line.split("'")[1].split("'")[0]
        if name in done_engines: continue
        new_lines.append(line)
    lines = list(new_lines)
    #for line in lines:
    #    if 'Trinket' in line: print(line)
    #return
    all_results = []
    i = 0
    for line in lines:
        i += 1
   #     if i < 800: continue
      #  if 'Obsidian' not in line: continue
       # if '4ku' not in line: continue
        engine_name = line.split("'")[1].split("'")[0]
        if engine_name in done_engines:
            continue
        if ' 8CPU' in engine_name:
            if engine_name.replace(' 8CPU', '') in done_engines: continue
        else:
            if engine_name + ' 8CPU' in done_engines: continue
        if ' 4CPU' in engine_name:
            if engine_name.replace(' 4CPU', '') in done_engines: continue
        else:
            if engine_name + ' 4CPU' in done_engines: continue

        done_engines.append(engine_name)
        print("-----", line)
        result = test_engine(line)
        print("---RESULT---", result)
        if result:
            engine_name = result[0]
            print("::::", engine_name)
            all_results.append(result)
            print(result)
        print(len(all_results), i)
        if i == 100000000000000: break
    f = open('engine_list_complete_new.txt','w', encoding='utf-8')
    for result in all_results:
        f.write(str(result) + "\n")
    f.close()

def test_limit(filename):

    try:
        board = chess.Board()

        # Set up the chess engine
        with chess.engine.SimpleEngine.popen_uci(filename) as engine:
            # Set the engine options
            try:
                engine.configure({"UCI_LimitStrength": 'true'})  # Example engine option (adjust as needed)
                engine.quit()
                return True
            except:
                return False
    except Exception as e:
        print("EXCEPTION::::", str(e))
        return False

def sort_ratings():
    # Step 1: Read the file
    with open('engine_list_complete_merged.txt', 'r') as file:
        lines = file.readlines()

    # Step 2: Parse the lines into a list of tuples using ast.literal_eval()
    data = []
    for line in lines:
        line = line.strip()  # Remove extra spaces or newline characters
        tuple_data = ast.literal_eval(line)  # Safely convert the string to a tuple
        data.append(tuple_data)

    # Step 3: Sort the list by the third value (which is the integer)
    data.sort(key=lambda x: int(x[3]), reverse=True)  # Sort by the third value (index 3) which is the integer

    # Step 4: Write the sorted list to a new file
    with open('engine_list_complete_sorted.txt', 'w') as file:
        for item in data:
            # Rebuild the tuple into a string and write it to the file
            file.write(f"{item}\n")

def test_limits():
    f = open('engine_list_complete.txt')
    lines = f.readlines()
    f.close()
    engines = []
    found = 0
    for line in lines:
        info = ast.literal_eval(f"{line}")
        print(info[0], info[4])
        result = test_limit(str(info[4].replace("\\","/")))
        if result:
            found += 1
            engines.append(info[0])
    for engine in engines:
        print(engine)
    print("Found:", found, "/", len(lines))

start_time = time.time()
#test_limits()
test_all_engines()
#sort_ratings()
#print(test_exe('downloads/Barbarossa-0.6.0.exe'))
#print(test_exe('downloads/trinket-v1.0.0.exe'))
duration = time.time() - start_time
print("Time taken:", duration)

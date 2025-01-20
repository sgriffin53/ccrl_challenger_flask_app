import os
import requests
import ast
import zipfile
import time
from pathlib import Path
import chess, chess.engine

def find_first_exe_file(folder_path):
    folder = Path(folder_path)
    for exe_file in folder.rglob('*.exe'):  # Search recursively for .exe files
        return exe_file  # Return the first .exe file found
    return None  # If no .exe file is found

# test executable

def test_exe(filename):
    try:
        board = chess.Board()

        # Set up the chess engine
        with chess.engine.SimpleEngine.popen_uci(filename) as engine:
            # Set the engine options
            engine.configure({"Hash": 32})  # Example engine option (adjust as needed)
            pv = ''
            # Stream analysis as the engine processes the position
            pv = None
            start_time = time.time()
            with engine.analysis(board, chess.engine.Limit(time=0.5)) as analysis:
                for info in analysis:
                    if info.get("pv", None) is not None: pv = str(info.get("pv", None)[0])
                    duration = time.time() - start_time
                    if duration > 1: return False
            engine.quit()
            if chess.Move.from_uci(pv) not in board.legal_moves:
                return False
            return True
    except:
        return False

def test_engine(engine_info):
    info = ast.literal_eval(f"{engine_info}")
    name = info[0]
    github_link = info[1]
    author = info[2]
    print(author)
    rating = info[3]
    files = info[4]
    print(files)
    print(name, info)
    files_list = ast.literal_eval(f"{files}")
    print(files_list)
    for file in files_list:
        filename = file[0]
        ##print(file[1])
        #return
        download_url = github_link + file[1]
        print(filename)
        if ".zip" in filename or ".exe" in filename:
            save_path = os.path.join("downloads", filename)

            # Download file
            try:
                print(f"Downloading {filename} from {download_url}...")
                response = requests.get(download_url)
                response.raise_for_status()
                with open(save_path, "wb") as f:
                    f.write(response.content)
                exe_file = None
                engine_path = None
                # Handle zip files
                if filename.endswith(".zip"):
                    engine_path = "downloads\\unzipped\\" + name
                    with zipfile.ZipFile(save_path, 'r') as zip_ref:
                        zip_ref.extractall(os.path.join(engine_path))
                    os.remove(save_path)
                    first_exe = find_first_exe_file(engine_path)
                    if first_exe:
                        #print(first_exe)
                        exe_file = first_exe
                        exe_dir = engine_path
                elif filename.endswith(".exe"):
                    exe_file = save_path
                exe_file = str(exe_file)
                new_exe = exe_file
                old_exe = exe_file
                if exe_file:
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
                        return((name, github_link, author, rating, new_exe))
            except Exception as e:
                print(f"Failed to download {filename}: {e}")
        #print(file)
        break
    return None

def test_all_engines():
    os.system("mkdir downloads")
    os.system("mkdir downloads\\unzipped")
    os.system("mkdir saved_engines")
    f = open('engine_info_1.txt', 'r', encoding='utf-8')
    lines = f.readlines()
    f.close()
    all_results = []
    i = 0
    for line in lines:
        i += 1
        result = test_engine(line)
        if result:
            all_results.append(result)
            print(result)
        print(len(all_results), i)
        if i == 100000000000000: break
    f = open('engine_list_complete.txt','w', encoding='utf-8')
    for result in all_results:
        f.write(str(result) + "\n")
    f.close()

start_time = time.time()
test_all_engines()
duration = time.time() - start_time
print("Time taken:", duration)

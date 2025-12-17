import traceback
import os
import requests
import ast
import zipfile
import time
import shutil
from pathlib import Path
import chess, chess.engine
import re

def find_all_files(folder_path):
    folder = Path(folder_path)
    filenames = []
    for file in folder.rglob('*'):  # Search recursively for all files
        filenames.append(file)
        #return exe_file  # Return the first .exe file found
    return filenames
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
        if ".exe" in filename: continue
        ##print(file[1])
        #return
        download_url = github_link + file[1]
        print(filename)
        if filename:
            if "4ku" in filename: continue
            if "lishex" in filename: continue
            if "Aras_" in filename: continue
            if "Ara_" in filename: continue
            if ".exe" in filename: continue
            save_path = os.path.join("downloads_linux", filename)

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
                all_files = []
                if filename.endswith(".zip") or ".tar" in filename:
                    engine_path = "downloads_linux\\unzipped\\" + name
                    with zipfile.ZipFile(save_path, 'r') as zip_ref:
                        zip_ref.extractall(os.path.join(engine_path))
                    os.remove(save_path)
                    all_files = find_all_files(engine_path)
                elif filename.endswith(""):
                    engine_path = "downloads_linux\\"
                    exe_file = save_path
                    all_files = [exe_file]
                #exe_file = str(exe_file)
                new_exe = exe_file
                old_exe = exe_file
                print("all files", all_files)
                for file in all_files:
                    exe_file = str(file)
                    if ".exe" in exe_file: continue
                    # Ensure it's an executable file (better than checking ".exe"!)
                    if not os.access(exe_file, os.X_OK):
                        continue

                    print("exe file", exe_file)
                    result = test_exe(exe_file)
                    print("result", result)

                    if result:
                        old_dir = engine_path

                        # Clean up the name to ensure it's a valid folder name (replace invalid chars)
                        name = re.sub(r'[^a-zA-Z0-9_\-\.]', '_', name)
                        print(f"Cleaned name: {name}")  # Debug: See the cleaned name

                        if engine_path:
                            new_dir = engine_path.replace(f"downloads_linux/unzipped/{name}",
                                                          f"saved_engines_linux/{name}")

                            # Create the new directory using os.system (mkdir)
                            os.system(f"mkdir -p \"{new_dir}\"")  # -p makes sure the parent directories are created

                            # Copy files from old_dir to new_dir using `cp -r` for recursive copy
                            os.system(f"cp -r \"{old_dir}\" \"{new_dir}\"")

                            # Replace path in exe_file for the new location
                            new_exe = exe_file.replace("downloads_linux/unzipped", "saved_engines_linux")
                        else:
                            # Replace path in exe_file for the new location
                            new_exe = exe_file.replace("downloads_linux/", f"saved_engines_linux/{name}/")

                            # Create the directory for the new path using os.system (mkdir)
                            os.system(f"mkdir -p \"saved_engines_linux/{name}\"")

                            # Copy the file from save_path to the new executable location
                            os.system(f"cp \"{save_path}\" \"{new_exe}\"")

                        return (name, github_link, author, rating, new_exe)
            except Exception as e:
                print(f"Failed to download {filename}: {e}")
                traceback.print_exc()
        #print(file)
        #break
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
        if i == 10000: break
    f = open('engine_list_complete_linux.txt','w', encoding='utf-8')
    for result in all_results:
        f.write(str(result) + "\n")
    f.close()

start_time = time.time()
test_all_engines()
duration = time.time() - start_time
print("Time taken:", duration)

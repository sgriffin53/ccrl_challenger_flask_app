import requests

def test_engine(engine_name):
    fen = 'rnbqkbnr/ppp2ppp/3p4/8/2B1Pp2/5N2/PPPP2PP/RNBQK2R w KQkq - 0 1'
    url = f'https://ccrl_tunnel.blindfoldchess.app/stream_engine?fen={fen}&engine_name={engine_name}&move_time=0.5&book_moves=0'
    page = requests.get(url)
    text = page.text
    if 'error' in text: return False
    if 'best_move' in text:
        return True
    return False

def test_all_engines():
    file = 'engine_list_complete.txt'
    f = open(file,'r',encoding='utf-8')
    lines = f.readlines()
    f.close()
    to_delete = []
    for line in lines:
        engine_name = line.split("'")[1].split("'")[0]
        result = test_engine(engine_name)
        print(engine_name, result)
        if not result:
            to_delete.append(engine_name)
    return to_delete

def delete_engines(to_delete):
    file = 'engine_list_complete.txt'
    f = open(file,'r',encoding='utf-8')
    lines = f.readlines()
    f.close()
    new_lines = []
    for line in lines:
        engine_name = line.split("'")[1].split("'")[0]
        if engine_name in to_delete:
            continue
        new_lines.append(line)
    file = 'engine_list_complete_new.txt'
    f = open(file,'w',encoding='utf-8')
    for line in lines:
        f.write(line + "\n")
    f.close()

#print(test_engine('Stockfish 17 64-bit 8CPU1'))
to_delete = test_all_engines()
for line in to_delete:
    print(line)
delete_engines(to_delete)
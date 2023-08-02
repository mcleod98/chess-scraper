import re, os
import datetime
from functools import partial
from models import GameRecord, Move, Download

class Parser():
    def __init__(self, config, session):
        self.session = session
        self.parse_path = os.path.abspath(config.SCRAPER_DOWNLOAD_PATH)
        self.my_account = config.ACCOUNT_NAME

    
    def parse_file_list(self, list):
        '''
        Parses a list of files using parse_txt_file
        '''
        for filename in list:
            self.parse_txt_file(self.parse_path + '/' + filename)

    def parse_download_folder(self):
        '''
        Parses all new files in the dowload folder.
        First queries the database to find which files have already been parsed
        '''
        old = [r[0] for r in self.session.query(Download.filename).all()]
        for root, dir, files in os.walk(self.parse_path):
            for f in files:
                fname, ext = os.path.splitext(f)
                if ext == '.pgn' and f not in old:
                    self.parse_txt_file(os.path.join(root, f))

    def parse_txt_file(self, filepath):
        '''
        Parses a downloaded game record, which is a plain text document containing meta data and move lists for multiple chess games
        Muliple entries are created in the database:
            GameRecord: Meta data for a single chess game
            Move: Data for a single move. Each GameRecord may have many moves connected by their database relationship
            Download: Represents the actual downloaded text file. This is to keep track of which files have been parsed already (as checked above in parse_download_folder)

        '''
        with open(filepath) as f:
            print(f'parsing txt file {filepath}')

            # Find the first line for of each game in the file
            lines = f.readlines()
            startpoints = [i for i, line in enumerate(lines) if re.match(r'\[Event', line)]
            p = r'"(.*)"'

            # Extract metadata for each game by counting off lines from the startpoints found above
            for shift in startpoints:
                datestr = re.search(p, lines[shift + 2]).group().strip('"')
                whiteplayer = re.search(p, lines[shift + 4]).group().strip('"')
                blackplayer = re.search(p, lines[shift + 5]).group().strip('"')
                res = re.search(p, lines[shift + 6]).group().strip('"')
                whiteelo = int(re.search(p, lines[shift + 7]).group().strip('"'))
                blackelo = int(re.search(p, lines[shift + 8]).group().strip('"'))
                tc = re.search(p, lines[shift + 9]).group().strip('"')
                endtime = re.search(p, lines[shift + 10]).group().strip('"')
                endtype = re.search(p, lines[shift + 11]).group().strip('"')

                # Parse the raw text fields to create a GameRecord object, then add it to our database session
                kw = {}
                if whiteplayer == self.my_account:
                    kw['white'] = True
                    kw['op_name'] = blackplayer
                    kw['my_elo'] = whiteelo
                    kw['opp_elo'] = blackelo
                    kw['result'] = did_i_win(white=True, result=res)
                elif blackplayer == self.my_account:
                    kw['white'] = False
                    kw['op_name'] = whiteplayer
                    kw['my_elo'] = blackelo
                    kw['opp_elo'] = whiteelo
                    kw['result'] = did_i_win(white=False, result=res)
                kw['ending'] = parse_ending(endtype)
                year, month, day = datestr.split('.')
                hour, minute, second = endtime.split(' ')[0].split(':')
                kw['date_played'] = datetime.datetime(year=int(year), month=int(month), day=int(day), hour=int(hour), minute=int(minute), second=int(second))
                kw['timecontrol'] = tc
                _game = GameRecord(**kw)
                self.session.add(_game)

                # Moves are listed at the end of each game record as a single line of text (kind of, there are newline characters)
                # Since the number of moves in a game varies, the number of lines we need to select also varies
                # Selects all relevant lines and combines them into 'moveline' which we parse below
                moveline = ''
                i = 13
                while not re.match(r'\n', lines[shift + i]):
                    moveline += lines[shift + i]
                    i += 1
                    if i + shift >= len(lines):
                        break
                self.parse_moves(game=_game, moveline=moveline)

            
            # After parsing the whole file, make a Download object to record that this raw file has been parsed
            _download = Download(filename=os.path.basename(filepath))
            self.session.add(_download)

    def parse_moves(self, game, moveline):
        '''
        Parses a list of moves from a line of text, as stored in downloaded game records
        Each move is numbered and added to the sqlalchemy session with a reference to the game from which it came
        '''
        moves = moveline.replace('\n', ' ').strip().split(' ')
        movecounter = 1
        for m in moves:
            # ignore the turn counters and game results, we just need the moves
            if m not in ['1-0', '0-1', '0-0'] and m.find('.') == -1:
                _move = Move(game=game, movenumber=movecounter, move=m)
                self.session.add(_move)
                movecounter += 1

def did_i_win(white, result):
    '''
    Outputs whether a game was a win (W) loss (L) or draw (D)
    '''
    if result == 'draw':
        return 'D'
    if white and result == '1-0':
        return 'W'
    if white and result == '0-1':
        return 'L'
    if not white and result == '0-1':
        return 'W'
    if not white and result == '1-0':
        return 'L'

def parse_ending(endstr):
    if endstr.find('by checkmate') != -1:
        return 'checkmate'
    elif endstr.find('by resignation') != -1:
        return 'resignation'
    elif endstr.find('on time') != -1:
        return 'time'
    else:
        return 'draw'

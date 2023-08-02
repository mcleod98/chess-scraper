import scraper, parser, config, db
from sqlalchemy import func
import models, db
import asyncio

conf = config.Config()
session = db.get_session(conf)

#r = session.query(models.GameRecord).join(models.Move).filter(models.Move.movenumber == 1, models.Move.move == 'e4').all()
r = session.execute("""
    SELECT distinct game.id
    FROM game
    JOIN move on game.id = move.game_id
    WHERE ((move.movenumber = 1 and move.move = 'e4') or (move.movenumber = 2 and move.move = 'c5'))
    and game.white = False
    GROUP BY game.id
    HAVING COUNT(move) = 2""").all()
print(len(r))


y = session.execute(f"""
    SELECT move.movenumber, move.move
    FROM move
    JOIN game on game.id = move.game_id
    WHERE game.id = {1}
    ORDER BY move.movenumber ASC
    """).all()
print(y)
print(y[0])

#where game.moves = any (select move.movenumber from move where move.movenumber = 1)'
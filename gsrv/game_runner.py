from gsrv import settings
from gsrv.runtime import RT
from gsrv.dtypes import Game, GuessARandom

import asyncio
import time


class GameRunner:
    def __init__(self, rt: RT,
                 max_concurrent_games: int = settings.MAX_CONCURRENT_GAMES):
        self.logger = rt.get_logger(self.__class__.__name__)
        self.rt = rt
        self.max_concurrent_games = max_concurrent_games
        self.finished_games = asyncio.Queue()

    async def start(self):
        await asyncio.gather(
            asyncio.create_task(self._run_games()),
            asyncio.create_task(self._collect_finished_games()),
        )

    async def _run_games(self, intval=15):
        started = 0
        while self.rt.is_running():
            if started and time.time() - started < intval:
                await asyncio.sleep(0.05)
                continue
            started = time.time()
            n = self.max_concurrent_games - len(self.rt.games)
            for i in range(n):
                g = GuessARandom()
                task = asyncio.create_task(self._execute_game(g))
                self.logger.info(g)
                await self.rt.add_game(g, task)

    async def _collect_finished_games(self):
        while self.rt.is_running():
            try:
                game_id = await asyncio.wait_for(
                    self.finished_games.get(),
                    timeout=0.1
                )
                await self.rt.remove_game(game_id)
            except asyncio.TimeoutError:
                pass

    async def _execute_game(self, game: Game):
        try:
            await asyncio.wait_for(
                self._wait_for_players(game),
                timeout=settings.GAME_PENDING_TIMEOUT
            )
        except asyncio.TimeoutError:
            pass

        if len(game.state.players) < game.settings.min_players:
            game.cancel()
        else:
            print("STARTING", game.game_id)
            # FIXME
            await game.start()
            self.finished_games.put_nowait(game.game_id)

    async def _wait_for_players(self, g: Game):
        while len(g.state.players) < g.settings.max_players:
            # self.logger.info("Pending: %s", len(g.state.players))
            await asyncio.sleep(0.05)

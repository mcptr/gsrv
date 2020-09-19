import asyncio
import signal
import logging
import concurrent


STOP_EV = asyncio.Event()


def setup_signals(loop, handler=None):
    for sig in {signal.SIGINT, signal.SIGTERM}:
        if handler:
            loop.add_signal_handler(
                sig,
                lambda s=sig: handler(loop, sig=s))
        else:
            loop.add_signal_handler(
                sig,
                lambda s=sig: loop.create_task(shutdown(loop, sig=s)))


async def shutdown(loop, sig=None):
    # await loop.shutdown_asyncgens()
    tasks = [t for t in asyncio.all_tasks()
             if t is not asyncio.current_task()]

    # pending = asyncio.Task.all_tasks()
    [t.cancel() for t in tasks]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    handle_task_results(results)


def handle_exception(loop, context, *args, **kwargs):
    msg = context.get("exception", context["message"])
    logging.error("Caught exception: %s", msg)
    # logging.error(context)
    # asyncio.ensure_future(shutdown(loop))


def handle_task_results(results, *args, **kwargs):
    for res in results:
        if res and isinstance(res, Exception):
            if not isinstance(res, concurrent.futures._base.CancelledError):
                logging.error("%s: %s", type(res), res)


async def cancel_tasks(task, *tasks):
    tasks = [task, *tasks]
    [t.cancel() for t in tasks]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    handle_task_results(results)


def run(coro, **kwargs):
    terminate_func = kwargs.pop("terminate", None)

    loop = asyncio.get_event_loop()
    if not kwargs.pop("no_exception_handler", False):
        loop.set_exception_handler(handle_exception)

    setup_signals(loop, terminate_func)

    try:
        loop.run_until_complete(coro)
    except asyncio.exceptions.CancelledError as e:
        # logging.error(e)
        pass
    finally:
        pass

    loop.run_until_complete(shutdown(loop))
    loop.close()

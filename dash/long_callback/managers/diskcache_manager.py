import traceback
from contextvars import copy_context
import asyncio
from functools import partial

from . import BaseLongCallbackManager
from .._proxy_set_props import ProxySetProps
from ..._callback_context import context_value
from ..._utils import AttributeDict
from ...exceptions import PreventUpdate

_pending_value = "__$pending__"


class DiskcacheManager(BaseLongCallbackManager):
    """Manage the background execution of callbacks with subprocesses and a diskcache result backend."""

    def __init__(self, cache=None, cache_by=None, expire=None):
        """
        Long callback manager that runs callback logic in a subprocess and stores
        results on disk using diskcache

        :param cache:
            A diskcache.Cache or diskcache.FanoutCache instance. See the diskcache
            documentation for information on configuration options. If not provided,
            a diskcache.Cache instance will be created with default values.
        :param cache_by:
            A list of zero-argument functions.  When provided, caching is enabled and
            the return values of these functions are combined with the callback
            function's input arguments and source code to generate cache keys.
        :param expire:
            If provided, a cache entry will be removed when it has not been accessed
            for ``expire`` seconds.  If not provided, the lifetime of cache entries
            is determined by the default behavior of the ``cache`` instance.
        """
        try:
            import diskcache  # pylint: disable=import-outside-toplevel
            import psutil  # noqa: F401,E402 pylint: disable=import-outside-toplevel,unused-import,unused-variable,import-error
            import multiprocess  # noqa: F401,E402 pylint: disable=import-outside-toplevel,unused-import,unused-variable
        except ImportError as missing_imports:
            raise ImportError(
                """\
DiskcacheLongCallbackManager requires extra dependencies which can be installed doing

    $ pip install "dash[diskcache]"\n"""
            ) from missing_imports

        if cache is None:
            self.handle = diskcache.Cache()
        else:
            if not isinstance(cache, (diskcache.Cache, diskcache.FanoutCache)):
                raise ValueError(
                    "First argument must be a diskcache.Cache "
                    "or diskcache.FanoutCache object"
                )
            self.handle = cache

        self.expire = expire
        super().__init__(cache_by)

    def terminate_job(self, job):
        import psutil  # pylint: disable=import-outside-toplevel,import-error

        if job is None:
            return

        job = int(job)

        # Use diskcache transaction so multiple process don't try to kill the
        # process at the same time
        with self.handle.transact():
            if psutil.pid_exists(job):
                process = psutil.Process(job)

                for proc in process.children(recursive=True):
                    try:
                        proc.kill()
                    except psutil.NoSuchProcess:
                        pass

                try:
                    process.kill()
                except psutil.NoSuchProcess:
                    pass

                try:
                    process.wait(1)
                except (psutil.TimeoutExpired, psutil.NoSuchProcess):
                    pass

    def terminate_unhealthy_job(self, job):
        import psutil  # pylint: disable=import-outside-toplevel,import-error

        job = int(job)

        if job and psutil.pid_exists(job):
            if not self.job_running(job):
                self.terminate_job(job)
                return True

        return False

    def job_running(self, job):
        import psutil  # pylint: disable=import-outside-toplevel,import-error

        job = int(job)

        if job and psutil.pid_exists(job):
            proc = psutil.Process(job)
            return proc.status() != psutil.STATUS_ZOMBIE
        return False

    def make_job_fn(self, fn, progress, key=None):
        return _make_job_fn(fn, self.handle, progress)

    def clear_cache_entry(self, key):
        self.handle.delete(key)

    # noinspection PyUnresolvedReferences
    def call_job_fn(self, key, job_fn, args, context):
        """
        Call the job function, supporting both sync and async jobs.
        Args:
            key: Cache key for the job.
            job_fn: The job function to execute.
            args: Arguments for the job function.
            context: Context for the job.
        Returns:
            The PID of the spawned process or None for async execution.
        """
        # pylint: disable-next=import-outside-toplevel,no-name-in-module,import-error
        from multiprocess import Process

        # pylint: disable-next=not-callable
        process = Process(
            target=job_fn,
            args=(key, self._make_progress_key(key), args, context),
        )
        process.start()
        return process.pid

    @staticmethod
    def _run_async_in_process(job_fn, key, args, context):
        """
        Helper function to run an async job in a new process.
        Args:
            job_fn: The async job function.
            key: Cache key for the job.
            args: Arguments for the job function.
            context: Context for the job.
        """
        # Create a new event loop for the process
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # Wrap the job function to include key and progress
        async_job = partial(job_fn, key, args, context)

        try:
            # Run the async job and wait for completion
            loop.run_until_complete(async_job())
        except Exception as e:
            # Handle errors, log them, and cache if necessary
            raise Exception(str(e)) from e
        finally:
            loop.close()

    def get_progress(self, key):
        progress_key = self._make_progress_key(key)
        progress_data = self.handle.get(progress_key)
        if progress_data:
            self.handle.delete(progress_key)

        return progress_data

    def result_ready(self, key):
        return self.handle.get(key) is not None

    def get_result(self, key, job):
        # Get result value
        result = self.handle.get(key, self.UNDEFINED)
        if result is self.UNDEFINED:
            return self.UNDEFINED

        # Clear result if not caching
        if self.cache_by is None:
            self.clear_cache_entry(key)
        else:
            if self.expire:
                self.handle.touch(key, expire=self.expire)

        self.clear_cache_entry(self._make_progress_key(key))

        if job:
            self.terminate_job(job)
        return result

    def get_updated_props(self, key):
        set_props_key = self._make_set_props_key(key)
        result = self.handle.get(set_props_key, self.UNDEFINED)
        if result is self.UNDEFINED:
            return {}

        self.clear_cache_entry(set_props_key)

        return result


# pylint: disable-next=too-many-statements
def _make_job_fn(fn, cache, progress):
    # pylint: disable-next=too-many-statements
    def job_fn(result_key, progress_key, user_callback_args, context):
        def _set_progress(progress_value):
            if not isinstance(progress_value, (list, tuple)):
                progress_value = [progress_value]

            cache.set(progress_key, progress_value)

        maybe_progress = [_set_progress] if progress else []

        def _set_props(_id, props):
            cache.set(f"{result_key}-set_props", {_id: props})

        ctx = copy_context()

        def run():
            c = AttributeDict(**context)
            c.ignore_register_page = False
            c.updated_props = ProxySetProps(_set_props)
            context_value.set(c)
            errored = False
            try:
                if isinstance(user_callback_args, dict):
                    user_callback_output = fn(*maybe_progress, **user_callback_args)
                elif isinstance(user_callback_args, (list, tuple)):
                    user_callback_output = fn(*maybe_progress, *user_callback_args)
                else:
                    user_callback_output = fn(*maybe_progress, user_callback_args)
            except PreventUpdate:
                errored = True
                cache.set(result_key, {"_dash_no_update": "_dash_no_update"})
            except Exception as err:  # pylint: disable=broad-except
                errored = True
                cache.set(
                    result_key,
                    {
                        "long_callback_error": {
                            "msg": str(err),
                            "tb": traceback.format_exc(),
                        }
                    },
                )

            if not errored:
                cache.set(result_key, user_callback_output)

        async def async_run():
            c = AttributeDict(**context)
            c.ignore_register_page = False
            c.updated_props = ProxySetProps(_set_props)
            context_value.set(c)
            errored = False
            try:
                if isinstance(user_callback_args, dict):
                    user_callback_output = await fn(
                        *maybe_progress, **user_callback_args
                    )
                elif isinstance(user_callback_args, (list, tuple)):
                    user_callback_output = await fn(
                        *maybe_progress, *user_callback_args
                    )
                else:
                    user_callback_output = await fn(*maybe_progress, user_callback_args)
            except PreventUpdate:
                errored = True
                cache.set(result_key, {"_dash_no_update": "_dash_no_update"})
            except Exception as err:  # pylint: disable=broad-except
                errored = True
                cache.set(
                    result_key,
                    {
                        "long_callback_error": {
                            "msg": str(err),
                            "tb": traceback.format_exc(),
                        }
                    },
                )
            if asyncio.iscoroutine(user_callback_output):
                user_callback_output = await user_callback_output
            if not errored:
                cache.set(result_key, user_callback_output)

        if asyncio.iscoroutinefunction(fn):
            func = partial(ctx.run, async_run)
            asyncio.run(func())
        else:
            ctx.run(run)

    return job_fn


class DiskcacheLongCallbackManager(DiskcacheManager):
    """Deprecated: use `from dash import DiskcacheManager` instead."""

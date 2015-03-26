from subprocess import Popen, PIPE
import platform
import os


class CancelAction(RuntimeError):
    pass


def run_exe(exe, params, try_admin=False, force_admin=False, working_dir=None):
    if platform.system() == 'Windows':
        # On Windows, launch executable using [`ShellExecuteEx`][1] function,
        # which can be configured to show program output in a terminal window.
        #
        # [1]: https://msdn.microsoft.com/en-us/library/windows/desktop/bb762154%28v=vs.85%29.aspx
        def run_func(exe, params, as_admin):
            import win32com.shell.shell as shell
            import win32con
            from win32process import GetExitCodeProcess
            import win32event
            import pywintypes
            try:
                # Try to launch process as administrator in case exception was
                # due to insufficient privileges.
                # To make process call block, set `fMask` parameter to return
                # handle to process that can be monitored to wait for the
                # process to exit.  See the [SHELLEXECUTEINFO structure
                # documentation][1] for details.
                #
                # [1]: https://msdn.microsoft.com/en-us/library/windows/desktop/bb759784%28v=vs.85%29.aspx
                SEE_MASK_NOASYNC = 0x00000100
                SEE_MASK_NOCLOSEPROCESS = 0x00000040
                WAIT_FOREVER = -1

                launch_kwargs = dict(lpFile=exe, lpParameters=params,
                                     nShow=win32con.SW_SHOW,
                                     fMask=(SEE_MASK_NOASYNC |
                                            SEE_MASK_NOCLOSEPROCESS))
                if as_admin:
                    launch_kwargs['lpVerb'] = 'runas'
                process_info = shell.ShellExecuteEx(**launch_kwargs)
                win32event.WaitForSingleObject(process_info['hProcess'],
                                               WAIT_FOREVER)
                return_code = GetExitCodeProcess(process_info['hProcess'])
                if return_code == 0:
                    return ''
                else:
                    raise RuntimeError('Process returned error code: %s' %
                                       return_code)
            except pywintypes.error, e:
                if e.winerror == 1223:  # Error 1223 is elevation cancelled.
                    raise CancelAction(e.strerror)
                else:
                    raise
    elif (force_admin or try_admin):
        raise RuntimeError('Elevation to administrator privileges is currently'
                           ' only supported on Windows.')
    else:
        def run_func(exe, params, as_admin):
            process = Popen('%s %s' % (exe, params),
                            shell=True, stdout=PIPE, stderr=PIPE)
            stdout, stderr = process.communicate()

            if process.returncode == 0:
                # Process completed successfully.
                return stdout + stderr
            else:
                raise RuntimeError('Process returned error code: %s' %
                                   process.returncode)
    try:
        original_cwd = os.getcwd()
        if working_dir is not None:
            os.chdir(working_dir)

        output = None
        if not force_admin:
            # Try to run process not using administrator privileges.
            try:
                output = run_func(exe, params, False)
            except RuntimeError:
                if try_admin:
                    # Process failed, so try again with administrator
                    # privileges.
                    force_admin = True
        if output is None and force_admin:
            output = run_func(exe, params, True)
        return output
    finally:
        if working_dir is not None:
            os.chdir(original_cwd)

from subprocess import check_output, Popen, PIPE
import platform
import sys


class CancelAction(RuntimeError):
    pass


def run_exe(exe, params, try_admin=False):
    process = Popen('%s %s' % (sys.executable, params),
                    shell=True, stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()

    if process.returncode == 0:
        # Process completed successfully.
        return stdout
    elif try_admin and platform.system() == 'Windows':
        import win32com.shell.shell as shell
        import win32con
        import win32event
        import pywintypes

        # Process returned an error code.
        try:
            # Try to launch process as administrator in case exception was due
            # to insufficient privileges.
            # To make process call block, set `fMask` parameter to return
            # handle to process that can be monitored to wait for the process
            # to exit.  See the [SHELLEXECUTEINFO structure documentation][1]
            # for details.
            #
            # [1]: https://msdn.microsoft.com/en-us/library/windows/desktop/bb759784%28v=vs.85%29.aspx
            SEE_MASK_NOASYNC = 0x00000100
            SEE_MASK_NOCLOSEPROCESS = 0x00000040
            WAIT_FOREVER = -1

            process_info = shell.ShellExecuteEx(lpVerb='runas',
                                                lpFile=sys.executable,
                                                lpParameters=params,
                                                nShow=win32con.SW_SHOW,
                                                fMask=
                                                (SEE_MASK_NOASYNC |
                                                 SEE_MASK_NOCLOSEPROCESS))
            win32event.WaitForSingleObject(process_info['hProcess'],
                                           WAIT_FOREVER)
            return ''
        except pywintypes.error, e:
            if e.winerror == 1223:  # Error 1223 is elevation cancelled.
                raise CancelAction(e.strerror)
            else:
                raise
    else:
        raise RuntimeError(stdout + stderr)

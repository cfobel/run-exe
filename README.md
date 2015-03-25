# Overview #

Run executable file, with option to try as admin on error on Windows. 

# Usage #

The following example opens a temporary file in the root of `C:`.  This should
prompt the user to permit the process to run with elevated privileges.

    import sys
    import tempfile
    
    t = tempfile.mktemp(dir='C:/')
    
    run_exe(sys.executable, ''' -c "'''
            '''import os;'''
            '''open('%s', 'wb')'''
            '''os.remove(%s)"''' % (t, t),
            try_admin=True)

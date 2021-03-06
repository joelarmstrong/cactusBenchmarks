"""
A bunch of miscellaneous helpful functions copied from sonLib.
"""
import subprocess
import tempfile
import sys

def system(cmd):
    """Run a command or die if it fails"""
    sts = subprocess.call(cmd, shell=True, bufsize=-1, stdout=sys.stdout, stderr=sys.stderr)
    if sts != 0:
        raise RuntimeError("Command: %s exited with non-zero status %i" % (cmd, sts))

def getTempDirectory(rootDir=None):
    """
    returns a temporary directory that must be manually deleted
    """
    if rootDir is None:
        return tempfile.mkdtemp()
    else:
        while True:
            rootDir = os.path.join(rootDir, "tmp_" + getRandomAlphaNumericString())
            if not os.path.exists(rootDir):
                break
        os.mkdir(rootDir)
        os.chmod(rootDir, 0777) #Ensure everyone has access to the file.
        return rootDir

def nameValue(name, value, valueType=str, quotes=False):
    """Little function to make it easier to make name value strings for commands.
    """
    if valueType == bool:
        if value:
            return "--%s" % name
        return ""
    if value is None:
        return ""
    if quotes:
        return "--%s '%s'" % (name, valueType(value))
    return "--%s %s" % (name, valueType(value))

def popenCatch(command, stdinString=None):
    """Runs a command and return standard out.
    """
    if stdinString != None:
        process = subprocess.Popen(command, shell=True,
                                   stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=sys.stderr, bufsize=-1)
        output, nothing = process.communicate(stdinString)
    else:
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=sys.stderr, bufsize=-1)
        output, nothing = process.communicate() #process.stdout.read().strip()
    sts = process.wait()
    if sts != 0:
        raise RuntimeError("Command: %s with stdin string '%s' exited with non-zero status %i" % (command, stdinString, sts))
    return output

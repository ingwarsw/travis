#!/usr/bin/env python
import os, os.path, sys, string, getopt, xml.dom.minidom, subprocess

# https://github.com/Prototik/HoloEverywhere-Addon-Roboguice/blob/0d343e0ddd0607b0c9319eb21fdc50d451019f42/.travis.py

def main(argv):
    mode = string.join(argv)
    if mode == "--fetch":
        mvn_fetch()
    elif mode == "--test":
        mvn_test()
    elif mode == "--deploy":
        if "TRAVIS_SECURE_ENV_VARS" in os.environ and os.environ["TRAVIS_SECURE_ENV_VARS"] == "true":
            mvn_deploy()
        else:
            print " # [MAVEN] Wrong variables to deploy, so not deploying"
    else:
        print " # [ERR] No such mode"

def mvn_call(tests = False, extra = []):
    args = ["mvn", "test", "--batch-mode", "-T4"]
    if "PROFILE" in os.environ:
        args = args + ["-P{}".format(os.environ["PROFILE"])]
    if not tests:
        args = args + ["-DskipTests=true"]
    call(args + extra)
        
def mvn_fetch(num = 3):
    print " # [MAVEN] Fetching all"
    for i in range(0, num + 1):
        try:
            mvn_call()
            print " # [MAVEN] Fetch done after [{}] retries".format(i)
            break
        except subprocess.CalledProcessError:
            if i < num:
                print " # [MAVEN] Retrying fetch [{}]..".format(i + 1)
                pass
            else:
                raise


def mvn_test():
    print " # [MAVEN] Test..."
    mvn_call(True)

def mvn_deploy():
    print " # [MAVEN] Deploy..."
    maven_config = os.getcwd() + "/.maven.xml"
    create_maven_config(maven_config, os.environ["DEPLOY_USERNAME"], os.environ["DEPLOY_PASSWORD"], os.environ["DEPLOY_SERVER_ID"])
    mvn_call(False, ["deploy", "--settings=" + maven_config])

def create_maven_config(filename, username, password, server_id):
    m2 = xml.dom.minidom.parse(os.path.expanduser("~") + '/.m2/settings.xml')

    settings = m2.getElementsByTagName("settings")[0]
    serversNodes = settings.getElementsByTagName("servers")
    if not serversNodes:
        serversNode = m2.createElement("servers")
        settings.appendChild(serversNode)
    else:
        serversNode = serversNodes[0]

    serverNode = m2.createElement("server")

    serverId = m2.createElement("id")
    serverId.appendChild(m2.createTextNode(server_id))
    serverNode.appendChild(serverId)

    serverUser = m2.createElement("username")
    serverUser.appendChild(m2.createTextNode(username))
    serverNode.appendChild(serverUser)

    serverPass = m2.createElement("password")
    serverPass.appendChild(m2.createTextNode(password))
    serverNode.appendChild(serverPass)
 
    serversNode.appendChild(serverNode)
  
    f = open(filename, 'w')
    f.write(m2.toxml())
    f.close()

def call(command, hide_output=False):
    print " # [CALL] {}".format(string.join(command))
    if hide_output:
        subprocess.check_call(command, env=os.environ, stdout=os.open("/dev/null", os.W_OK))
    else:
        subprocess.check_call(command, env=os.environ)

def call_output(command):
    return subprocess.check_output(command, env=os.environ)

def which(program):
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)
    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file
    return False

if __name__ == "__main__":
    main(sys.argv[1:])

#!/usr/bin/env python
import os, os.path, sys, getopt, xml.dom.minidom, subprocess

# https://github.com/Prototik/HoloEverywhere-Addon-Roboguice/blob/0d343e0ddd0607b0c9319eb21fdc50d451019f42/.travis.py

def main(argv):
    mvn_fetch()
    mvn_test()
  
    if os.environ["TRAVIS_SECURE_ENV_VARS"] == "true" && os.environ["SONATYPE_SNAPSHOT"] == "true":
        mvn_deploy();

def mvn_call(tests = false, extra = [])
    args = ["mvn", "install", "--batch-mode"]
    if not tests:
        args = args + ["-DskipTests=true"]
    call(args + extra)
	    
def mvn_fetch(num):
	print " # [MAVEN] Fetching all"
	for i in range(0, num):
	    try:
	        mvn_call()
	        break
        except subprocess.CalledProcessError:
            print " [MAVEN] Retrying fetch [" + i + "].."
            pass

def mvn_test():
	print " # [MAVEN] Test..."
	    mvn_call(true)

def mvn_deploy():
	print " # [MAVEN] Deploy..."
	maven_config = os.getcwd() + "/.maven.xml"
	create_maven_config(maven_config, os.environ["SONATYPE_USERNAME"], os.environ["SONATYPE_PASSWORD"])
	mvn_call(["deploy", "--settings=" + maven_config])

def create_maven_config(filename, username, password):
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
	serverId.appendChild(m2.createTextNode("sonatype-nexus-snapshots"))
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

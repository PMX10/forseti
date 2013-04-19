#!/bin/sh

lcm-gen -j types/*.lcm
javac -cp .:lcm.jar Forseti/*.java
jar cvf Forseti/Forseti.jar Forseti/*.class
export CLASSPATH=$CLASSPATH:./Forseti/Forseti.jar
alias java='java -ea -server'
lcm-spy
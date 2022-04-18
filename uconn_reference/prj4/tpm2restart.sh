#!/bin/sh

pkill dbus-daemon
pkill tpm_server
pkill tpm2-abrmd

rm -rf /var/run/dbus.pid

# Start dbus service and sleep for 1 second to wait that it has started.
# If tpm2-abrmd starts before the dbus service is ready we get an error.
dbus-daemon --system &
sleep 1

# Start the ibm tpm simulator with default settings
tpm_server &

# Start tpm2 access broker & resource manager daemon
tpm2-abrmd --allow-root --tcti=mssim &


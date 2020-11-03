if [ "$(id -u)" != "0" ]; then
    echo "Run it as root"
	echo
	echo "usage: sudo bash install.sh --install | --uninstall"

else
	if [ "$1" = "--install" ] ; then
		if [ ! -d /usr/share/MACSwitcher ]; then
			mkdir /usr/share/MACSwitcher
		fi
		cp install.sh /usr/share/MACSwitcher
		cp macs.py /usr/share/MACSwitcher
		cp macvendors.py /usr/share/MACSwitcher
		cp .bin/macs /usr/bin
		chmod +x /usr/bin/macs
		echo "MACSwitcher installed successfully"

	elif [ "$1" = "--uninstall" ] ; then
		if [ -d /usr/share/MACSwitcher ] ; then
			rm -r  /usr/share/MACSwitcher
		fi
		if [ -e /usr/bin/macs ] ; then
			rm /usr/bin/macs
		fi
		echo "MACSwitcher uninstalled successfully"
	else
		echo "usage: bash install.sh --install | --uninstall"
	fi			
fi
 

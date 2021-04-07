all: ws-annotator ws-annotator.service
.PHONY: all ws-annotator install uninstall
lib_dir=/usr/local/lib/ws-annotator
conf_dir=/usr/local/etc/ws-annotator
service_dir=/etc/systemd/system
venv=$(lib_dir)/venv

install: $(service_dir) ws-annotator.service
	@echo Installing the service files...
	cp ws-annotator.service $(service_dir)
	chown root:root $(service_dir)/ws-annotator.service
	chmod 644 $(service_dir)/ws-annotator.service

	@echo Installing library files...
	mkdir -p $(lib_dir)
	cp annotator.py $(lib_dir)
	cp validator.py $(lib_dir)
	chown root:root $(lib_dir)/*
	chmod 644 $(lib_dir)/*

	@echo Installing configuration files...
	mkdir -p $(conf_dir)
	cp ws-annotator.env $(conf_dir)
	chown root:root $(conf_dir)/*
	chmod 644 $(conf_dir)/*

	@echo Creating python virtual environment and isntalling packages...
	python3 -m venv $(venv)
	$(venv)/bin/pip3 install numpy
	$(venv)/bin/pip3 install -r requirements.txt
	#$(venv)/bin/pip3 install micropipenv
	#$(venv)/bin/micropipenv install

	@echo Installation complete...
	@echo run 'systemctl start ws-annotator' to start service
	@echo run 'systemctl status ws-annotator' to view status

uninstall:
	-systemctl stop ws-annotator
	-systemctl disable ws-annotator
	-rm -r $(lib_dir)
	-rm -r $(conf_dir)
	-rm -r $(service_dir)/ws-annotator.service

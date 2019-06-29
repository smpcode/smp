THIS_MAKEFILE_PATH := $(word $(words $(MAKEFILE_LIST)),$(MAKEFILE_LIST))
THIS_DIR := $(shell cd $(dir $(THIS_MAKEFILE_PATH));pwd)

PYTHON_BIN := $(shell which python3)
AUTOPEP8_BIN := $(shell which autopep8)
PIP_BIN := $(shell which pip3)
PYTEST_BIN := $(shell which py.test)
MKDOCS_BIN := $(shell which mkdocs)
DOCKER_BIN := $(shell which docker)

ENV := dev
CONFIG := $(THIS_DIR)/conf/$(ENV)/conf.yml

install:
	@echo "开始安装基础环境"
	$(PIP_BIN) install -r requirements.txt

run:
	@echo "debug模式启动api服务"
	$(PYTHON_BIN) cli.py -f $(CONFIG) api --route=all --port=7654 --prefork=1 -D --allow-origin="http://127.0.0.1:8081"

run_prefork:
	$(PYTHON_BIN) cli.py -f $(CONFIG) api --route=all --port=7654 --prefork=2 --allow-origin="http://127.0.0.1:8081"

test:
	$(PYTEST_BIN) . -v

pytest:
	$(PYTEST_BIN) . -s

format:
	@echo "格式化代码"
	find . -name "*.py" | xargs $(AUTOPEP8_BIN) -i --aggressive

clean:
	@echo "执行清理操作"
	find . -name "*.pyc" | xargs rm -rf
	find . -name "__pycache__" | xargs rm -rf


.PHONY: run test docs

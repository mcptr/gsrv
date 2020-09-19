.PHONY: all


.DEFAULT_GOAL 		:= all
__SELF_DIR 		:= $(dir $(lastword $(MAKEFILE_LIST)))


include $(__SELF_DIR)/_vars.mk

ifeq ($(USE_PYTHON),1)
include $(__SELF_DIR)/_python.mk
endif

ifeq ($(USE_MGMT),1)
include $(__SELF_DIR)/_mgmt.mk
endif

ifeq ($(USE_DOCKER),1)
include $(__SELF_DIR)/_docker.mk
endif


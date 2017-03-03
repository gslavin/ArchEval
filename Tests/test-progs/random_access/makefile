PROJNAME = random_access
VIEWER = less
reverse = $(if $(wordlist 2,2,$(1)),$(call reverse,$(wordlist 2,$(words $(1)),$(1))) $(firstword $(1)),$(1))

IDIR = .
ODIR = build
SRCDIR = src


BUILD_ENV_BASE = $(ODIR)
BUILD_ENV =  $(BUILD_ENV_BASE)
DEPF =
DEPS = $(patsubst %,$(IDIR)/%,$(DEPF))

OBJF =  main.o 
OBJ = $(patsubst %,$(ODIR)/%,$(OBJF))

DRIVER = $(SRCDIR)/main.c

CC = gcc
CCOPTS = -g -Wall -Wextra -Wno-unused-variable -Wno-missing-field-initializers -I$(IDIR) -I$(ARCH_DIR) -I$(T_IDIR)

.PHONY: all view build env clean rebuild preprocessor
.DEFAULT: build

build : | env all

$(ODIR)/%.o: $(T_SRCDIR)/%.c $(DEPS)
	-@ $(CC) -c -o $@ $< $(CCOPTS)

$(ODIR)/%.o: $(SRCDIR)/%.c $(DEPS)
	-@ $(CC) -c -o $@ $< $(CCOPTS)

all : $(OBJ)
	- $(CC) -o $(PROJNAME) $^ $(CCOPTS)

env: 
	-@ mkdir -p $(BUILD_ENV)

clean :
	-@ \rm -f $(OBJ) $(SRCDIR)/*~ core $(PROJNAME)
	-@ \rmdir $(call reverse, $(BUILD_ENV)) 

rebuild : | clean build

view :
	-@ $(VIEWER) $(DRIVER) $(DEPS)

run :
	-@ ./$(PROJNAME)

preprocessor :
	-@ $(CC) -c $(DRIVER) -E $(CCOPTS)



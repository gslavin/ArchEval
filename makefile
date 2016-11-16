CACTI=cacti

.PHONY: all cacti clean test_clean test

all: cacti

cacti:
	$(MAKE) -C $(CACTI) all

cacti_clean:
	$(MAKE) -C $(CACTI) clean

clean: cacti_clean test_clean

test_clean:
	rm -fr _TestOut

test:
	./tests.sh

CACTI=cacti

.PHONY: all cacti clean

all: cacti

cacti:
	$(MAKE) -C $(CACTI) all

cacti_clean:
	$(MAKE) -C $(CACTI) clean

clean: cacti_clean
	rm -fr _TestOut

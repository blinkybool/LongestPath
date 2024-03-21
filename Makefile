.PHONY: all clean

all:
	$(MAKE) -C ./longestpath/brute

clean:
	$(MAKE) -C ./longestpath/brute clean

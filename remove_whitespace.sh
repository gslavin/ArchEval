#! /bin/sh

# Remove trailing whitespace from all python files
find . -name "*.py" -print0 | xargs -0 sed -i 's/[ \t]*$//'

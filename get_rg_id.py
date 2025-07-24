import re
import sys
regexp=r"([^ ]+)\s{1,}(\S*)"
print(re.match(regexp, sys.argv[1]).group(2))
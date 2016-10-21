import string
import re
import json 

def main():
  f = open("stats.txt", 'r')
  
  out = {'op_class':{}}
  params = ['op_class']
  
  for line in f:
    temp = string.split(line, ' ')
    res = []
    for x in temp:
      if len(x) > 0 and x != '#':
        res.append(x)
      elif x =='#':
        break
    
    if any(x in res[0] for x in params):
      key = re.split('[.:]+', res[0])[2]
      var = re.split('[.:]+', res[0])[3]
      val = res[1]
      out[key][var] = val
  f = open("src.json", 'w')
  f.write(json.dumps(out, sort_keys=True, indent=4))

if __name__ == "__main__":
  main()

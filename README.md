# pycno
Python map overlay software to read CNO and CNOB files.

# status

Very early development. Useful light weight mapping library, but interface likely to change until stable.

# install 

`pip install https://github.com/barronh/pycno/archive/main.zip`

# example usage

By default, this adds coasts and countries to the current axes.

```
import pycno
import matplotlib.pyplot as plt
cno = pycno.cno()
cno.draw()
plt.savefig('coasts_countries.png')
```

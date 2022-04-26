import numerical_methods as num_meth
import matplotlib.pyplot as plt
import numpy as np

x = np.array([0, 1, 2, 3, 4])
y = np.array([1, 6, 2, -1, -2])
xx = np.linspace(0, 4, 20)
yy = []

for i in xx:
    yy.append(num_meth.interp_lagrange(x, y, i, 4))

plt.plot(x, y, marker = 'o')
plt.plot(xx, yy, marker = 'o')
plt.show()

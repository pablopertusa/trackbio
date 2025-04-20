import os
import random
import numpy as np
import tensorflow as tf

def set_seed(seed_value=27):
    """
    Establece la semilla para Python, NumPy y TensorFlow para intentar asegurar
    la reproducibilidad de los experimentos.

    Args:
        seed_value (int): El valor de la semilla a utilizar. Por defecto es 27.
    """
    print(f"Estableciendo todas las semillas a: {seed_value}")

    random.seed(seed_value)

    np.random.seed(seed_value)

    tf.random.set_seed(seed_value)
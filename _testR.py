import rpy2.robjects as ro
ro.r('print("Hello from R")')

import rpy2.robjects as robjects
from rpy2.robjects import pandas2ri

# Activate automatic conversion of pandas data frames to R data frames
pandas2ri.activate()

# Install the mirt library
# instalar somente uma vez
# robjects.r('install.packages("mirt")')

robjects.r('library(mirt)')
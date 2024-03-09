import rpy2.robjects as ro
ro.r('print("Hello from R")')

from rpy2.robjects.packages import importr

psyirt = importr('psyirt')
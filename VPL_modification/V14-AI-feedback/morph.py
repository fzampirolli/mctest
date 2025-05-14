
"""
Copyright 2014 by Francisco de Assis Zampirolli from UFABC
License MIT
https://github.com/fzampirolli/morph
25 January 2024
"""
import matplotlib.pyplot as plt, numpy as np, cv2, requests, sys, subprocess
from PIL import Image
from skimage import io
class mm(object):
  """ A helper class for image processing tasks. """
  
  IN_COLAB = 'google.colab' in sys.modules #### INICIALIZATION ####
  count_Images = 0

  def __init__(self):
    pass

  @staticmethod
  def install(packages=['matplotlib','numpy','opencv-python']):
    """This function will install the packages
    input: <packages> list of packages.
    Examples: mm.install(['matplotlib', 'scikit-image']) """
    for package in packages:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

  #### IMAGE UTILITIES: CREATE, DRAW, CHECK ####

  @staticmethod
  def read(file):
    """ Reads an image from a local file path or URL.
    input: <str> File path or URL (full or 'id=keyGoogleDrive').
    output: the read image.
    Examples:
    img_local  = mm.read('image.png')
    img_url    = mm.read('https://example.com/image.jpg')
    img_gdrive = mm.read('id=keyGoogleDrive')"""
    if file.startswith(('http', 'id=')):
        url, pre = '', 'https://drive.google.com/file/d/'
        if pre in file:
            url = 'https://drive.google.com/uc?export=view&id='
            url += file[len(pre):].split('/')[0]
        elif file.startswith('id='):
            url = 'https://drive.google.com/uc?export=view&id=' + file[3:]
        else:
            url = file
        return io.imread(url)
    else:
        return cv2.imread(file)

  @staticmethod
  def color(img):
    """ Converts an image to RGB color space.
    input: <numpy.ndarray> Image in BGR, grayscale, or RGBA format.
    output: RGB image in <numpy.ndarray> format.
    Example:
    img     = mm.read('image.png')
    img_rgb = mm.color(img) """
    if len(img.shape) == 2:
        return cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
    elif len(img.shape) == 3 and img.shape[2] == 4:
        return cv2.cvtColor(img, cv2.COLOR_RGBA2RGB)
    elif len(img.shape) == 3 and img.shape[2] == 3:
        return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    else:
        raise ValueError("Unsupported image format.")

  @staticmethod
  def gray(img):
    """ Converts a color image to grayscale.
    input: <numpy.ndarray> Input color image.
    output: grayscale image.
    Examples:
    img = mm.read('image.png')
    img_gray = mm.gray(img) """
    if len(img.shape) == 3 and img.shape[2] == 4:
        return cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)
    else:
        return cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

  @staticmethod
  def threshold(img, limiar=0):
    """ Thresholds an input image by a threshold value or using Otsu's method.
    input: <numpy.ndarray> Input image to be thresholded.
    output: <numpy.ndarray> Thresholded image.
    Examples:
    img = mm.read('image.png')
    th = mm.threshold(img) """
    if limiar == 0:
        value, th = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    else:
        value, th = cv2.threshold(img, limiar, 255, cv2.THRESH_BINARY)
    return th

  @staticmethod
  def show(*args):
    """ This function will draw images f
    input: <*args> set of images f_i, where i>0 is binary image
    output: image drawing
    Example:
    f1, f2 = np.zeros((100, 100,3)),  np.zeros((100, 100))
    f2[50:60, 50:60] = 1
    mm.show(f1, f2)"""
    colors = [[255, 0, 0], [0, 255, 0], [0, 0, 255], [255, 0, 255], [0, 255, 255],
     [255, 255, 0], [255, 50, 50], [50, 255, 50]] # red, green, blue, cyan, ...
    f = args[0].copy()
    for i in range(1,len(args)):
        if i >= len(colors):
            break
        f[args[i] > 0] = colors[i-1]
    _ = plt.imshow(f, "gray")
    if not mm.IN_COLAB:
        plt.savefig('fig_' + str(mm.count_Images).zfill(4) + '.png')
        mm.count_Images += 1

  @staticmethod
  def readImg(h, w):
    """ This function reads an image from input and returns it as a NumPy array.
    input: size of image: height and width
    output: image
    Example:
      mm.readImg(3, 4)
      0 1 0 0
      1 1 1 1
      0 1 0 0
      The function will return the following NumPy array:
      array([[0, 1, 0, 0],
             [1, 1, 1, 1],
             [0, 1, 0, 0]]) """
    m = np.zeros((h, w), dtype='uint8')
    # Loop over each row of the image and read it from standard input.
    for l in range(h):
        # Split the row into individual pixel values and convert them to integers.
        m[l] = [int(i) for i in input().split() if i]
    return m

  @staticmethod
  def readImg2():
    """ This function reads an image of varying size from standard input.
    Example:
      mm.readImg2()
      255   0  255
      128  64  192
      0   192  128 """
    b = []
    read_row = input()
    while read_row:  # Read each line of the input until there is no more input.
      # Split the line into individual pixel values and convert them to integers.
      row = [int(i) for i in read_row.split() if i]
      b.append(row) # Add the row to the list of rows.
      read_row = input()
    return np.array(b).astype('uint8')

  @staticmethod
  def randomImage(h, w, maxValue=9):
    """ Creates a random image of size h x w with integer values in [0,maxValue].
    input: size of image: height, width and max value
    output: image
    Example:
      mm.randomImage(3, 3, maxValue=5)
      The function will return a random NumPy array, such as:
      array([[2, 1, 3],
             [0, 4, 2],
             [5, 1, 5]], dtype=uint8)"""
    return np.random.randint(maxValue + 1, size=(h, w)).astype('uint8')

  @staticmethod
  def drawImage(f):
    """ Converts the input image f into a string representation suitable for printing.
    Args: f (ndarray): The input image.
    Returns: A string representing the input image.
    Example:
        string_representation = mm.drawImage(f)
        print(string_representation) """
    l, c = f.shape
    if np.min(f) < 0:
        digits = '%' + str(1 + len(str(np.max(f)))) + 'd '
    else:
        digits = '%' + str(len(str(np.max(f)))) + 'd '
    #print('"'+digits+'"')
    string_representation = ''
    for i in range(l):
        for j in range(c):
            string_representation += digits % f[i][j]
        string_representation += '\n'
    return string_representation

  @staticmethod
  def drawImagePlt(f):
    """ Displays the input image f using Matplotlib.
    Args: f (ndarray): The input image.
    Example: drawImagePlt(f) """
    h, w = f.shape
    m = min(h, w)
    # Set up the plot.
    plt.figure(figsize=(m, m))
    plt.rcParams['xtick.bottom'] = plt.rcParams['xtick.labelbottom'] = False
    plt.rcParams['xtick.top'] = plt.rcParams['xtick.labeltop'] = True
    # Display the image.
    _ = plt.imshow(f, 'gray')
    # Set the tick marks and labels.
    plt.yticks(range(h))
    plt.xticks(range(w))
    plt.ylabel('y')
    plt.xlabel('x')
    # Add grid lines.
    [plt.axvline(i + .5, 0, h, color='r') for i in range(w - 1)]
    [plt.axhline(j + .5, 0, w, color='r') for j in range(h - 1)]

  @staticmethod
  def drawImageKernel(f,B,x,y):
      """This function will draw image f, considering a kernel
      input:
       - f: input image
       - B: kernel
       - x,y: center pixel of kernel
      output:
       - string: image drawing
      """
      h,w = f.shape
      Bh, Bw = B.shape
      Bcx, Bcy = Bw//2, Bh//2
      m = min(h,w)
      plt.figure(figsize=(m,m))
      plt.rcParams['xtick.bottom'] = plt.rcParams['xtick.labelbottom'] = False
      plt.rcParams['xtick.top'] = plt.rcParams['xtick.labeltop'] = True
      plt.imshow(f,'gray')
      plt.yticks(range(h))
      plt.xticks(range(w))
      plt.ylabel('y')
      plt.xlabel('x')
      plt.title('Processando pixel (x,y)=(%d,%d)'%(x,y))
      [plt.axvline(i+.5, 0, h, color='r') for i in range(w-1)]
      [plt.axhline(j+.5, 0, w, color='r') for j in range(h-1)]
      [plt.plot([i+x-Bcx-.5,i+x-Bcx-.5], [y-Bcy-.5,Bh+y-Bcy-.5], color='y', linewidth=5) for i in range(Bw+1)]
      [plt.plot([x-Bcx-.5,x-Bcx+Bw-.5], [j+y-Bcy-.5, j+y-Bcy-.5], color='y', linewidth=5) for j in range(Bh+1)]

  @staticmethod
  def lblshow(f,border=3):
      """This function will draw image f with each component has a color
      input:
       - f: input image
       - border: border optional [defaul=2]
      output:
       - y: color image
      """
      from skimage import measure #<<<<<<<<<<<<<<<<<<
      r = f
      # Find contours at a constant value of 0.8
      contours = measure.find_contours(r, 0.0)

      fig, ax = plt.subplots()
      ax.imshow(r, interpolation='nearest', cmap=plt.cm.gray)

      for n, contour in enumerate(contours):
        ax.plot(contour[:, 1], contour[:, 0], linewidth=border)

      ax.axis('image')
      ax.set_xticks([])
      ax.set_yticks([])
      _=plt.imshow(f,"gray")
      if not mm.IN_COLAB:
            plt.savefig('fig_'+str(mm.count_Images).zfill(4)+'.png')
            mm.count_Images += 1

  @staticmethod
  def binary(f):
    """This function checks whether the image is binary
    input:
     - f: input image
    output:
     - y: True if binary image
    """
    hist,bins = np.histogram(f.ravel(),256,[0,256])
    if np.count_nonzero(hist > 0) == 2: # binary
      return True
    elif np.count_nonzero(hist > 0) > 2:
      return False
    else:
      return None
    
  ##### OPERATIONS ON IMAGES (DO NOT USE NEIGHBORHOOD) #####
  
  @staticmethod
  def subm(f,g):
    """This fuction will be subtract f by g
    input:
      - f: input image
      - g: input image
    output:
      - y: result of subtraction
    """
    #return cv2.subtract(f,g)
    return np.maximum(f-g,0)

  @staticmethod
  def addm(f,g):
    """This fuction will be add f by g
    input:
      - f: input image
      - g: input image
    output:
      - y: result of add
    """
    return cv2.add(f,g)
   
  @staticmethod
  def union(f,g):
    """This fuction will be union f by g
    input:
      - f: input image
      - g: input image
    output:
      - y: result of add
    """
    return np.maximum(f,g)

  @staticmethod
  def hist(img):
    """Função para retornar o histograma
      Sintaxe:
        hist = hist(img)
        input: image
        output hist
    """
    H = np.zeros(np.max(img)+1, dtype=int)
    for i in range(len(img.flatten())):
        cor = img.flatten()[i]
        H[cor] += 1
    return np.asarray(H)

  @staticmethod
  def histPlus(img):
    """Função para retornar o histograma e todos os pixels de cada cor
      Sintaxe:
        hist, dict = histPlus(img)
        input: image
        output hist e dict
    """
    H = np.zeros(np.max(img)+1, dtype=int)
    vet = {} # cria um dicionário para os pixels de cada cor
    for i in range(len(img.flatten())):
        cor = img.flatten()[i]
        H[cor] += 1
        if str(cor) in vet.keys():
          vet[str(cor)].append(i)
        else:
          vet[str(cor)] = [i]
    return H,vet

  @staticmethod
  def equalizacao(image):
    """Função para retornar a imagem equalizada pelo valor máximo
      Sintaxe:
        imgEqu = equalizacao(image)
        input: image
        output imgEqu
    """
    @staticmethod
    def somaAcumulada(prob):
        soma = np.zeros(len(prob))
        soma[0] = prob[0]
        for i in range(1,len(prob)):
            soma[i] = soma[i-1]+prob[i]
        return np.asarray(soma)

    hist = mm.hist(image)      # histograma
    prob = hist/sum(hist)      # probabilidades
    soma = somaAcumulada(prob) # função de distribuição acumulada
    soma = soma*(np.max(image))# multiplicando pelo valor máximo da img
      
    soma = np.round(soma) # arredondando para obter os níveis de cinza correspondetes
      
    l,c = image.shape
    imgEqua = np.zeros([l,c])
    for i in range(l):
        for j in range(c):
            imgEqua[i,j] = soma[image[i,j]]
    return imgEqua.astype('int')
    
  #### MINKOWSKI SUM ####

  @staticmethod
  def sesum(b,n=0):
    """This function will be create a structure function nB by Minkowski sum B
    input:
      - b: structure fuction
      - n: number of sum
    output:
      - y: result of Minkowski sum
    """
    def _sesum(nb,b):
      h,w = b.shape
      nbh,nbw = nb.shape
      H = nbh+h-1 if h%2 else nbh+h
      W = nbw+w-1 if w%2 else nbw+w
      Hc,Wc = H//2, W//2
      r = np.zeros((H,W)).astype('uint8')
      r[h//2:-(h//2),w//2:-(w//2)] = nb
      return cv2.dilate(r,b).astype('uint8')

    B = b.copy()
    for i in range(n):
      B = _sesum(B,b)
    return B
    
  @staticmethod
  def sebox(n=0):
    """This function will be create a box structure function nB by Minkowski sum B
    input:
      - n: number of sum
    output:
      - y: result of Minkowski sum
    """
    B = mm.sebox()
    return mm.sesum(B,n)
   
  @staticmethod
  def secross(n=0):
    """This function will be create a cross structure function nB by Minkowski sum B
    input:
      - n: number of sum
    output:
      - y: result of Minkowski sum
    """
    B = mm.sebox()
    B[0,0] = B[0,2] = B[2,0] = B[2,2] = 0
    return mm.sesum(B,n)
    
  @staticmethod
  def sedisk(n=3):
    """This function will be create a disk structure function
    input:
      - n: number of sum
    output:
      - y: result of disk
    """
    return cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(n,n))
    
  #### BASIC MORPHOLOGICAL OPERATORS ####

  @staticmethod
  def ero(f,Bc=np.zeros((3,3),dtype= 'uint8')):
      """This function will create an erosion of f by Bc
      input:
       - f: input image
       - Bc: structuring element
      output:
       - y: result of filter
      """
      try:
        return cv2.erode(f,Bc)
      except: # with weight in Bc
        return mm.ero1(f,Bc)

  @staticmethod
  def dil(f,Bc=np.zeros((3,3),dtype= 'uint8')):
      """This function will create an dilate of f by Bc
      input:
       - f: input image
       - Bc: structuring element
      output:
       - y: result of filter
      """
      try:
        return cv2.dilate(f,Bc)
      except: # with weight in Bc
        return mm.dil1(f,Bc)
        
  @staticmethod
  def ero0(f,Bc=np.zeros((3,3),dtype= 'uint8')):
      """This function will create an erosion of f by Bc
      input:
       - f: input image
       - Bc: structuring element
      output:
       - y: result of filter
      """
      H,W = f.shape
      Bh, Bw = Bc.shape
      g = f.copy() # nas listas, as vezes eu uso assim
     
      # para varrer imagem na ordem raster
      for y in range(H): # para cada linha y
        for x in range(W): # para cada coluna x
     
          # para cada vizinho de (x,y)
          for by in range(Bh):
            for bx in range(Bw):
              viz_y = int(y + by - Bh/2 + 0.5)
              viz_x = int(x + bx - Bw/2 + 0.5)

              # verificar o domínion da image
              if  Bc[by,bx] and 0 <= viz_y < H and 0 <= viz_x < W:
     
                # para calcular o mínino dos vizinhos
                if g[y,x] > f[viz_y,viz_x]:
                  g[y,x] = f[viz_y,viz_x]
      return g

  @staticmethod
  def dil0(f,Bc=np.zeros((3,3),dtype= 'uint8')):
      """This function will create a dilate of f by Bc
      input:
       - f: input image
       - Bc: structuring element
      output:
       - y: result of filter
      """
      H,W = f.shape
      Bh, Bw = Bc.shape
      Bcy, Bcx = Bh/2, Bw/2
      g = f.copy() # nas listas, as vezes eu uso assim
     
      # para varrer imagem na ordem raster
      for y in range(H): # para cada linha y
        for x in range(W): # para cada coluna x
     
          # para cada vizinho de (x,y)
          for by in range(Bh):
            for bx in range(Bw):
              viz_x = int(x + bx - Bcx + 0.5)
              viz_y = int(y + by - Bcy + 0.5)
     
              # verificar o domínion da image
              if Bc[by,bx] and 0 <= viz_x < W and 0 <= viz_y < H:
     
                # para calcular o máximo dos vizinhos
                if g[y,x] < f[viz_y,viz_x]:
                  g[y,x] = f[viz_y,viz_x]
      return g

  @staticmethod
  def ero1(f,b=np.zeros((3,3),dtype= 'uint8')):
      """This function will create an erosion of f by b
      input:
       - f: input image
       - b: structuring element
      output:
       - y: result of filter
      """
      H,W = f.shape
      Bh, Bw = b.shape
      g = f.copy() # nas listas, as vezes eu uso assim
     
      # para varrer imagem na ordem raster
      for y in range(H): # para cada linha y
        for x in range(W): # para cada coluna x
     
          # para cada vizinho de (x,y)
          for by in range(Bh):
            for bx in range(Bw):
              viz_y = int(y + by - Bh/2 + 0.5)
              viz_x = int(x + bx - Bw/2 + 0.5)

              # verificar o domínion da image
              if  0 <= viz_y < H and 0 <= viz_x < W:
     
                # para calcular o mínino dos vizinhos
                if g[y,x] > f[viz_y,viz_x] - b[by,bx]:
                  g[y,x] = f[viz_y,viz_x] - b[by,bx]
      return g

  @staticmethod
  def dil1(f,b=np.zeros((3,3),dtype= 'uint8')):
      """This function will create a dilate of f by b
      input:
       - f: input image
       - b: structuring element
      output:
       - y: result of filter
      """
      H,W = f.shape
      Bh, Bw = b.shape
      g = f.copy() # nas listas, as vezes eu uso assim
     
      # para varrer imagem na ordem raster
      for y in range(H): # para cada linha y
        for x in range(W): # para cada coluna x
     
          # para cada vizinho de (x,y)
          for by in range(Bh):
            for bx in range(Bw):
              viz_y = int(y + by - Bh/2 + 0.5)
              viz_x = int(x + bx - Bw/2 + 0.5)

              # verificar o domínion da image
              if  0 <= viz_y < H and 0 <= viz_x < W:
     
                # para calcular o mínino dos vizinhos
                if g[y,x] < f[viz_y,viz_x] + b[by,bx]:
                  g[y,x] = f[viz_y,viz_x] + b[by,bx]
      return g

  @staticmethod
  def correlacao0(F, kernel, bias):
    """This function will create an correlation of f by b
    input:
    - f: input image
    - b: kernel
    output:
    - y: result of filter
    """
    Bh, Bw = kernel.shape
    if (Bh == Bw): # apenas para kernel quadrado
        H, W = f.shape
        H = H - Bh + 1 # REMOVO A BORDA!!!
        W = W - Bw + 1 # REMOVO A BORDA!!!
        new_f = np.zeros((H,W))
        for i in range(H): # para cada linha i
          for j in range(W): # para cada coluna j
            new_f[i][j] = np.sum(f[i:i+Bh, j:j+Bw]*kernel) + bias

    return new_f.astype(np.uint8)
    
   ##### MORPHOLOGICAL OPERATORS USING DILATATION OR EROSION #####

  @staticmethod
  def gradm(f,b=np.zeros((3,3),dtype= 'uint8')):
    """This fuction will be dilate f by b minus erodel f by b
    input:
      - f: input image
      - b: neighbors
    output:
      - y: result of condictional dilations
    """
    return mm.subm(mm.dil(f,b),mm.ero(f,b))

  @staticmethod
  def cero(f,g,b=np.zeros((3,3),dtype= 'uint8'),n=1):
    """This fuction will be erode g with maximum f, n times
    input:
      - f: input image
      - g: mark image
      - b: neighbors
      - n: number of iterations
    output:
      - y: result of condictional erodes
    """
    y = np.maximum(f,g)
    for i in range(n):
      d = cv2.erode(y,b)
      y = np.maximum(d,g)
    return y
    
  @staticmethod
  def cdil(f,g,b=np.zeros((3,3),dtype= 'uint8'),n=1):
    """This fuction will be dilate g with minimum f, n times
    input: 
      - f: input image
      - g: mark image
      - b: neighbors
      - n: number of iterations
    output:
      - y: result of condictional dilations
    """
    y = np.minimum(f,g)
    for i in range(n):
      d = cv2.dilate(y,b)
      y = np.minimum(d,g)
    return y

  @staticmethod
  def infrec(f,g,b=np.zeros((3,3),dtype= 'uint8')):
    """This function will be dilate g with minimum f, until converge
    input: 
      - f: input image
      - g: mark image
      - b: neighbors
    output:
      - y: result of inf-reconstruction
    """
    y = np.minimum(f,g)
    y1 = np.zeros_like(f)
    while not np.array_equal(y,y1):
      y1 = y
      d = cv2.dilate(y,b)
      y = np.minimum(d,g)
    return y
  
    
  @staticmethod
  def suprec(f,g,b=np.zeros((3,3),dtype= 'uint8')):
    """This function will be erode g with maximum f, until converge
    input:
      - f: input image
      - g: mark image
      - b: neighbors
    output:
      - y: result of sup-reconstruction
    """
    y = np.maximum(f,g)
    y1 = np.ones_like(f)*255
    while not np.array_equal(y,y1):
      y1 = y
      d = cv2.erode(y,b)
      y = np.maximum(d,g)
    return y
    
  @staticmethod
  def closerec(f,b=np.zeros((3,3),dtype= 'uint8'),bc=np.zeros((3,3),dtype= 'uint8')):
    """This function will be erode g with maximum f, until converge
    input:
      - f: input image
      - b: mark image
      - bc: neighbors
    output:
      - y: result of sup-reconstruction
    """

    return mm.suprec(f, mm.dil(f,b), bc)
    
    
  @staticmethod
  def areaopen(f,a):
    """This function will be dilate g with minimum f, until converge
    input:
      - f: input image
      - a: area
      #- Bc: neighbors
    output:
      - y: result of areaopen
    """
    def _areaopen(f,a):
      y = np.zeros(f.shape).astype(int)
      if mm.binary(f): # binary
        num_labels, labels_im = cv2.connectedComponents(f)
        for i in range(1,num_labels):
          area = np.sum(labels_im[labels_im==i] > 0)
          if area > a: # filtra por área aproximada
            #print('area:',area)
            y[labels_im==i] = area
      else: # gray scale
        hist,bins = np.histogram(f.ravel(),256,[0,256])
        for cor,h in enumerate(hist):
          if h and cor:
            #print('>>cor:',cor)
            ret, fcor = cv2.threshold(f, cor, 255, cv2.THRESH_BINARY)
            fo = _areaopen(fcor,a)
            if np.amax(fo) == 0:
              break
            y += fo
      return y
    return _areaopen(f,a)
    
    
  @staticmethod
  def asf(f,filter='OC',b=np.zeros((3,3),dtype= 'uint8'),n=1):
    """This function will create an alternating sequential filter
    input:
      - f: input image
      - b: structuring fuctions
      - n: number of iterations
      - filter: 'OC', 'CO', 'OCO', 'COC' [Default: 'OC']
    output:
      - y: result of filter
    ATENÇÃO: 
    """
    filter = filter.upper()
    y = f.copy()
    if filter=='OC':
      for i in range(n):
        bi = mm.sesum(b,i)
        y = cv2.morphologyEx(y, cv2.MORPH_OPEN, bi)
        y = cv2.morphologyEx(y, cv2.MORPH_CLOSE, bi)
    elif filter=='CO':
      for i in range(n):
        bi = mm.sesum(b,i)
        y = cv2.morphologyEx(y, cv2.MORPH_CLOSE, bi)
        y = cv2.morphologyEx(y, cv2.MORPH_OPEN, bi)
    elif filter=='OCO':
      for i in range(n):
        bi = mm.sesum(b,i)
        y = cv2.morphologyEx(y, cv2.MORPH_OPEN, bi)
        y = cv2.morphologyEx(y, cv2.MORPH_CLOSE, bi)
        y = cv2.morphologyEx(y, cv2.MORPH_OPEN, bi)
    elif filter=='COC':
      for i in range(n):
        bi = mm.sesum(b,i)
        y = cv2.morphologyEx(y, cv2.MORPH_CLOSE, bi)
        y = cv2.morphologyEx(y, cv2.MORPH_OPEN, bi)
        y = cv2.morphologyEx(y, cv2.MORPH_CLOSE, bi)
      
    return y

  @staticmethod
  def openth(f,b=np.zeros((3,3),dtype= 'uint8')):
      return mm.subm(f,cv2.morphologyEx(f, cv2.MORPH_OPEN, b))

  @staticmethod
  def openth1(f,b=np.zeros((3,3),dtype= 'uint8')):
    return mm.subm(f, mm.dil1(mm.ero1(f,b),b) )

  @staticmethod
  def closeth(f,b=np.zeros((3,3),dtype= 'uint8')):
      return mm.subm(cv2.morphologyEx(f, cv2.MORPH_CLOSE, b),f)
       
  @staticmethod
  def closerecth(f,b=np.zeros((3,3),dtype= 'uint8')):
      return mm.subm(cv2.morphologyEx(f, cv2.MORPH_CLOSE, b),f)

  @staticmethod
  def open(f,b=np.zeros((3,3),dtype= 'uint8')):
      return cv2.morphologyEx(f, cv2.MORPH_OPEN, b)
  
  @staticmethod
  def close(f,b=np.zeros((3,3),dtype= 'uint8')):
      return cv2.morphologyEx(f, cv2.MORPH_CLOSE, b)
   
  @staticmethod
  def water0(f,b=np.zeros((3,3),dtype= 'uint8'), op='region'):
      """This function will create the watershed
        input:
          - f: input binary image
          - op: regions of watershed

        output:
          - y: watershed
      """
      f = mm.label0(f,b)
      h,w = f.shape
      bh, bw = b.shape
      g = f.copy()
      while np.amin(g)==0:
        for x in range(h):
          for y in range(w):
              for bx in range(bh):
                for by in range(bw):
                  viz_x = int(x + bx - bh/2 + 0.5)
                  viz_y = int(y + by - bw/2 + 0.5)
                  if 0 <= viz_x < h and 0 <= viz_y < w:
                    if g[x,y] == 0 and g[x,y] < f[viz_x,viz_y]:
                      g[x,y] = f[viz_x,viz_y]
        f = g.copy()
        
      if op == 'region':
        return g
      elif op == 'line':
        return mm.gradm(g,mm.secross())
	
  @staticmethod
  def waterB(f,m,b=np.zeros((3,3),dtype= 'uint8'), op='region'):
      """This function will create the watershed, process only border pixel of each object
        input:
          - f: input binary image
          - op: regions of watershed

        output:
          - y: watershed
      """
      m = mm.label0(m,b)
      h,w = m.shape
      bh, bw = b.shape
      queue = []
      for x in range(h):
        for y in range(w):
          if m[x,y]:
            for bx in range(bh):
              for by in range(bw):
                viz_x = int(x + bx - bh/2 + 0.5)
                viz_y = int(y + by - bw/2 + 0.5)
                if 0 <= viz_x < h and 0 <= viz_y < w:
                  if not m[viz_x,viz_y]:
                    queue.append([abs(f[x,y]-f[viz_x,viz_y]), x, y])
                    
      while len(queue):
        #queue = sorted(queue, key=lambda a:a[0])
        cor_diff,x,y = queue.pop(0)
        cor = m[x,y]
        for bx in range(bh):
          for by in range(bw):
            viz_x = int(x + bx - bh/2 + 0.5)
            viz_y = int(y + by - bw/2 + 0.5)
            if 0 <= viz_x < h and 0 <= viz_y < w:
              if not m[viz_x,viz_y]:
                m[viz_x,viz_y] = cor
                queue.append([abs(f[x,y]-f[viz_x,viz_y]), viz_x, viz_y])

      if op == 'region':
        return m
      elif op == 'line':
        return mm.gradm(m,mm.secross())
        
  @staticmethod
  def watershed(f,mark,op='region'):
      """This function will create the watershed
        input:
          - f: input image
            - f==[] # binary watershed by skimage
            - else  # condictional watershed by cv2
          - mark: markers image
          - op: region or line [default: region]

        output:
          - y: watershed
      """

      mark = mark*255 if np.amax(mark)==1 else mark
        
      if len(f): # condictional watershed by cv2
      
        ret, markers = cv2.connectedComponents(mark)
        w = cv2.watershed(f,markers)
        if op=='line':
          f[markers == -1] = [255,0,0]
          return f
        else:
          return w
          
      else: # binary watershed by skimage
      
        from scipy import ndimage as ndi
        from skimage.segmentation import watershed
        fones = np.ones_like(mark)*255
        markers = ndi.label(mark)[0]
        w = watershed(fones, markers, mask=fones)

        if op=='line':
          return np.array((w-cv2.erode(w.astype('uint16'),mm.sebox()))>0).astype('uint16')
        else:
          return w

  @staticmethod
  def regmax(f,b=np.ones((3,3),dtype='uint8')):
    """This function will be calculate region maximum
    input:
      - f: input image
      - b: neighbors
    output:
      - y: result of regmax
    """
    if np.amax(f)<=255:
       k = 255
    else:
       k = 65535
    fminus = mm.subm(f,1)
    g = mm.subm(f,mm.infrec(fminus,f,b))
    return mm.union(mm.threshold(g,0),mm.threshold(f,k))

  @staticmethod
  def regmin(f,b=np.ones((3,3),dtype='uint8')):
    """This function will be calculate region minimum
    input:
      - f: input image
      - b: neighbors
    output:
      - y: result of regmax
    """
    fplus = mm.addm(f,1);
    g = mm.subm(mm.suprec(fplus,f,b),f);
    return mm.union(mm.threshold(g,1),mm.threshold(f,0))
    
  def blob(f,op='area',border=1,precision=0.01,show='True'):
    """This function will be calculate topology of each connect component
    input:
      - f: input image
      - op: 'area', 'perimeter', etc [default='area']
      - border: border of lines [default=1]
      - precision: precision of polygonon [default=0.01]
      - show=True, return image, else, return measure
    output:
      - y: image with op or measure
    """
    if mm.binary(f): # binary
      measures = []
      cont, _ = cv2.findContours(f.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
      color_img = cv2.cvtColor(f, cv2.COLOR_GRAY2RGB)
      if op=='area':
        color_img = np.zeros_like(f).astype('uint32')
        num_labels, labels_im = cv2.connectedComponents(f)
        for i in range(1,num_labels):
            area = np.sum(labels_im[labels_im==i] > 0)
            measures.append(area)
            color_img[labels_im==i] = area

      elif op=='textLabel':
        for k,c in enumerate(cont):
            x,y,w,h = cv2.boundingRect(c)
            measures.append(k+1)
            cv2.putText(color_img, str(k+1),(x+w//3, y+h//2), cv2.FONT_HERSHEY_SIMPLEX, 0.2,(255,0,0),border,cv2.LINE_AA)
      
      elif op=='textPer':
        cont, _ = cv2.findContours(f.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        color_img = cv2.cvtColor(f, cv2.COLOR_GRAY2RGB)
        for k,c in enumerate(cont):
            perimeter = int(cv2.arcLength(c,True))
            measures.append(perimeter)
            x,y,w,h = cv2.boundingRect(c)
            cv2.putText(color_img, str(perimeter),(x+w//3, y+h//2), cv2.FONT_HERSHEY_SIMPLEX, 0.2,(255,0,0),border,cv2.LINE_AA)

      elif op=='textArea':
        cont, _ = cv2.findContours(f.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        color_img = cv2.cvtColor(f, cv2.COLOR_GRAY2RGB)
        for k,c in enumerate(cont):
            area = int(cv2.contourArea(c))
            measures.append(area)
            x,y,w,h = cv2.boundingRect(c)
            cv2.putText(color_img, str(area),(x+w//3, y+h//2), cv2.FONT_HERSHEY_SIMPLEX, 0.2,(255,0,0),border,cv2.LINE_AA)

      elif op=='box':
        color_img = cv2.cvtColor(f, cv2.COLOR_GRAY2RGB)
        cont, _ = cv2.findContours(f.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        for c in cont:
          rect = cv2.minAreaRect(c)
          box = cv2.boxPoints(rect)
          box = np.int0(box)
          measures.append(box)
          cv2.drawContours(color_img,[box],0,(255,0,0),border)
      
      elif op=='rect':
        color_img = cv2.cvtColor(f, cv2.COLOR_GRAY2RGB)
        cont, _ = cv2.findContours(f.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        for c in cont:
          x,y,w,h = cv2.boundingRect(c)
          measures.append([x,y,w,h])
          cv2.rectangle(color_img,(x,y),(x+w,y+h),(0,255,0),border)

      elif op=='circle':
        color_img = cv2.cvtColor(f, cv2.COLOR_GRAY2RGB)
        cont, _ = cv2.findContours(f.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        for c in cont:
          (x,y),radius = cv2.minEnclosingCircle(c)
          center = (int(x),int(y))
          radius = int(radius)
          measures.append([center,radius])
          cv2.circle(color_img,center,radius,(0,255,0),border)

      elif op=='ellipse':
        color_img = cv2.cvtColor(f, cv2.COLOR_GRAY2RGB)
        cont, _ = cv2.findContours(f.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        for c in cont:
          ellipse = cv2.fitEllipse(c)
          measures.append(ellipse)
          cv2.ellipse(color_img,ellipse,(0,255,0),border)

      elif op=='convex':
        color_img = cv2.cvtColor(f, cv2.COLOR_GRAY2RGB)
        cont, _ = cv2.findContours(f.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        for c in cont:
          hull = cv2.convexHull(c)
          measures.append(hull)
          cv2.drawContours(color_img,[hull],0,(255,0,0),border)

      elif op=='poly':
        color_img = cv2.cvtColor(f, cv2.COLOR_GRAY2RGB)
        cont, _ = cv2.findContours(f.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        for c in cont:
          epsilon = precision*cv2.arcLength(c,True)
          approx = cv2.approxPolyDP(c,epsilon,True)
          measures.append(approx)
          cv2.drawContours(color_img,[approx],0,(255,0,0),border)

      elif op=='line':
        color_img = cv2.cvtColor(f, cv2.COLOR_GRAY2RGB)
        cont, _ = cv2.findContours(f.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        for c in cont:
          ellipse = cv2.fitEllipse(c)
          cv2.ellipse(color_img,ellipse,(255,0,0),border)
          
          rows,cols = f.shape[:2]
          [vx,vy,x,y] = cv2.fitLine(c, cv2.DIST_L2,0,0.01,0.01)
          measures.append([vx,vy,x,y])
          lefty = int((-x*vy/vx) + y)
          righty = int(((cols-x)*vy/vx)+y)
          cv2.line(color_img,(cols-1,righty),(0,lefty),(0,255,0),border)

      if show:
        mm.show(color_img)
        return color_img
      else:
        return measures
   
  def blobAll(f,border=1,precision=0.01,show='False'):
    """This function will be calculate topology of each connect component
    input:
      - f: input image
      - border: border of lines [default=1]
      - precision: precision of polygonon [default=0.01]
      - show=False, return measure
    output:
      - y: measures
    """
    num_labels, labels = cv2.connectedComponents(f)
    measures_all = ['textLabel','textArea','textPer','box','rect',
                'circle','ellipse','convex','poly', 'line']
    measures_vect = {k:[] for k in measures_all}
    for i in range(np.amax(labels)):
      for m in measures_all:
        aux = np.zeros_like(labels).astype('uint8')
        aux[labels==i] = 255
        measures_vect[m].append(mm.blob(aux,m,1,0.01,False)[0])
    return measures_vect
    
  def intersec(f1,f2):
    return np.minimum(f1,f2)
  
  @staticmethod
  def toggle(f,f1,f2, op='gray'):
    """This function will be calculate label of each connect component
    input:
      - f: input image
      - f1: input image
      - f2: input image
      - op: input image
    output:
      - y: image with op
    """
    f11 = mm.subm(f,f1)
    f22 = mm.subm(f2,f)
    g = np.logical_and((f11 <= f),(f <= f22))
    if op == 'gray':
      t = np.array(g,dtype='uint8')*255
      g = mm.union(mm.intersec(mm.neg(t), f1), mm.intersec(t,f2))
    return g

  @staticmethod
  def label(f):
    """This function will be calculate label of each connect component
    input:
      - f: input image
    output:
      - y: image with op
    """
    num_labels, labels_im = cv2.connectedComponents(f)
    return labels_im
    
  @staticmethod
  def label0(f,b=np.ones((3,3),dtype='uint8')):
    """This function will be calculate label of each connect component
    input:
      - f: input image
      - b: structure element
    output:
      - y: image with op
    """
    h,w = f.shape
    bh, bw = b.shape

    g = np.zeros(f.shape).astype(int)
    cor = 1
    pilha = []
    for x in range(h):
     for y in range(w):

      if (f[x,y]) and not g[x,y]: # buscar pixel de objeto não pintado

        pilha.append([x,y]) # colocar na pilha pixel p=[x,y]

        while pilha: # laço para pintar todos os pixel de cada objeto com cor
          i,j=pilha.pop() # retirar da pilha pixel q=[i,j]
          g[i,j] = cor

          # para cada vizinho de (i,j)
          for bx in range(bh):
            for by in range(bw):
              if b[bx,by]:
                viz_x = int(i + bx - bh/2 + 0.5)
                viz_y = int(j + by - bw/2 + 0.5)
                # verificar o domínion da image
                if 0 <= viz_x < h and 0 <= viz_y < w:
                  if f[viz_x, viz_y] and not g[viz_x, viz_y]: # colocar na pilha
                      pilha.append([viz_x, viz_y]) # somente pixels não visitados e =1

        cor+=1 # incremento para pintar o próximo objeto
    return g
    
  @staticmethod
  def dist(f):
    """This function will be calculate euclidean distance of each connect component
    input:
      - f: input image
    output:
      - y: image with op
    """
    y = cv2.distanceTransform (f,cv2.DIST_L2,5)
    if np.amax(y)<=255:
      y = y.astype('uint8')
    else:
      y = y.astype('uint16')
    return y
    
  @staticmethod
  def dist1(f,b):
    """This function will be calculate distance by erosions
    input:
      - f: input image
    output:
      - y: image with op
    """
    g = f.copy()
    while True:
        f=g.copy()
        g=mm.ero1(g,b)
        if np.array_equal(f,g): break
    return g
    
  @staticmethod
  def gdist(f,g,b=np.ones((3,3),dtype='uint8')):
    """This function will be calculate geodesic distance with erode neg of g intersect f
    input:
      - f: input binary image with 0 and 1
      - g: marker - input binary image with 0 and 1
      - b: kernel
    output:
      - y: image with op
    """
    h,w = f.shape
    max = h*w
    fneg = (max - f*max).astype('uint16')
    gneg = (1 - g).astype('uint16')
    c = 0
    y = gneg
    while True and c<1000000:
      c+=1
      y0=y
      log = np.logical_xor(gneg,fneg)
      y = log*(y + mm.cero(gneg,fneg,b,c))
      if np.array_equal(y0,y):
        break
    return y
    
  @staticmethod
  def thin(f):
    """This function will be calculate the skeleton of image
    input:
      - f: input image
    output:
      - y: image with skeleton
    """
    from skimage.morphology import skeletonize

    return np.array(skeletonize(f)).astype('uint8')

  @staticmethod
  def frame(f,border=5):
    """This function will be return a frame of image
    input:
      - f: input image
      - border: default=5
    output:
      - y: image
    """
    g = np.ones_like(f)*255
    g[border:-border,border:-border] = 0
    return g
        
  def edgeoff(f,b=np.ones((3,3),dtype='uint8')):
    """This function will be remove border componentes
    input:
      - f: input image
      - b: structiring function
    output:
      - y: image
    """
    return mm.subm(f,mm.infrec(mm.frame(f),f,b))
      
      
  @staticmethod
  def clohole(f,b=np.ones((3,3),dtype='uint8')):
    """This function will be close hole of image
    input:
      - f: input image
    output:
      - y: image
    """
    frame = mm.frame(f)
    return mm.neg(mm.infrec(frame,mm.neg(f),b))

  @staticmethod
  def neg(f):
    """This function will be return the inverting image
    input:
      - f: input image
    output:
      - y: image
    """
    return cv2.bitwise_not(f)
    
  def hmin(f,h,b=np.ones((3,3),dtype='uint8')):
    """sup-reconstructs the gray-scale image f
       from the marker created by the addition of the positive integer value h to f
    input:
      - f: input image
      - b: structiring function
    output:
      - y: image
    """
    g = mm.addm(f,h)
    return mm.suprec(f,g,b)

  def skelm(f,b=np.zeros((3,3),dtype='uint8')): 
    """versão corrigida em 2/3/2023
    essa implementação NÃO roda na lista3 até 2023.1
    """
    global sesum, ero1, dil1
    img = f.copy()
    skel = np.zeros((f.shape))
    ero = np.ones((f.shape))
    n = 0
    while np.max(ero):
      nb = mm.sesum(b,n)
      ero = mm.ero1(img, nb)
      Sn = ero - mm.dil1(mm.ero1(ero, b), b) #mm.subm dá underflow pois usa uint8
      skel = np.maximum(skel,Sn)
      # print(f'n={n} nb=\n{mm.drawImage(nb)}\nero=\n{mm.drawImage(ero)}\nSn=\n{mm.drawImage(Sn)}\n')
      n += 1
    return skel

  def skel(f): # implementação do cv2
    """implementação do cv2
    https://docs.opencv.org/4.x/df/d2d/group__ximgproc.html#ga37002c6ca80c978edb6ead5d6b39740c
    técnica de Zhang-Suen: http://rstudio-pubs-static.s3.amazonaws.com/302782_e337cfbc5ad24922bae96ca5977f4da8.html
    """
    return cv2.ximgproc.thinning(f)

  # essa implementação é a do enunciado e
  # RODA na lista3 de 2022.1
  # porém, não calcula corretamento o esqueleto
  def esqueleto(f, b):
    global dilatacao, erosao, sesum
    img = f.copy()
    skel = np.zeros((f.shape))
    n = 0
    while np.max(img):
        nb = mm.sesum(b,n)
        abertura = mm.dil1(mm.ero1(img, b), b)
        skel = np.logical_or(skel, np.logical_and(img, np.logical_not(abertura))).astype(int)
        img = mm.ero1(img, nb)
        n += 1
    return skel

  def verifyBoundBox(object, center, matrix, width, height):
    """ Função interessante para verificar se conseguiu segmentar corretamente imagens comparando com gabaritos (matriz lide de TXT).
        Ver exemplos de datasets: https://storage.googleapis.com/openimages/web/visualizer/index.html
        Utilizar OIDv4 para baixar exemplos: https://github.com/theAIGuysCode/OIDv4_ToolKit
        
        A matriz contem um boundbox normalizado por linha do arquivo TXT para cada objeto. Para ler essa matriz:
            
            import pandas as pd
            df = pd.read_csv("00001.txt", sep='\t', header=None)
            matrix = df.to_numpy()
            
            As colunas têm objetos, p1=[x1,y1] e p2=[x2,y2] (valores nomalizados entre 0 e 1 - são os dois pontos extremos para definir o retângulo)
        input:
          - object: é um dos índices dos objetos segmentados - valores entre 0 e 8 (n=9 objetos segmentados)
          - center: centro=[x,y] de massa do objeto segmentado
          - matrix: matriz objetos e bounding boxes, em cada linha tem: [i x1 y1 x2 y2]
          - width: largura da imagem
          - height: altura da imagem
        output:
          - correct: conseguiu segmentar corretamente se retorno correct = 1
    """
    import numpy as np
    correct = 0
    for v in matrix[matrix[:,0]==object]:
        p1 = v[1:][:2]*[width, height]//1
        p2 = v[1:][2:]*[width, height]//1
        if (p1 < np.array(center)).all() and (np.array(center)<p2).all():
            correct += 1
    return correct

'''
O problema na questão do esqueleto da lista3:

Implementei duas versões no final do arquivo morph.py

O problema surgiu pois considerei implementações da sugestão que está na lista.

O ideal é considerar pesos nos vizinhos! Não temos controle sobre esses pesos e na origem do kernel nas implementações do OpenCV.

Neste arquivo morph.py estão quase todas as implementações necessárias para fazer as listas, basta saber utiliza corretamente os métodos de entrada e de processamento.

Padronizei esse arquivo com: 
 * mm.operacao0, para tratar erosão e dilatação sem pesos nos vizinhos, porém somente valores > 0
 * mm.operacao1, tem pesos nos vizinhos. Exemplos
 * mm.operacao, implementação do opencv - pois são mais rápidas para serem aplicadas na segunda parte do curso: Visão Computacional.

mm.ero0
mm.ero1
mm.ero
'''





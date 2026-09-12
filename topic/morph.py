"""
Morph – Operações morfológicas para Processamento de Imagens.
Copyright 2024 Francisco de Assis Zampirolli, UFABC. License MIT.
version 1.0 - https://github.com/fzampirolli/morph
version 1.1 - https://github.com/fzampirolli/pdi-vc/blob/master/morph/morph.py - compacto
version 1.1.2 - com vários métodos para auxílio no cálculo de medidas usando cv2
version 1.1.5 - remoção de import global cv2, numpy, matplotlib, skimage, scipy.ndimage; lazy loading
version 1.1.6 - inclusão de métodos para Aprendizado de Máquina (k-NN, readTrain, readTest)
version 1.1.7 - lazy loading de sklearn (neighbors, preprocessing, metrics) e skimage.feature
version 1.1.8 - showNet e showTrainCurves para mostrar arquitetura de rede pytorch
version 1.1.9 - mm.otsu(img): expõe só o limiar T de Otsu (espelha mm::otsu da morph.hpp)
Last update: Aug 2026
"""

# Convenção de nomes:
#   mm.<nome>   -> encapsula implementação clássica (cv2 / skimage / sklearn)
#   mm.<nome>0  -> implementação manual/didática, com kernel planar
#   mm.<nome>1  -> implementação manual/didática, com kernel não-planar

# Imports lazy adicionais (mesmo padrão de _get_cv2/_get_np/_get_skmeasure do cabeçalho).

__version__ = "1.1.9"

from typing import Optional
import sys

class mm:
    """Helper class for image processing tasks optimized for minimal RAM usage."""

    IN_INTERACTIVE = (
        'google.colab' in sys.modules          # Google Colab
        or 'ipykernel' in sys.modules          # Jupyter Notebook / JupyterLab / VSCode
        or 'IPython' in sys.modules            # IPython interativo
    )

    count_Images = 0

    # Atributos privados para guardar cache das importações (Lazy Loading)
    _cv2 = None
    _np = None
    _plt = None
    _measure = None
    _scipy_ndimage = None
    _sklneighbors = None
    _sklpreprocessing = None
    _sklmetrics = None
    _skfeature = None
    _torch = None
    _nn = None

    @classmethod
    def _get_cv2(cls):
        if cls._cv2 is None:
            import cv2
            cls._cv2 = cv2
        return cls._cv2

    @classmethod
    def _get_np(cls):
        if cls._np is None:
            import numpy as np
            cls._np = np
        return cls._np

    @classmethod
    def _get_plt(cls):
        if cls._plt is None:
            import matplotlib.pyplot as plt
            cls._plt = plt
        return cls._plt

    @classmethod
    def _get_skmeasure(cls):
        if cls._measure is None:
            from skimage import measure
            cls._measure = measure
        return cls._measure

    @classmethod
    def _get_scipy_ndimage(cls):
        if cls._scipy_ndimage is None:
            import scipy.ndimage as ndimage
            cls._scipy_ndimage = ndimage
        return cls._scipy_ndimage
    
    @classmethod
    def _get_sklneighbors(cls):
        if cls._sklneighbors is None:
            import sklearn.neighbors as sklneighbors
            cls._sklneighbors = sklneighbors
        return cls._sklneighbors
 
    @classmethod
    def _get_sklpreprocessing(cls):
        if cls._sklpreprocessing is None:
            import sklearn.preprocessing as sklpreprocessing
            cls._sklpreprocessing = sklpreprocessing
        return cls._sklpreprocessing
 
    @classmethod
    def _get_sklmetrics(cls):
        if cls._sklmetrics is None:
            import sklearn.metrics as sklmetrics
            cls._sklmetrics = sklmetrics
        return cls._sklmetrics
 
    @classmethod
    def _get_skfeature(cls):
        if cls._skfeature is None:
            from skimage import feature as skfeature
            cls._skfeature = skfeature
        return cls._skfeature
 
    @classmethod
    def _get_torch(cls):
        if cls._torch is None:
            import torch
            cls._torch = torch
        return cls._torch

    @classmethod
    def _get_nn(cls):
        if cls._nn is None:
            import torch.nn as nn
            cls._nn = nn
        return cls._nn
    
    def __init__(self): pass

    # ── UTILITIES ────────────────────────────────────────────────────────────

    @staticmethod
    def install(packages=None):
        """Instala pacotes pip. Ex: mm.install(['scikit-image'])"""
        if packages is None:
            packages = ['matplotlib', 'numpy', 'opencv-python']
        import subprocess
        for p in packages:
            subprocess.check_call([sys.executable, "-m", "pip", "install", p])

    @staticmethod
    def read(file, pil=False, grayscale=False):
        """Lê imagem (local, URL ou Google Drive) → PIL.Image, ndarray 2D ou RGB 3D."""
        import re, requests
        from PIL import Image
        from io import BytesIO
        from urllib.request import urlopen, Request
        np = mm._get_np()

        # — fonte: URL / Google Drive —
        if isinstance(file, str) and file.startswith(("http://", "https://", "id=")):
            m = re.search(r"id=([\w-]+)", file) or re.search(r"/d/([\w-]+)", file)
            url = f"https://drive.google.com/uc?export=view&id={m.group(1)}" \
                if m and ("id=" in file or "drive.google.com" in file) else file
            hdr = {"User-Agent": "Mozilla/5.0 AppleWebKit/537.36 Chrome/124 Safari/537.36"}
            try:
                r = requests.get(url, headers=hdr, timeout=20)
                if r.status_code == 429: raise requests.exceptions.HTTPError()
                r.raise_for_status()
                file = BytesIO(r.content)
            except:
                file = BytesIO(urlopen(Request(url, headers=hdr), timeout=20).read())

        img = Image.open(file)
        img.load()
        if pil:                    return img
        if grayscale:              return np.array(img.convert("L"))   # (H,W)
        if img.mode == "L":        return np.array(img)                # (H,W)
        if img.mode == "RGBA":                                         # fundo branco
            bg = Image.new("RGB", img.size, (255, 255, 255))
            bg.paste(img, mask=img.split()[3])
            return np.array(bg)
        return np.array(img.convert("RGB"))                            # (H,W,3)

    @staticmethod
    def color(img):
        """Converte imagem para RGB."""
        cv2 = mm._get_cv2()
        if img.ndim == 2:         return cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
        if img.shape[2] == 4:    return cv2.cvtColor(img, cv2.COLOR_RGBA2RGB)
        return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    @staticmethod
    def gray(img):
        """Converte imagem colorida para escala de cinza. Idempotente: se já
        for 1 canal (2D ou HxWx1), devolve como está."""
        cv2 = mm._get_cv2()
        if getattr(img, "ndim", 2) == 2 or (img.ndim == 3 and img.shape[2] == 1):
            return img if img.ndim == 2 else img[:, :, 0]
        return cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY if img.shape[2] == 4
                            else cv2.COLOR_RGB2GRAY)

    @staticmethod
    def neg(f):
        """Inverte a imagem."""
        cv2 = mm._get_cv2()
        return cv2.bitwise_not(f)

    @staticmethod
    def binary(f):
        """True se binária, False se não, None se vazia."""
        np = mm._get_np()
        hist, _ = np.histogram(f.ravel(), 256, [0, 256])
        nz = np.count_nonzero(hist > 0)
        return True if nz == 2 else (False if nz > 2 else None)

    # ── LEITURA / CRIAÇÃO ────────────────────────────────────────────────────

    @staticmethod
    def readImg(h, w, dtype='uint8'):
        """Lê uma matriz h×w da entrada padrão (valores por linha separados por espaço), aceitando int ou float."""
        np = mm._get_np()
        m = np.zeros((h, w), dtype=dtype)
        
        # Identifica dinamicamente se o tipo desejado é ponto flutuante
        is_float = 'float' in str(dtype)
        
        for l in range(h):
            if is_float:
                m[l] = [float(i) for i in input().split() if i]
            else:
                m[l] = [int(i) for i in input().split() if i]
        return m

    @staticmethod
    def readImg2(dtype='uint8'):
        """Lê uma matriz de tamanho variável da entrada padrão (até linha vazia), aceitando int ou float."""
        np = mm._get_np()
        rows = []
        
        # Identifica dinamicamente se o tipo desejado é ponto flutuante
        is_float = 'float' in str(dtype)
        
        while line := input():
            if is_float:
                rows.append([float(i) for i in line.split() if i])
            else:
                rows.append([int(i) for i in line.split() if i])
                
        return np.array(rows, dtype=dtype)

    @staticmethod
    def randomImage(h, w, maxValue=9):
        """Cria imagem aleatória h×w com valores em [0, maxValue]."""
        np = mm._get_np()
        return np.random.randint(maxValue + 1, size=(h, w)).astype('uint8')

    @staticmethod
    def crop(img, y0, y1, x0, x1):
        """Recorte retangular img[y0:y1, x0:x1] (equivalente ao fatiamento NumPy)."""
        return img[y0:y1, x0:x1]

    @staticmethod
    def subsample(img, f):
        """Subamostragem por fatiamento com passo f: img[::f, ::f]."""
        return img[::f, ::f]

    @staticmethod
    def resize(img, size_or_factor, method='bilinear'):
        """Redimensiona imagem via OpenCV integrado ao mm: nearest, bilinear, bicubic."""
        cv2 = mm._get_cv2()
        interp = {'nearest': cv2.INTER_NEAREST, 'bilinear': cv2.INTER_LINEAR, 'bicubic': cv2.INTER_CUBIC}
        m = interp.get(method, cv2.INTER_LINEAR)
        
        if isinstance(size_or_factor, (int, float)):
            return cv2.resize(img, (0,0), fx=size_or_factor, fy=size_or_factor, interpolation=m)
        return cv2.resize(img, size_or_factor, interpolation=m)
    
    @staticmethod
    def rotate(img, angle, center=None, scale=1.0, interp='bilinear'):
        """Rotaciona uma imagem em torno de um ponto central."""
        cv2 = mm._get_cv2()
        flags = {'nearest': cv2.INTER_NEAREST,
                'bilinear': cv2.INTER_LINEAR,
                'bicubic': cv2.INTER_CUBIC}.get(interp, cv2.INTER_LINEAR)
        h, w = img.shape[:2]
        if center is None:
            center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, scale)
        return cv2.warpAffine(img, M, (w, h), flags=flags)
    
    @staticmethod
    def translate(img, tx, ty):
        cv2 = mm._get_cv2()
        np = mm._get_np()
        h, w = img.shape[:2]
        M = np.float32([[1, 0, tx], [0, 1, ty]])
        return cv2.warpAffine(img, M, (w, h))

    @staticmethod
    def shear(img, shx=0.0, shy=0.0, method='bilinear'):
        """Aplica cisalhamento afim. method: 'nearest', 'bilinear', 'bicubic', 'lanczos'."""
        cv2 = mm._get_cv2()
        np = mm._get_np()
        _m = {'nearest': cv2.INTER_NEAREST, 'bilinear': cv2.INTER_LINEAR,
            'bicubic': cv2.INTER_CUBIC,   'lanczos':  cv2.INTER_LANCZOS4}
        h, w = img.shape[:2]
        M = np.float32([[1, shx, 0], [shy, 1, 0]])
        return cv2.warpAffine(img, M, (w, h), flags=_m.get(method, cv2.INTER_LINEAR))

    @staticmethod
    def perspective_transform(img, pts1, pts2, size=None):
        """Aplica transformação de perspectiva (homografia) em uma imagem.

        pts1/pts2: 4 pares (x, y) — aceita np.ndarray, lista ou tupla.
        """
        cv2 = mm._get_cv2()
        np = mm._get_np()
        pts1 = np.asarray(pts1, dtype=np.float32)
        pts2 = np.asarray(pts2, dtype=np.float32)
        if size is None:
            h, w = img.shape[:2]
            size = (w, h)
        M = cv2.getPerspectiveTransform(pts1, pts2)
        return cv2.warpPerspective(img, M, size)

    @staticmethod
    def write(img, path):
        """Salva imagem em disco. Aceita numpy array (RGB ou cinza) ou PIL Image."""
        import os
        np = mm._get_np()
        cv2 = mm._get_cv2()
        os.makedirs(os.path.dirname(path), exist_ok=True) if os.path.dirname(path) else None
        if isinstance(img, np.ndarray):
            if img.ndim == 3 and img.shape[2] == 3:
                cv2.imwrite(path, cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
            else:
                cv2.imwrite(path, img)
        else:
            exif = img.info.get("exif", b"")
            img.save(path, exif=exif) if exif else img.save(path)

    @staticmethod
    def drawImg(f):
        return mm.drawImage(f)

    @staticmethod
    def drawImage(f):
        """Retorna string formatada da matriz para impressão."""
        width = max(len(str(f.max())), len(str(f.min())))
        fmt = '%' + str(width) + 'd '
        return ''.join(
            ''.join(fmt % f[i,j] for j in range(f.shape[1])) + '\n'
            for i in range(f.shape[0])
        )

    @staticmethod
    def drawImageTab(f, spacing=None, width=None):
        """Retorna string formatada da matriz para impressão (sem tabs)."""
        if spacing is None:
            spacing = 1  # comportamento anterior

        if width is None:
            width = max(len(str(f.max())), len(str(f.min())))

        sep = ' ' * spacing
        fmt = '{:>' + str(width) + 'd}'

        linhas = []
        for i in range(f.shape[0]):
            colunas = [fmt.format(f[i, j]) for j in range(f.shape[1])]
            linha = sep + sep.join(colunas)
            linhas.append(linha)

        texto = '\n'.join(linhas) + '\n'
        texto = texto.replace('\t', ' ' * width)
        return texto

    @staticmethod
    def _plot_grid(f):
        """Configura grade e rótulos para drawImagePlt/drawImageKernel."""
        plt = mm._get_plt()
        h, w = f.shape
        plt.rcParams.update({'xtick.bottom':False,'xtick.labelbottom':False,
                             'xtick.top':True,'xtick.labeltop':True})
        plt.imshow(f, 'gray')
        plt.yticks(range(h)); plt.xticks(range(w))
        plt.ylabel('y'); plt.xlabel('x')
        [plt.axvline(i+.5, 0, h, color='r') for i in range(w-1)]
        [plt.axhline(j+.5, 0, w, color='r') for j in range(h-1)]

    @staticmethod
    def drawImgKernel(f, B, x, y, scale=40):
        return mm.drawImageKernel(f, B, x, y, scale)

    @staticmethod
    def drawImageKernel(f,B,x,y,scale=40):
        """Exibe imagem com kernel B centrado em (x,y)."""
        plt = mm._get_plt()
        Bh,Bw=B.shape
        Bcx,Bcy=Bw//2,Bh//2
        h,w=f.shape[:2]
        plt.figure(figsize=(w/100*scale,h/100*scale))
        mm._plot_grid(f)
        plt.xticks(fontsize=8)
        plt.yticks(fontsize=8)
        plt.title(f'Processando pixel (x,y)=({x},{y})')
        [plt.plot([i+x-Bcx-.5]*2,[y-Bcy-.5,Bh+y-Bcy-.5],color='y',lw=2) for i in range(Bw+1)]
        [plt.plot([x-Bcx-.5,x-Bcx+Bw-.5],[j+y-Bcy-.5]*2,color='y',lw=2) for j in range(Bh+1)]

    @staticmethod
    def drawImgPlt(f, scale=40):
        return mm.drawImagePlt(f, scale)

    @staticmethod
    def drawImagePlt(f, scale=40):
        """ Displays the input image f using Matplotlib."""
        plt = mm._get_plt()
        h,w=f.shape[:2]
        plt.figure(figsize=(w/100*scale,h/100*scale))
        plt.rcParams['xtick.bottom'] = plt.rcParams['xtick.labelbottom'] = False
        plt.rcParams['xtick.top'] = plt.rcParams['xtick.labeltop'] = True
        _ = plt.imshow(f, 'gray')
        plt.yticks(range(h))
        plt.xticks(range(w))
        plt.ylabel('y')
        plt.xlabel('x')
        [plt.axvline(i + .5, 0, h, color='r') for i in range(w - 1)]
        [plt.axhline(j + .5, 0, w, color='r') for j in range(h - 1)]

    @staticmethod
    def lblshow(f, border=3):
        """Exibe contornos coloridos de cada componente."""
        plt = mm._get_plt()
        skmeasure = mm._get_skmeasure()
        fig, ax = plt.subplots()
        ax.imshow(f, interpolation='nearest', cmap=plt.cm.gray)
        for c in skmeasure.find_contours(f, 0.0):
            ax.plot(c[:,1], c[:,0], linewidth=border)
        ax.axis('image'); ax.set_xticks([]); ax.set_yticks([])
        plt.imshow(f, "gray")
        if not mm.IN_INTERACTIVE:
            plt.savefig(f'fig_{mm.count_Images:04d}.png')
            mm.count_Images += 1

    # ── OPERAÇÕES BÁSICAS ────────────────────────────────────────────────────

    @staticmethod
    def subm(f, g):   return mm._get_cv2().subtract(f, g)
    @staticmethod
    def addm(f, g):   return mm._get_cv2().add(f, g)
    @staticmethod
    def union(f, g):  return mm._get_np().maximum(f, g)
    @staticmethod
    def intersec(f1, f2): return mm._get_np().minimum(f1, f2)

    @staticmethod
    def blend(f, g, alpha=0.5):
        """Mistura ponderada: alpha*f + (1-alpha)*g, com clipping para uint8."""
        np = mm._get_np()
        return np.clip(
            alpha * f.astype(np.float32) + (1 - alpha) * g.astype(np.float32),
            0, 255
        ).astype(np.uint8)
    
    @staticmethod
    def band(f, g):   return mm._get_cv2().bitwise_and(f, g)
    @staticmethod
    def bor(f, g):    return mm._get_cv2().bitwise_or(f, g)
    @staticmethod
    def bxor(f, g):   return mm._get_cv2().bitwise_xor(f, g)
    @staticmethod
    def bnot(f):      return mm._get_cv2().bitwise_not(f)

    @staticmethod
    def circle(img, center, radius, color, thickness=-1):
        """Desenha um círculo em img (wrapper de cv2.circle). thickness=-1 = preenchido.
        Não altera o original: opera sobre uma cópia."""
        out = img.copy()
        mm._get_cv2().circle(out, tuple(int(c) for c in center), int(radius),
                             color, int(thickness))
        return out

    @staticmethod
    def circle0(img, center, radius, color, thickness=-1):
        """Círculo didático (sem cv2): teste r^2 pixel a pixel. thickness=-1 =
        preenchido; qualquer valor > 0 desenha só o anel dessa espessura."""
        np = mm._get_np()
        out = img.copy()
        cx, cy = int(center[0]), int(center[1])
        r = int(radius)
        H, W = img.shape[:2]
        y0, y1 = max(0, cy - r - 1), min(H, cy + r + 2)
        x0, x1 = max(0, cx - r - 1), min(W, cx + r + 2)
        for y in range(y0, y1):
            for x in range(x0, x1):
                d2 = (x - cx) ** 2 + (y - cy) ** 2
                if thickness < 0:
                    hit = d2 <= r * r
                else:
                    ri = max(0, r - thickness)
                    hit = ri * ri <= d2 <= r * r
                if hit:
                    out[y, x] = color
        return out

    @staticmethod
    def threshold(img, limiar=None):
        """Limiarização binária. Se limiar for None, utiliza o método de Otsu."""
        cv2 = mm._get_cv2()
        flags = cv2.THRESH_BINARY + (cv2.THRESH_OTSU if limiar is None else 0)
        valor_limiar = 0 if limiar is None else limiar
        _, th = cv2.threshold(img, valor_limiar, 255, flags)
        return th

    @staticmethod
    def otsu(img):
        """Limiar de Otsu (só o valor T), o mesmo que `mm.threshold(img)` usa
        internamente quando o limiar é omitido. Útil quando o T precisa
        aparecer num título/log sem recorrer a `cv2.threshold(...)[0]`.
        Espelha `mm::otsu` da morph.hpp."""
        cv2 = mm._get_cv2()
        T, _ = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return int(T)

    # ── HISTOGRAMA / EQUALIZAÇÃO ─────────────────────────────────────────────

    @staticmethod
    def hist(img, B=8):
        np = mm._get_np()
        H = np.zeros(2**B, dtype=int)
        for v in img.flatten(): H[v] += 1
        return H

    @staticmethod
    def histPlus(img):
        """Histograma e dicionário de pixels por cor."""
        np = mm._get_np()
        H = np.zeros(int(img.max()) + 1, dtype=int)
        vet = {}
        for i, cor in enumerate(img.flatten()):
            H[cor] += 1
            vet.setdefault(str(cor), []).append(i)
        return H, vet
    
    @staticmethod
    def histImg(img, vmax=None, color="steelblue"):
        """Renderiza o histograma de img como array NumPy (para uso em mm.show)."""
        import io
        plt = mm._get_plt()
        np = mm._get_np()
        H = mm.hist(img)
        vmax = vmax if vmax is not None else int(img.max())
        fig, ax = plt.subplots(figsize=(4, 3))
        ax.bar(range(len(H)), H, color=color, edgecolor="none", width=1)
        ax.set_xlim(0, vmax)
        ax.set_xticks([0, vmax//2, vmax])
        plt.tight_layout()
        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=100)
        plt.close(fig)
        buf.seek(0)
        return np.array(plt.imread(buf))

    @staticmethod
    def equalize(image, B=8):
        """Equalização de histograma pela CDF: s_k = (L-1) * CDF(r_k)."""
        np = mm._get_np()
        Lmax = 2**B
        h = mm.hist(image, B)
        cdf = np.cumsum(h / h.sum())
        lut = np.round(cdf * (Lmax - 1)).astype(np.uint8)
        return lut[image]

    @staticmethod
    def clahe(img, clipLimit=2.0, tiles=8):
        """CLAHE — equalização adaptativa com limite de contraste.

        Encapsula cv2.createCLAHE(clipLimit, (tiles, tiles)). Espelha
        mm::clahe da morph.hpp (reimplementação header-only fiel ao OpenCV)."""
        cv2 = mm._get_cv2()
        return cv2.createCLAHE(clipLimit=float(clipLimit),
                               tileGridSize=(int(tiles), int(tiles))).apply(img)

    @staticmethod
    def equalizacao(image):
        """Equalização pelo valor máximo."""
        np = mm._get_np()
        h = mm.hist(image)
        prob = h / h.sum()
        soma = np.cumsum(prob) * image.max()
        soma = np.round(soma)
        out = np.vectorize(lambda v: soma[v])(image)
        return out.astype('int')

    # ── ELEMENTOS ESTRUTURANTES ───────────────────────────────────────────────

    @staticmethod
    def sesum(b, n=0):
        """Soma de Minkowski nB."""
        cv2 = mm._get_cv2()
        np = mm._get_np()
        def _s(nb, b_struct):
            h, w = b_struct.shape
            nbh, nbw = nb.shape
            H = nbh+h-1 if h%2 else nbh+h
            W = nbw+w-1 if w%2 else nbw+w
            r = np.zeros((H, W), dtype='uint8')
            r[h//3:-(h//3), w//3:-(w//3)] = nb
            return cv2.dilate(r, b_struct).astype('uint8')
        B = b.copy()
        for _ in range(n): B = _s(B, b)
        return B

    @staticmethod
    def sebox(n=0):
        np = mm._get_np()
        return mm.sesum(np.ones((3,3), dtype='uint8'), n)

    @staticmethod
    def secross(n=0):
        np = mm._get_np()
        B = np.ones((3,3), dtype='uint8')
        B[0,0]=B[0,2]=B[2,0]=B[2,2]=0
        return mm.sesum(B, n)

    @staticmethod
    def sedisk(n=3):
        cv2 = mm._get_cv2()
        return cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (n,n))

    # ── VIZINHANÇA (helper interno) ───────────────────────────────────────────

    @staticmethod
    def _viz(f, B, y, x):
        """Gera (vy, vx, b_val) para cada vizinho válido de (y,x)."""
        np = mm._get_np()
        H, W = f.shape
        Bh, Bw = B.shape
        oh, ow = -Bh/2 + 0.5, -Bw/2 + 0.5
        for by, bx in np.ndindex(Bh, Bw):
            vy, vx = int(y + by + oh), int(x + bx + ow)
            if 0 <= vy < H and 0 <= vx < W:
                yield vy, vx, B[by, bx]
                
    # ── FILTROS / CORRELAÇÃO ─────────────────────────────────────────────────

    @staticmethod
    def _border_flag(border):
        """Mapeia nome de borda -> flag do OpenCV (usado por conv/pad)."""
        cv2 = mm._get_cv2()
        return {
            "reflect101": cv2.BORDER_REFLECT_101,
            "replicate":  cv2.BORDER_REPLICATE,
            "constant":   cv2.BORDER_CONSTANT,
            "reflect":    cv2.BORDER_REFLECT,
        }[border]

    @staticmethod
    def conv(f, w, border="reflect101"):
        """Correlação vetorizada via cv2.filter2D (eficiente).

        border: 'reflect101' (padrão do cv2), 'replicate', 'constant' (zero) ou
        'reflect'."""
        cv2 = mm._get_cv2()
        np = mm._get_np()
        return cv2.filter2D(f, -1, w.astype(np.float32),
                            borderType=mm._border_flag(border))

    @staticmethod
    def conv0(f, w, border="keep"):
        """Correlação didática (laços explícitos).

        border: 'keep' (bordas mantidas com o valor original, padrão) ou
        'constant' (zero fora da imagem — resultado completo)."""
        np = mm._get_np()
        f  = f.astype(np.float32)
        a, b = w.shape[0]//2, w.shape[1]//2
        H, W = f.shape
        g = f.copy()
        if border == "constant":
            fp = np.pad(f, ((a, a), (b, b)), mode="constant")
            for y in range(H):
                for x in range(W):
                    viz = fp[y:y+2*a+1, x:x+2*b+1]
                    g[y, x] = (w * viz).sum()
        else:
            for y in range(a, H-a):
                for x in range(b, W-b):
                    viz = f[y-a:y+a+1, x-b:x+b+1]
                    g[y, x] = (w * viz).sum()
        return np.clip(g, 0, 255).astype(np.uint8)

    @staticmethod
    def gaussKernel(N=3, sigma=0):
        """Kernel Gaussiano 2D N×N normalizado (soma = 1).

        sigma <= 0 → fórmula do cv2.getGaussianKernel. Espelha
        mm::Kernel::gaussian da morph.hpp."""
        cv2 = mm._get_cv2()
        k = cv2.getGaussianKernel(N, sigma)
        w = k @ k.T
        return w / w.sum()

    @staticmethod
    def pad(img, b, border="constant"):
        """Preenchimento de borda de largura b (wrapper de cv2.copyMakeBorder).

        border: 'constant' (zero), 'replicate', 'reflect101' ou 'reflect'."""
        cv2 = mm._get_cv2()
        return cv2.copyMakeBorder(img, b, b, b, b, mm._border_flag(border), value=0)

    @staticmethod
    def pad0(img, b, border="constant"):
        """Preenchimento de borda didático (np.pad), mesmos modos de mm.pad."""
        np = mm._get_np()
        modo = {"constant": "constant", "replicate": "edge",
                "reflect101": "reflect", "reflect": "symmetric"}[border]
        return np.pad(img, ((b, b), (b, b)), mode=modo).astype(img.dtype)

    @staticmethod
    def blur0(f, N=3):
        """Filtro de média N×N (Python pura): borda copiada."""
        L, C = f.shape
        r = N // 2
        g = f.copy().astype(int)
        for i in range(r, L-r):
            for j in range(r, C-r):
                g[i,j] = round(f[i-r:i+r+1, j-r:j+r+1].mean())
        return g.astype('uint8')

    @staticmethod
    def blur(f, N=3):
        """Filtro de média N×N via cv2: borda copiada."""
        return mm._get_cv2().blur(f, (N, N))

    @staticmethod
    def gaussian0(f, N=3, sigma=0):
        """Filtro Gaussiano N×N (Python pura): borda copiada."""
        cv2 = mm._get_cv2()
        np = mm._get_np()
        r = N // 2
        L, C = f.shape

        k = cv2.getGaussianKernel(N, sigma)
        h = k @ k.T
        h /= h.sum()

        g = f.copy().astype(float)
        for i in range(r, L-r):
            for j in range(r, C-r):
                g[i,j] = round(np.sum(f[i-r:i+r+1, j-r:j+r+1] * h))
        return g.astype('uint8')

    @staticmethod
    def gaussian(f, N=3, sigma=0):
        """Filtro Gaussiano N×N via cv2: borda copiada."""
        return mm._get_cv2().GaussianBlur(f, (N, N), sigma)   

    @staticmethod
    def laplacian0(f, B=None):
        """Realce por Laplaciano (Python pura): g = clip(f - conv(f,B)), borda copiada."""
        np = mm._get_np()
        if B is None:
            B = np.array([[0,1,0],[1,-4,1],[0,1,0]], dtype=np.float32)
        g = f.copy().astype(int)
        for y in range(f.shape[0]):
            for x in range(f.shape[1]):
                viz = list(mm._viz(f, B, y, x))
                if len(viz) == B.size:
                    lap = sum(int(f[vy,vx]) * bv for vy,vx,bv in viz)
                    g[y,x] = max(0, min(255, int(f[y,x]) - lap))
        return g.astype('uint8')

    @staticmethod
    def laplacian_viz0(f, B=None):
        """Visualização do Laplaciano bruto (Python pura): normaliza |lap| para [0,255]."""
        np = mm._get_np()
        if B is None:
            B = np.array([[0,1,0],[1,-4,1],[0,1,0]], dtype=np.float32)
        g = np.zeros_like(f, dtype=np.float32)
        r = B.shape[0] // 2
        for y in range(r, f.shape[0]-r):
            for x in range(r, f.shape[1]-r):
                viz = list(mm._viz(f, B, y, x))
                if len(viz) == B.size:
                    g[y,x] = sum(int(f[vy,vx]) * bv for vy,vx,bv in viz)
        mx = np.abs(g).max() or 1
        return np.clip(np.abs(g) / mx * 255, 0, 255).astype(np.uint8)
                                                            
    @staticmethod
    def laplacian_viz(f, B=None):
        """Visualização do Laplaciano bruto via cv2: normaliza |lap| para [0,255]."""
        cv2 = mm._get_cv2()
        np = mm._get_np()
        if B is None:
            B = np.array([[0,1,0],[1,-4,1],[0,1,0]], dtype=np.float32)
        lap = cv2.filter2D(f.astype(np.float32), -1, B)
        return np.clip(np.abs(lap) / np.abs(lap).max() * 255, 0, 255).astype(np.uint8)

    @staticmethod
    def laplacian(f, B=None):
        """Realce por Laplaciano via cv2: borda copiada."""
        cv2 = mm._get_cv2()
        np = mm._get_np()
        if B is None:
            B = np.array([[0,1,0],[1,-4,1],[0,1,0]], dtype=np.float32)
        lap = cv2.filter2D(f.astype(np.float32), -1, B)
        return np.clip(f.astype(np.float32) - lap, 0, 255).astype('uint8')

    @staticmethod
    def sobel0(f, Bx=None, By=None):
        """Magnitude do gradiente de Sobel (Python pura): borda zero."""
        np = mm._get_np()
        if Bx is None:
            Bx = np.array([[-1,0,1],[-2,0,2],[-1,0,1]], dtype=np.float32)
        if By is None:
            By = np.array([[-1,-2,-1],[0,0,0],[1,2,1]], dtype=np.float32)
        g = np.zeros(f.shape, dtype='uint8')
        H, W = f.shape
        for y in range(1, H-1):
            for x in range(1, W-1):
                gx = sum(float(f[y+dy, x+dx]) * Bx[dy+1, dx+1] for dy in [-1,0,1] for dx in [-1,0,1])
                gy = sum(float(f[y+dy, x+dx]) * By[dy+1, dx+1] for dy in [-1,0,1] for dx in [-1,0,1])
                g[y,x] = max(0, min(255, round((gx**2 + gy**2)**0.5)))
        return g

    @staticmethod
    def sobel(f, Bx=None, By=None):
        """Magnitude do gradiente de Sobel via cv2: borda zero."""
        cv2 = mm._get_cv2()
        np = mm._get_np()
        if Bx is None:
            Bx = np.array([[-1,0,1],[-2,0,2],[-1,0,1]], dtype=np.float32)
        if By is None:
            By = np.array([[-1,-2,-1],[0,0,0],[1,2,1]], dtype=np.float32)
        gx = cv2.filter2D(f.astype(np.float32), -1, Bx, borderType=cv2.BORDER_ISOLATED)
        gy = cv2.filter2D(f.astype(np.float32), -1, By, borderType=cv2.BORDER_ISOLATED)
        return np.clip(np.round(np.sqrt(gx**2 + gy**2)), 0, 255).astype('uint8')

    @staticmethod
    def prewitt0(f, Bx=None, By=None):
        """Magnitude do gradiente de Prewitt (Python pura): borda zero."""
        np = mm._get_np()
        if Bx is None:
            Bx = np.array([[-1,0,1],[-1,0,1],[-1,0,1]], dtype=np.float32)
        if By is None:
            By = np.array([[-1,-1,-1],[0,0,0],[1,1,1]], dtype=np.float32)
        g = np.zeros(f.shape, dtype='uint8')
        H, W = f.shape
        for y in range(1, H-1):
            for x in range(1, W-1):
                gx = sum(float(f[y+dy, x+dx]) * Bx[dy+1, dx+1] for dy in [-1,0,1] for dx in [-1,0,1])
                gy = sum(float(f[y+dy, x+dx]) * By[dy+1, dx+1] for dy in [-1,0,1] for dx in [-1,0,1])
                g[y,x] = max(0, min(255, round((gx**2 + gy**2)**0.5)))
        return g

    @staticmethod
    def prewitt(f, Bx=None, By=None):
        """Magnitude do gradiente de Prewitt via cv2: borda zero."""
        cv2 = mm._get_cv2()
        np = mm._get_np()
        if Bx is None:
            Bx = np.array([[-1,0,1],[-1,0,1],[-1,0,1]], dtype=np.float32)
        if By is None:
            By = np.array([[-1,-1,-1],[0,0,0],[1,1,1]], dtype=np.float32)
        gx = cv2.filter2D(f.astype(np.float32), -1, Bx, borderType=cv2.BORDER_ISOLATED)
        gy = cv2.filter2D(f.astype(np.float32), -1, By, borderType=cv2.BORDER_ISOLATED)
        return np.clip(np.round(np.sqrt(gx**2 + gy**2)), 0, 255).astype('uint8')

    @staticmethod
    def canny0(f, t_low=50, t_high=150, ksize=3, sigma=0):
        """Detector de Canny (Python pura, didático)."""
        cv2 = mm._get_cv2()
        np = mm._get_np()
        scipy_nd = mm._get_scipy_ndimage()

        # 1. suavização
        k = cv2.getGaussianKernel(ksize, sigma)
        s = scipy_nd.convolve(f.astype(np.float32), k @ k.T)

        # 2. gradiente
        Bx = np.array([[-1,0,1],[-2,0,2],[-1,0,1]], dtype=np.float32)
        By = np.array([[-1,-2,-1],[0,0,0],[1,2,1]], dtype=np.float32)
        gx, gy = scipy_nd.convolve(s, Bx), scipy_nd.convolve(s, By)
        mag    = np.sqrt(gx**2 + gy**2)
        angle  = np.degrees(np.arctan2(gy, gx)) % 180

        # 3. supressão de não-máximos
        nms = np.zeros_like(mag)
        H, W = f.shape
        for y in range(1, H-1):
            for x in range(1, W-1):
                a = angle[y, x]
                if   a < 22.5 or a >= 157.5: n1, n2 = mag[y, x-1],   mag[y, x+1]
                elif a < 67.5:               n1, n2 = mag[y-1, x+1],  mag[y+1, x-1]
                elif a < 112.5:              n1, n2 = mag[y-1, x],     mag[y+1, x]
                else:                        n1, n2 = mag[y-1, x-1],   mag[y+1, x+1]
                if mag[y, x] >= n1 and mag[y, x] >= n2:
                    nms[y, x] = mag[y, x]

        # 4. histerese
        strong = nms >= t_high
        weak   = (nms >= t_low) & ~strong
        labeled, _ = scipy_nd.label(weak | strong)
        keep   = {labeled[y, x] for y, x in zip(*np.where(strong))}
        out    = np.zeros((H, W), dtype=np.uint8)
        out[(strong | weak) & np.isin(labeled, list(keep))] = 255
        return out

    @staticmethod
    def canny(f, t_low=50, t_high=150, ksize=5, sigma=0):
        """Detector de Canny via cv2."""
        cv2 = mm._get_cv2()
        blurred = cv2.GaussianBlur(f, (ksize, ksize), sigma)
        return cv2.Canny(blurred, t_low, t_high)

    @staticmethod
    def median0(f, B=None, border='copy'):
        """border: 'copy' (padrão) ou 'zero'."""
        np = mm._get_np()
        if B is None:
            B = np.zeros((3,3), dtype='uint8')
        g = f.copy() if border == 'copy' else np.zeros_like(f)
        for y in range(f.shape[0]):
            for x in range(f.shape[1]):
                viz = list(mm._viz(f, B, y, x))
                if len(viz) == B.size:
                    vals = sorted(int(f[vy,vx]) for vy,vx,_ in viz)
                    g[y,x] = vals[len(vals) // 2]
        return g.astype('uint8')

    @staticmethod
    def median(f, ksize=3):
        """Filtro da mediana via cv2: tamanho configurável (ímpar)."""
        return mm._get_cv2().medianBlur(f, ksize)

    @staticmethod
    def usm0(f, k=1.0, w=None):
        """Unsharp Masking (Python pura): g = clip(round(f + k*(f - mean))), borda copiada."""
        np = mm._get_np()
        if w is None:
            a, b = 1, 1
            def blur_pixel(img, i, j):
                return img[i-1:i+2, j-1:j+2].mean()
        else:
            a, b = w.shape[0] // 2, w.shape[1] // 2
            def blur_pixel(img, i, j):
                return (w * img[i-a:i+a+1, j-b:j+b+1]).sum()

        L, C = f.shape
        fbar = f.copy().astype(float)
        for i in range(a, L-a):
            for j in range(b, C-b):
                fbar[i,j] = blur_pixel(f, i, j)

        m = f.astype(float) - fbar
        g = f.copy().astype(float)
        for i in range(a, L-a):
            for j in range(b, C-b):
                g[i,j] = max(0, min(255, round(float(f[i,j]) + k * m[i,j])))
        return g.astype('uint8')

    @staticmethod
    def usm(f, k=1.0, w=None):
        """Unsharp Masking via cv2: g = clip(round(f + k*(f - blur))), borda copiada."""
        cv2 = mm._get_cv2()
        np = mm._get_np()
        if w is None:
            w = np.ones((3, 3), dtype=np.float32) / 9.0
        fbar = cv2.filter2D(f.astype(np.float32), -1, w)
        m = f.astype(np.float32) - fbar
        return np.clip(np.round(f.astype(np.float32) + k * m), 0, 255).astype('uint8')

    # ── EROSÃO / DILATAÇÃO ───────────────────────────────────────────────────

    @staticmethod
    def ero(f, Bc=None):
        """Erosão (OpenCV ou com pesos)."""
        cv2 = mm._get_cv2()
        np = mm._get_np()
        if Bc is None:
            Bc = np.zeros((3,3), dtype='uint8')
        try:    return cv2.erode(f, Bc)
        except: return mm.ero1(f, Bc)

    @staticmethod
    def ero0(f, Bc=None):
        """Erosão clássica sem pesos."""
        np = mm._get_np()
        if Bc is None:
            Bc = np.ones((3,3), dtype='uint8')
        g = np.empty_like(f)
        for y in range(f.shape[0]):
            for x in range(f.shape[1]):
                g[y,x] = 255
                for vy,vx,bv in mm._viz(f,Bc,y,x):
                    if bv and g[y,x] > f[vy,vx]: g[y,x] = f[vy,vx]
        return g
    
    @staticmethod
    def ero1(f, b=None):
        """Erosão com pesos: mínimo de f[viz]-b."""
        np = mm._get_np()
        if b is None:
            b = np.zeros((3,3), dtype='uint8')
        g = np.empty_like(f)
        for y in range(f.shape[0]):
            for x in range(f.shape[1]):
                g[y,x] = 255
                for vy, vx, bv in mm._viz(f, b, y, x):
                    if np.isinf(bv): continue
                    val = int(f[vy,vx]) - int(bv)
                    if int(g[y,x]) > val:
                        g[y,x] = max(0, val)
        return g

    @staticmethod
    def dil(f, Bc=None):
        """Dilatação (OpenCV ou com pesos)."""
        cv2 = mm._get_cv2()
        np = mm._get_np()
        if Bc is None:
            Bc = np.zeros((3,3), dtype='uint8')
        try:    return cv2.dilate(f, Bc)
        except: return mm.dil1(f, Bc)

    @staticmethod
    def dil0(f, Bc=None):
        """Dilatação plana seguindo rigorosamente a teoria."""
        np = mm._get_np()
        if Bc is None:
            Bc = np.ones((3,3), dtype='uint8')
        g = np.empty_like(f) 
        Bc = np.flip(Bc)
        for y in range(f.shape[0]):
            for x in range(f.shape[1]):
                g[y,x] = 0
                for vy,vx,bv in mm._viz(f,Bc,y,x):
                    if bv and g[y,x] < f[vy,vx]:
                        g[y,x] = f[vy,vx]
        return g

    @staticmethod
    def dil1(f, b=None):
        """Dilatação com pesos: máximo de f[viz]+b (Apenas uma definição unificada)."""
        np = mm._get_np()
        if b is None:
            b = np.zeros((3,3), dtype='uint8')
        g = np.empty_like(f)
        b = np.flip(b)
        for y in range(f.shape[0]):
            for x in range(f.shape[1]):
                g[y,x] = 0
                for vy, vx, bv in mm._viz(f, b, y, x):
                    val = int(f[vy,vx]) + int(bv)
                    if int(g[y,x]) < val:
                        g[y,x] = min(255, val)
        return g

    # ── OPERADORES MORFOLÓGICOS ──────────────────────────────────────────────

    @staticmethod
    def open(f, b=None):
        cv2 = mm._get_cv2()
        np = mm._get_np()
        if b is None: b = np.zeros((3,3), dtype='uint8')
        return cv2.morphologyEx(f, cv2.MORPH_OPEN, b)

    @staticmethod
    def open0(f, B=None):
        np = mm._get_np()
        if B is None: B = np.ones((3,3), dtype='uint8')
        return mm.dil0(mm.ero0(f, B), B)

    @staticmethod
    def open1(f, b=None):
        np = mm._get_np()
        if b is None: b = np.zeros((3,3), dtype='uint8')
        return mm.dil1(mm.ero1(f, b), b)
        
    @staticmethod
    def close(f, b=None):
        cv2 = mm._get_cv2()
        np = mm._get_np()
        if b is None: b = np.zeros((3,3), dtype='uint8')
        return cv2.morphologyEx(f, cv2.MORPH_CLOSE, b)

    @staticmethod
    def close0(f, B=None):
        np = mm._get_np()
        if B is None: B = np.ones((3,3), dtype='uint8')
        return mm.ero0(mm.dil0(f, B), B)

    @staticmethod
    def close1(f, b):
        return mm.ero1(mm.dil1(f, b), b)
    
    @staticmethod
    def openth(f, b=None):
        cv2 = mm._get_cv2()
        np = mm._get_np()
        if b is None: b = np.zeros((3,3), dtype='uint8')
        return mm.subm(f, cv2.morphologyEx(f, cv2.MORPH_OPEN, b))

    @staticmethod
    def openth1(f, b=None):
        np = mm._get_np()
        if b is None: b = np.zeros((3,3), dtype='uint8')
        return mm.subm(f, mm.dil1(mm.ero1(f,b), b))

    @staticmethod
    def closeth(f, b=None):
        cv2 = mm._get_cv2()
        np = mm._get_np()
        if b is None: b = np.zeros((3,3), dtype='uint8')
        return mm.subm(cv2.morphologyEx(f, cv2.MORPH_CLOSE, b), f)
    
    @staticmethod
    def closerecth(f, b=None):
        return mm.closeth(f, b)

    @staticmethod
    def asf(f, filter='OC', b=None, n=1):
        """Filtro sequencial alternado. filter: 'OC','CO','OCO','COC'."""
        cv2 = mm._get_cv2()
        np = mm._get_np()
        if b is None: b = np.zeros((3,3), dtype='uint8')
        seqs = {'OC':[cv2.MORPH_OPEN, cv2.MORPH_CLOSE],
                'CO':[cv2.MORPH_CLOSE, cv2.MORPH_OPEN],
                'OCO':[cv2.MORPH_OPEN, cv2.MORPH_CLOSE, cv2.MORPH_OPEN],
                'COC':[cv2.MORPH_CLOSE, cv2.MORPH_OPEN, cv2.MORPH_CLOSE]}
        y = f.copy()
        for i in range(n):
            bi = mm.sesum(b, i)
            for op in seqs.get(filter.upper(), []):
                y = cv2.morphologyEx(y, op, bi)
        return y

    # ── RECONSTRUÇÃO ─────────────────────────────────────────────────────────
    
    @staticmethod
    def cdil(f, g, b=None, n=1):
        """Dilatação geodésica do marcador f sob a máscara g."""
        cv2 = mm._get_cv2()
        np = mm._get_np()
        if b is None: b = np.zeros((3,3), dtype='uint8')
        y = f.copy()
        for _ in range(n):
            y = np.minimum(cv2.dilate(y, b), g)
        return y

    @staticmethod
    def cero(f, g, b=None, n=1):
        """Erosão geodésica do marcador f sob a máscara g."""
        cv2 = mm._get_cv2()
        np = mm._get_np()
        if b is None: b = np.zeros((3,3), dtype='uint8')
        y = f.copy()
        for _ in range(n):
            y = np.maximum(cv2.erode(y, b), g)
        return y

    @staticmethod
    def infrec(f, g, b=None):
        """Inf-reconstrução: dilata o marcador (f ∧ g) até convergir sob a máscara g."""
        cv2 = mm._get_cv2()
        np = mm._get_np()
        if b is None: b = np.zeros((3,3), dtype='uint8')
        y = np.minimum(f, g)
        y1 = np.full_like(f, 256, dtype=np.int16) 
        while not np.array_equal(y, y1):
            y1 = y.copy()
            y = np.minimum(cv2.dilate(y, b), g)
        return y.astype('uint8')

    @staticmethod
    def suprec(f, g, b=None):
        """Sup-reconstrução: erode o marcador (f ∨ g) até convergir sobre a máscara g."""
        cv2 = mm._get_cv2()
        np = mm._get_np()
        if b is None: b = np.zeros((3,3), dtype='uint8')
        y = np.maximum(f, g)
        y1 = np.full_like(f, -1, dtype=np.int16)
        while not np.array_equal(y, y1):
            y1 = y.copy()
            y = np.maximum(cv2.erode(y, b), g)
        return y.astype('uint8')

    @staticmethod
    def closerec(f, b=None, bc=None):
        np = mm._get_np()
        if b is None: b = np.zeros((3,3), dtype='uint8')
        if bc is None: bc = np.zeros((3,3), dtype='uint8')
        return mm.suprec(f, mm.dil(f,b), bc)

    @staticmethod
    def areaopen(f, a):
        """Remove componentes com área ≤ a."""
        cv2 = mm._get_cv2()
        np = mm._get_np()
        def _ao(img, area_lim):
            y = np.zeros(img.shape, dtype=int)
            if mm.binary(img):
                n, lbl = cv2.connectedComponents(img)
                for i in range(1, n):
                    area = np.sum(lbl==i)
                    if area > area_lim: y[lbl==i] = area
            else:
                hist, _ = np.histogram(img.ravel(), 256, [0,256])
                for cor, h in enumerate(hist):
                    if h and cor:
                        _, fc = cv2.threshold(img, cor, 255, cv2.THRESH_BINARY)
                        fo = _ao(fc, area_lim)
                        if fo.max()==0: break
                        y += fo
            return y
        return _ao(f, a)

    @staticmethod
    def gradm(f, b=None):
        """Gradiente morfológico: dil(f,b) - ero(f,b)."""
        np = mm._get_np()
        if b is None: b = np.zeros((3,3), dtype='uint8')
        return mm.subm(mm.dil(f,b), mm.ero(f,b))

    @staticmethod
    def grad0(f, b=None):
        """Gradiente Morfológico Plano: dil0(f, b) - ero0(f, b). Evidencia contornos."""
        np = mm._get_np()
        if b is None: b = np.ones((3,3), dtype='uint8')
        return mm.subm(mm.dil0(f, b), mm.ero0(f, b))

    @staticmethod
    def gradm1(f, b=None):
        """Gradiente morfológico: dil(f,b) - ero(f,b)."""
        np = mm._get_np()
        if b is None: b = np.zeros((3,3), dtype='uint8')
        return mm.subm(mm.dil1(f,b), mm.ero1(f,b))

    @staticmethod
    def tophat(f, b=None):
        """Top-hat: f - open(f, b). Realça detalhes brilhantes sobre fundo escuro."""
        np = mm._get_np()
        if b is None: b = np.zeros((3,3), dtype='uint8')
        return mm.subm(f, mm.open(f, b))

    @staticmethod
    def tophat0(f, b=None):
        """Top-hat Plano: f - open0(f, b). Realça picos brilhantes sem padding."""
        np = mm._get_np()
        if b is None: b = np.ones((3,3), dtype='uint8')
        return mm.subm(f, mm.open0(f, b))

    @staticmethod
    def tophat1(f, b=None):
        """Top-hat Plano: f - open0(f, b). Realça picos brilhantes sem padding."""
        np = mm._get_np()
        if b is None: b = np.zeros((3,3), dtype='uint8')
        return mm.subm(f, mm.open1(f, b))

    @staticmethod
    def blackhat(f, b=None):
        """Black-hat: close(f, b) - f. Realça detalhes escuros sobre fundo claro."""
        np = mm._get_np()
        if b is None: b = np.zeros((3,3), dtype='uint8')
        return mm.subm(mm.close(f, b), f)

    @staticmethod
    def blackhat0(f, b=None):
        """Black-hat Plano: close0(f, b) - f. Realça vales escuros sem padding."""
        np = mm._get_np()
        if b is None: b = np.ones((3,3), dtype='uint8')
        return mm.subm(mm.close0(f, b), f)

    @staticmethod
    def blackhat1(f, b=None):
        """Black-hat Plano: close0(f, b) - f. Realça vales escuros sem padding."""
        np = mm._get_np()
        if b is None: b = np.zeros((3,3), dtype='uint8')
        return mm.subm(mm.close1(f, b), f)
    
    # ── REGIÕES / RÓTULOS ─────────────────────────────────────────────────────

    @staticmethod
    def regmax(f, b=None):
        np = mm._get_np()
        if b is None: b = np.ones((3,3), dtype='uint8')
        k = 255 if f.max()<=255 else 65535
        return mm.union(mm.threshold(mm.subm(f, mm.infrec(mm.subm(f,1),f,b)),0),
                        mm.threshold(f,k))

    @staticmethod
    def regmin(f, b=None):
        np = mm._get_np()
        if b is None: b = np.ones((3,3), dtype='uint8')
        return mm.union(mm.threshold(mm.subm(mm.suprec(mm.addm(f,1),f,b),f),1),
                        mm.threshold(f,0))

    @staticmethod
    def label(f):
        cv2 = mm._get_cv2()
        _, lbl = cv2.connectedComponents(f)
        return lbl

    @staticmethod
    def label0(f, b=None):
        """Rotulagem por flood-fill com pilha."""
        np = mm._get_np()
        if b is None: b = np.ones((3,3), dtype='uint8')
        h, w = f.shape
        g = np.zeros(f.shape, dtype=int)
        cor = 1
        for x in range(h):
            for y in range(w):
                if f[x,y] and not g[x,y]:
                    pilha = [[x,y]]
                    while pilha:
                        i,j = pilha.pop(); g[i,j] = cor
                        for vy,vx,bv in mm._viz(f,b,i,j):
                            if bv and f[vy,vx] and not g[vy,vx]:
                                pilha.append([vy,vx])
                    cor += 1
        return g

    # ── WATERSHED ────────────────────────────────────────────────────────────

    @staticmethod
    def watershed0(f, mask=None, b=None, op='region'):
        np = mm._get_np()
        if b is None: b = np.ones((3,3), dtype='uint8')
        f = mm.label0(f, b); g = f.copy()
        mask = np.ones_like(f) if mask is None else (mask > 0)
        
        while g.min() == 0:
            mudou = False
            for x in range(f.shape[0]):
                for y in range(f.shape[1]):
                    if g[x,y] == 0 and mask[x,y]:
                        for vy,vx,bv in mm._viz(f, b, x, y):
                            if bv and g[x,y] < f[vy,vx]: 
                                g[x,y] = f[vy,vx]
                                mudou = True
            if not mudou: break
            f = g.copy()
            
        return g if op=='region' else mm.gradm(g, mm.secross())

    @staticmethod
    def watershedB(f, mask=None, b=None, op='region'):
        np = mm._get_np()
        if b is None: b = np.ones((3,3), dtype='uint8')
        m = mm.label0(f, b)
        h, w = m.shape
        mask = np.ones_like(m) if mask is None else (mask > 0)
        
        queue = []
        for x in range(h):
            for y in range(w):
                if m[x,y] > 0:
                    for vy, vx, bv in mm._viz(m, b, x, y):
                        if bv and m[vy,vx] == 0 and mask[vy,vx]:
                            queue.append((x, y))
                            break

        while queue:
            x, y = queue.pop(0)
            cor = m[x, y]
            for vy, vx, _ in mm._viz(m, b, x, y):
                if m[vy, vx] == 0 and mask[vy, vx]:
                    m[vy, vx] = cor
                    queue.append((vy, vx))
                    
        return m if op == 'region' else mm.gradm(m, mm.secross())
    
    @staticmethod
    def watershed(f, mask=None, b=None, op='region'):
        cv2 = mm._get_cv2()
        np = mm._get_np()
        if len(np.unique(f)) <= 2:
            _, m = cv2.connectedComponents(f.astype('uint8'))
        else:
            m = f.copy().astype('int32')
            
        mask = np.ones_like(m) if mask is None else (mask > 0)
        m[~mask] = 0
        
        markers = np.where((m == 0) & (~mask), -2, m).astype('int32')
        markers[(m == 0) & mask] = 0

        guidance = np.where(mask, 0, 255).astype(np.uint8)
        f_bgr = cv2.merge([guidance, guidance, guidance])
        
        cv2.watershed(f_bgr, markers)
        res = np.where((markers <= 0) | (~mask), 0, markers).astype('uint8')
        return res if op == 'region' else mm.gradm(res, mm.secross())

    # ── DISTÂNCIA / ESQUELETO ─────────────────────────────────────────────────

    @staticmethod
    def dist(f):
        cv2 = mm._get_cv2()
        y = cv2.distanceTransform(f, cv2.DIST_L2, 5)
        return y.astype('uint8') if y.max()<=255 else y.astype('uint16')

    @staticmethod
    def dist1(f, b):
        g = f.copy()
        while True:
            f=g.copy(); g=mm.ero1(g,b)
            if mm._get_np().array_equal(f,g): break
        return g

    @staticmethod
    def gdist(f, g, b=None):
        np = mm._get_np()
        if b is None: b = np.ones((3,3), dtype='uint8')
        h,w = f.shape; M=h*w
        fneg=(M-f*M).astype('uint16'); gneg=(1-g).astype('uint16')
        y,c = gneg,0
        while c<2000:
            c+=1; y0=y
            y = np.logical_xor(gneg,fneg)*(y+mm.cero(gneg,fneg,b,c))
            if np.array_equal(y0,y): break
        return y

    @staticmethod
    def thin(f):
        np = mm._get_np()
        from skimage.morphology import skeletonize
        return np.array(skeletonize(f), dtype='uint8')

    @staticmethod
    def skel(f):
        return mm._get_cv2().ximgproc.thinning(f)

    @staticmethod
    def skelm(f, b=None):
        np = mm._get_np()
        if b is None: b = np.zeros((3,3), dtype='uint8')
        img=f.copy(); skel=np.zeros(f.shape); n=0
        while img.max():
            nb=mm.sesum(b,n); ero=mm.ero1(img,nb)
            skel=np.maximum(skel, ero-mm.dil1(mm.ero1(ero,b),b)); n+=1
        return skel

    @staticmethod
    def esqueleto(f, b):
        """Esqueleto alternativo (lista3 2022.1)."""
        np = mm._get_np()
        img=f.copy(); skel=np.zeros(f.shape); n=0
        while img.max():
            abertura=mm.dil1(mm.ero1(img,b),b)
            skel=np.logical_or(skel,np.logical_and(img,np.logical_not(abertura))).astype(int)
            img=mm.ero1(img,mm.sesum(b,n)); n+=1
        return skel

    # ── OUTRAS OPERAÇÕES ──────────────────────────────────────────────────────

    @staticmethod
    def frame(f, border=5):
        np = mm._get_np()
        g=np.ones_like(f)*255; g[border:-border,border:-border]=0; return g

    @staticmethod
    def edgeoff(f, b=None, border=1):
        np = mm._get_np()
        if b is None: b = np.ones((3,3), dtype='uint8')
        marcador = mm.frame(f, border=border) & f
        return mm.subm(f, mm.infrec(marcador, f, b))

    @staticmethod
    def clohole(f, b=None):
        np = mm._get_np()
        if b is None: b = np.ones((3,3), dtype='uint8')
        marcador = mm.frame(f, border=1) & mm.neg(f)
        return mm.neg(mm.infrec(marcador, mm.neg(f), b))

    @staticmethod
    def hmin(f, h, b=None):
        np = mm._get_np()
        if b is None: b = np.ones((3,3), dtype='uint8')
        return mm.suprec(f, mm.addm(f,h), b)

    @staticmethod
    def toggle(f, f1, f2, op='gray'):
        np = mm._get_np()
        mask = np.logical_and(mm.subm(f,f1)<=f, f<=mm.subm(f2,f))
        if op=='gray':
            t=mask.astype('uint8')*255
            return mm.union(mm.intersec(mm.neg(t),f1), mm.intersec(t,f2))
        return mask

    @staticmethod
    def correlacao0(f, kernel, bias):
        np = mm._get_np()
        Bh,Bw = kernel.shape
        if Bh==Bw:
            H,W = f.shape[0]-Bh+1, f.shape[1]-Bw+1
            return np.array([[np.sum(f[i:i+Bh,j:j+Bw]*kernel)+bias
                              for j in range(W)] for i in range(H)]).astype(np.uint8)


    # ── BLOB / ANÁLISE DE COMPONENTES ────────────────────────────────────────

    @staticmethod
    def connectedComponents(img):
        """Rotula os componentes conexos de uma imagem binária."""
        return mm._get_cv2().connectedComponents(img)

    @staticmethod
    def findContours(img, mode=None, method=None):
        """Encontra os contornos de uma imagem binária."""
        cv2 = mm._get_cv2()
        if mode is None: mode = cv2.RETR_EXTERNAL
        if method is None: method = cv2.CHAIN_APPROX_SIMPLE
        contornos, _ = cv2.findContours(img.copy(), mode, method)
        return contornos

    @staticmethod
    def contourArea(contour):
        """Calcula a área de um contorno."""
        return mm._get_cv2().contourArea(contour)

    @staticmethod
    def arcLength(contour, closed=True):
        """Calcula o perímetro de um contorno."""
        return mm._get_cv2().arcLength(contour, closed)

    @staticmethod
    def boundingRect(contour):
        """Retorna o retângulo envolvente (x, y, largura, altura)."""
        return mm._get_cv2().boundingRect(contour)

    @staticmethod
    def minAreaRect(contour):
        """Retorna o menor retângulo que envolve o contorno."""
        return mm._get_cv2().minAreaRect(contour)

    @staticmethod
    def boxPoints(rect):
        """Obtém os quatro vértices de um retângulo."""
        return mm._get_cv2().boxPoints(rect).astype(int)

    @staticmethod
    def minEnclosingCircle(contour):
        """Retorna o menor círculo que envolve o contorno."""
        (x, y), r = mm._get_cv2().minEnclosingCircle(contour)
        return (int(x), int(y)), int(r)

    @staticmethod
    def fitEllipse(contour):
        """Ajusta uma elipse ao contorno. O contorno deve possuir pelo menos 5 pontos."""
        return mm._get_cv2().fitEllipse(contour)

    @staticmethod
    def convexHull(contour):
        """Retorna o fecho convexo do contorno."""
        return mm._get_cv2().convexHull(contour)

    @staticmethod
    def approxPolyDP(contour, precision=0.01, closed=True):
        """Aproxima um contorno por um polígono."""
        return mm._get_cv2().approxPolyDP(
            contour,
            precision * mm._get_cv2().arcLength(contour, closed),
            closed
        )

    @staticmethod
    def fitLine(contour):
        """Ajusta uma reta ao contorno."""
        cv2 = mm._get_cv2()
        return cv2.fitLine(contour, cv2.DIST_L2, 0, 0.01, 0.01)

    @staticmethod
    def measure(img: "np.ndarray", precision: float = 0.01) -> Optional[list[dict]]:
        """Extrai medidas geométricas dos objetos de uma imagem binária."""
        cv2 = mm._get_cv2()
        np = mm._get_np()
        if not mm.binary(img):
            return None
        medidas = []
        for i, c in enumerate(mm.findContours(img), 1):
            area = mm.contourArea(c)
            per = mm.arcLength(c)
            x, y, w, h = mm.boundingRect(c)
    
            M = cv2.moments(c)
            cx = M["m10"] / M["m00"] if M["m00"] else 0
            cy = M["m01"] / M["m00"] if M["m00"] else 0
    
            hull = mm.convexHull(c)
            hull_area = mm.contourArea(hull)
            poly = mm.approxPolyDP(c, precision)
    
            medidas.append(dict(
                id=i,
                area=area,
                perimeter=per,
                center=(cx, cy),
                bbox=(x, y, w, h),
                circularity=4 * np.pi * area / per**2 if per else 0,
                solidity=area / hull_area if hull_area else 0,
                vertices=len(poly)
            ))
        return medidas
        
    @staticmethod
    def saveMeasures(filename: str, measures: list[dict], fmt: str = "csv",
                    img_width: Optional[int] = None, img_height: Optional[int] = None,
                    class_id: int = 0) -> None:
        """Salva as medidas em CSV, texto simples ou formato YOLO."""
        header = None
    
        if fmt == "yolo":
            if img_width is None or img_height is None:
                raise ValueError("fmt='yolo' exige img_width e img_height")
    
            def linha(m):
                x, y, w, h = m["bbox"]
                xc, yc = (x + w / 2) / img_width, (y + h / 2) / img_height
                wn, hn = w / img_width, h / img_height
                return f"{class_id} {xc:.6f} {yc:.6f} {wn:.6f} {hn:.6f}"
    
        else:
            sep = "," if fmt == "csv" else " "
            if fmt == "csv":
                header = sep.join([
                    "id", "area", "perimeter", "cx", "cy", "x", "y", "w", "h",
                    "circularity", "solidity", "vertices"
                ])
    
            def linha(m):
                x, y, w, h = m["bbox"]
                cx, cy = m["center"]
                campos = [m["id"], m["area"], round(m["perimeter"], 2),
                        round(cx, 2), round(cy, 2), x, y, w, h,
                        round(m["circularity"], 3), round(m["solidity"], 3),
                        m["vertices"]]
                return sep.join(map(str, campos))
    
        with open(filename, "w") as f:
            if header:
                f.write(header + "\n")
            for m in measures:
                f.write(linha(m) + "\n")
    
    @staticmethod
    def IoU(boxA: tuple, boxB: tuple) -> float:
        """Intersection over Union entre duas bounding boxes (x, y, w, h)."""
        ax1, ay1, aw, ah = boxA
        bx1, by1, bw, bh = boxB
        ax2, ay2 = ax1 + aw, ay1 + ah
        bx2, by2 = bx1 + bw, by1 + bh
    
        ix1, iy1 = max(ax1, bx1), max(ay1, by1)
        ix2, iy2 = min(ax2, bx2), min(ay2, by2)
        iw, ih = max(0, ix2 - ix1), max(0, iy2 - iy1)
        inter = iw * ih
    
        union = aw * ah + bw * bh - inter
        return inter / union if union else 0.0
    
    @staticmethod
    def verifyBoundBox(object_id: int, bbox: tuple, matrix: "np.ndarray",
                        width: int, height: int, threshold: float = 0.5) -> int:
        """Conta quantos gabaritos do objeto `object_id` casam com `bbox` via IoU."""
        correct = 0
        for v in matrix[matrix[:, 0] == object_id]:
            x1, y1 = v[1] * width, v[2] * height
            x2, y2 = v[3] * width, v[4] * height
            gabarito_bbox = (x1, y1, x2 - x1, y2 - y1)
            if mm.IoU(bbox, gabarito_bbox) >= threshold:
                correct += 1
        return correct
    
    # ── BLOB / ANÁLISE DE COMPONENTES ANTIGO ────────────────────────────────────────

    @staticmethod
    def blob(f, op='area', border=1, precision=0.01, show='True'):
        """Topologia de componentes conexos antiga."""
        cv2 = mm._get_cv2()
        np = mm._get_np()
        if not mm.binary(f): return None
        measures = []
        color_img = cv2.cvtColor(f, cv2.COLOR_GRAY2RGB)
        cont, _ = cv2.findContours(f.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

        if op == 'area':
            color_img = np.zeros_like(f, dtype='uint32')
            n, lbl = cv2.connectedComponents(f)
            for i in range(1, n):
                area = np.sum(lbl==i); measures.append(area); color_img[lbl==i]=area

        elif op in ('textLabel','textPer','textArea'):
            for k,c in enumerate(cont):
                x,y,w,h = cv2.boundingRect(c)
                val = (k+1) if op=='textLabel' else \
                      int(cv2.arcLength(c,True)) if op=='textPer' else int(cv2.contourArea(c))
                measures.append(val)
                cv2.putText(color_img,str(val),(x+w//3,y+h//3),
                            cv2.FONT_HERSHEY_SIMPLEX,0.2,(255,0,0),border,cv2.LINE_AA)

        else:
            for c in cont:
                if op=='box':
                    box=np.int0(cv2.boxPoints(cv2.minAreaRect(c)))
                    measures.append(box); cv2.drawContours(color_img,[box],0,(255,0,0),border)
                elif op=='rect':
                    r=cv2.boundingRect(c); measures.append(list(r))
                    cv2.rectangle(color_img,r[:2],(r[0]+r[2],r[1]+r[3]),(0,255,0),border)
                elif op=='circle':
                    (cx,cy),rad=cv2.minEnclosingCircle(c)
                    center,rad=(int(cx),int(cy)),int(rad); measures.append([center,rad])
                    cv2.circle(color_img,center,rad,(0,255,0),border)
                elif op=='ellipse':
                    e=cv2.fitEllipse(c); measures.append(e)
                    cv2.ellipse(color_img,e,(0,255,0),border)
                elif op=='convex':
                    hull=cv2.convexHull(c); measures.append(hull)
                    cv2.drawContours(color_img,[hull],0,(255,0,0),border)
                elif op=='poly':
                    approx=cv2.approxPolyDP(c,precision*cv2.arcLength(c,True),True)
                    measures.append(approx); cv2.drawContours(color_img,[approx],0,(255,0,0),border)
                elif op=='line':
                    e=cv2.fitEllipse(c); cv2.ellipse(color_img,e,(255,0,0),border)
                    cols=f.shape[1]; vx,vy,x,y=cv2.fitLine(c,cv2.DIST_L2,0,0.01,0.01)
                    lefty=int((-x*vy/vx)+y); righty=int(((cols-x)*vy/vx)+y)
                    measures.append([vx,vy,x,y])
                    cv2.line(color_img,(cols-1,righty),(0,lefty),(0,255,0),border)

        if show: mm.show(color_img); return color_img
        return measures

    @staticmethod
    def blobAll(f, border=1, precision=0.01, show='False'):
        """Todas as medidas topológicas por componente."""
        cv2 = mm._get_cv2()
        np = mm._get_np()
        ops=['textLabel','textArea','textPer','box','rect','circle','ellipse','convex','poly','line']
        n, labels = cv2.connectedComponents(f)
        result = {k: [] for k in ops}
        for i in range(n):
            aux=np.zeros_like(labels,dtype='uint8'); aux[labels==i]=255
            for op in ops: result[op].append(mm.blob(aux,op,1,0.01,False)[0])
        return result

    @staticmethod
    def verifyBoundBox_old(object_lbl, center, matrix, width, height):
        """Verifica se centro do objeto está dentro do bounding box do gabarito (versão antiga)."""
        np = mm._get_np()
        correct = 0
        for v in matrix[matrix[:,0]==object_lbl]:
            p1=v[1:][:2]*[width,height]//1; p2=v[1:][2:]*[width,height]//1
            if (p1<np.array(center)).all() and (np.array(center)<p2).all(): correct+=1
        return correct
    
    # ── Aprendizado de máquina com VC ────────────────────────────────────────

    @staticmethod
    def readClasses():
        """Lê C e os C nomes de classe na mesma linha. Retorna a lista, na ordem de leitura."""
        linha = input().split()
        C = int(linha[0])
        return linha[1:1+C]
    
    @staticmethod
    def readDataset(num_linhas, D=2, label_type=None, label_pos='end'):
        """
        Lê 'num_linhas' de dados. 
        Se label_type for informado, lê os rótulos e retorna (X, y).
        Se label_type for None, lê apenas as D características e retorna X.
        """
        np = mm._get_np()
        X, y = [], []
        for _ in range(num_linhas):
            linha = input().split()
            if label_type is None:
                X.append([float(v) for v in linha[:D]])
            elif label_pos == 'end':
                X.append([float(v) for v in linha[:D]])
                y.append(label_type(linha[D]))
            else:  # 'start'
                X.append([float(v) for v in linha[1:1+D]])
                y.append(label_type(linha[0]))
                
        if label_type is None:
            return np.array(X)
        return np.array(X), np.array(y)
 
    @staticmethod
    def readTrain(N, D=2, label_type=int, label_pos='end'):
        return mm.readDataset(N, D, label_type, label_pos)

    @staticmethod
    def readTest(Q, D=2, label_type=None, label_pos='end'):
        return mm.readDataset(Q, D, label_type, label_pos)

    # ── k-NN (binário e multi-classe unificados) ─────────────────────────────
    @staticmethod
    def knn0(X_train, y_train, x_test, k, metric='euclidiana', num_classes=2, desempate='proximo'):
        """(didático) k-NN genérico — serve tanto para o caso binário quanto multi-classe.
        metric: 'euclidiana' ou 'manhattan'.
        desempate: 'proximo'  -> decide o vizinho mais próximo entre as classes empatadas (padrão do caso binário)
                'menor_id' -> decide a menor classe entre as empatadas (padrão do caso multi-classe)
        """
        np = mm._get_np()
        if metric == 'euclidiana':
            d = np.sqrt(np.sum((X_train - x_test) ** 2, axis=1))
        else:  # manhattan
            d = np.sum(np.abs(X_train - x_test), axis=1)
        viz = y_train[np.argsort(d, kind='mergesort')[:k]]      # k mais próximos (ordenação estável)
        contagem = np.bincount(viz, minlength=num_classes)
        empatadas = np.where(contagem == np.max(contagem))[0]   # classes com mais votos
        if desempate == 'menor_id':
            return int(empatadas[0])                            # já em ordem crescente de classe
        for c in viz:                                            # 'proximo': percorre do mais perto ao mais longe
            if c in empatadas:
                return int(c)

    @staticmethod
    def knn(X_train, y_train, x_test, k, metric='euclidiana'):
        """(clássico) k-NN via sklearn — serve tanto para binário quanto multi-classe."""
        p = 1 if metric == 'manhattan' else 2
        clf = mm._get_sklneighbors().KNeighborsClassifier(n_neighbors=k, p=p)
        clf.fit(X_train, y_train)
        return int(clf.predict([x_test])[0])
    
    # ── Normalização z-score ──────────────────────────────────────────────────
    @staticmethod
    def zscore0(X_train, X_test):
        """(didático) Normalização z-score (média/desvio padrão populacional)."""
        np = mm._get_np()
        m, s = np.mean(X_train, axis=0), np.std(X_train, axis=0)
        s_safe = np.where(s == 0, 1, s)                        # evita divisão por zero
        return np.where(s == 0, 0.0, (X_train - m) / s_safe), np.where(s == 0, 0.0, (X_test - m) / s_safe)
 
    @staticmethod
    def zscore(X_train, X_test):
        """(clássico) Normalização z-score via sklearn.preprocessing.StandardScaler."""
        scaler = mm._get_sklpreprocessing().StandardScaler()
        return scaler.fit_transform(X_train), scaler.transform(X_test)
    
    # ── Matriz de confusão / métricas (binário e multi-classe unificados) ───
    @staticmethod
    def confusion0(y_true, y_pred, pos_label=1, num_classes=None):
        """(didático) Métricas de classificação.
        - Sem num_classes (padrão): modo binário — retorna VP, FP, FN, VN, acurácia,
        precisão e revocação da classe pos_label.
        - Com num_classes: modo multi-classe — retorna a matriz de confusão C x C,
        acurácia global, precisão macro e revocação macro."""
        np = mm._get_np()
        if num_classes is not None:
            cm = np.zeros((num_classes, num_classes), dtype=int)
            for r, p in zip(y_true, y_pred): cm[r, p] += 1
            acuracia = np.trace(cm) / np.sum(cm) if np.sum(cm) > 0 else 0.0
            precisoes, revocacoes = [], []
            for c in range(num_classes):
                vp = cm[c, c]
                fp = np.sum(cm[:, c]) - vp
                fn = np.sum(cm[c, :]) - vp
                precisoes.append(vp / (vp + fp) if (vp + fp) > 0 else 0.0)
                revocacoes.append(vp / (vp + fn) if (vp + fn) > 0 else 0.0)
            return cm, acuracia, np.mean(precisoes), np.mean(revocacoes)

        # modo binário
        classes = np.unique(np.concatenate([y_true, y_pred, [pos_label, 0]]))
        neg_label = classes[classes != pos_label][0]
        acuracia = np.sum(y_true == y_pred) / len(y_true) if len(y_true) > 0 else 0.0
        VP = int(np.sum((y_true == pos_label) & (y_pred == pos_label)))
        FP = int(np.sum((y_true != pos_label) & (y_pred == pos_label)))
        FN = int(np.sum((y_true == pos_label) & (y_pred != pos_label)))
        VN = int(np.sum((y_true == neg_label) & (y_pred == neg_label)))
        precisao = (VP / (VP + FP)) if (VP + FP) > 0 else "indefinida"
        revocacao = (VP / (VP + FN)) if (VP + FN) > 0 else "indefinida"
        return VP, FP, FN, VN, acuracia, precisao, revocacao
    
    @staticmethod
    def confusion(y_true, y_pred, pos_label=1, num_classes=None):
        """(clássico) Matriz de confusão e métricas via sklearn.metrics.
        - Sem num_classes: modo binário — VP, FP, FN, VN, acurácia, precisão, revocação
        da classe pos_label.
        - Com num_classes: modo multi-classe — cm, acurácia, precisão macro,
        revocação macro."""
        m = mm._get_sklmetrics()
        if num_classes is not None:
            cm = m.confusion_matrix(y_true, y_pred, labels=range(num_classes))  # força C x C mesmo se alguma classe não aparecer
            acuracia = m.accuracy_score(y_true, y_pred)
            precisao_macro = m.precision_score(y_true, y_pred, average='macro', zero_division=0)
            revocacao_macro = m.recall_score(y_true, y_pred, average='macro', zero_division=0)
            return cm, acuracia, precisao_macro, revocacao_macro

        VN, FP, FN, VP = m.confusion_matrix(y_true, y_pred, labels=[0, pos_label]).ravel()
        acuracia = m.accuracy_score(y_true, y_pred)
        precisao = m.precision_score(y_true, y_pred, pos_label=pos_label, zero_division="warn")
        revocacao = m.recall_score(y_true, y_pred, pos_label=pos_label, zero_division="warn")
        return int(VP), int(FP), int(FN), int(VN), acuracia, precisao, revocacao

    # ── LBP (Local Binary Pattern) ────────────────────────────────────────────
    @staticmethod
    def lbp0(f, r=None, c=None, S=None):
        """(didático) LBP — três modos, escolhidos pelos parâmetros informados:
        1) lbp0(f)                    -> mapa completo: retorna (lbp_map, trans_map)
                                        para toda a imagem f (bordas globais zeradas).
        2) lbp0(f, r, c)               -> pixel único: retorna (lbp_codigo, transicoes,
                                        se você já tem só o bloco 3x3 f, chame
                                        com lbp0(f, 1, 1)]
        3) lbp0(f, r, c, S)             -> histograma de bloco: retorna H (10 compartimentos,
                                        normalizado) do bloco S x S com canto em (r, c),
                                        excluindo pixels de borda global da imagem f.
        """
        np = mm._get_np()
        L, C = f.shape
        dr, dc = [-1, -1, -1, 0, 1, 1, 1, 0], [-1, 0, 1, 1, 1, 0, -1, -1]  # 8 vizinhos, sentido horário

        # calcula sempre o mapa completo (base para os três modos)
        lbp_map, trans_map = np.zeros((L, C), dtype=np.int32), np.zeros((L, C), dtype=np.int32)
        bits = np.array([np.where(f[1+dri:L-1+dri, 1+dci:C-1+dci] >= f[1:L-1, 1:C-1], 1, 0)
                        for dri, dci in zip(dr, dc)])
        potencias = (2 ** np.arange(8))[:, np.newaxis, np.newaxis]
        lbp_map[1:L-1, 1:C-1] = np.sum(bits * potencias, axis=0)
        trans_map[1:L-1, 1:C-1] = np.sum(bits != np.roll(bits, -1, axis=0), axis=0)

        if r is None:                                     # modo 1: mapa completo
            return lbp_map, trans_map

        if S is None:                                      # modo 2: pixel único
            codigo, transicoes = int(lbp_map[r, c]), int(trans_map[r, c])
            classificacao = "UNIFORME" if transicoes <= 2 else "NAO_UNIFORME"
            return codigo, transicoes, classificacao

        # modo 3: histograma de bloco
        bloco_lbp = lbp_map[r:r+S, c:c+S]
        bloco_trans = trans_map[r:r+S, c:c+S]
        r_idx, c_idx = np.ogrid[r:r+S, c:c+S]
        valida = (r_idx > 0) & (r_idx < L - 1) & (c_idx > 0) & (c_idx < C - 1)
        lbp_validos, trans_validos = bloco_lbp[valida], bloco_trans[valida]

        H = np.zeros(10, dtype=np.float64)
        if len(lbp_validos) == 0: return H
        for l, t in zip(lbp_validos, trans_validos):
            idx = bin(int(l))[2:].count('1') if t <= 2 else 9   # uniforme: popcount / não-uniforme: bin 9
            H[idx] += 1
        return H / np.sum(H)

    @staticmethod
    def lbp(f, P=8, R=1, method='uniform', r=None, c=None, S=None):
        """(clássico) LBP via skimage.feature.local_binary_pattern.
        - Sem r/c/S: retorna o mapa LBP completo (igual ao lbp original).
        - Com r, c, S: retorna o histograma (10 compartimentos, normalizado) do bloco
        S x S com canto em (r, c), calculado a partir do mapa LBP uniforme
        (categorias 0-8 = nº de bits 1 do padrão uniforme, categoria 9 = não-uniforme —
        mapeamento direto do método 'uniform' do skimage)."""
        mapa = mm._get_skfeature().local_binary_pattern(f, P=P, R=R, method=method)
        if r is None:
            return mapa
        np = mm._get_np()
        bloco = mapa[r:r+S, c:c+S].astype(int)
        H, _ = np.histogram(bloco, bins=np.arange(P + 3))   # P+1 categorias uniformes + 1 não-uniforme
        return H / np.sum(H) if np.sum(H) > 0 else H.astype(np.float64)
    
    # ── HOG (Histogram of Oriented Gradients) ────────────────────────────────
    @staticmethod
    def hog0(magnitudes, orientacoes, B):
        """(didático) Histograma bruto e normalizado (L2) das orientações do gradiente de uma célula."""
        np = mm._get_np()
        bins = np.clip(np.floor(orientacoes / (180.0 / B)).astype(int), 0, B - 1)
        H = np.bincount(bins.ravel(), weights=magnitudes.ravel(), minlength=B).astype(np.float64)
        H_hat = H / np.sqrt(np.sum(H ** 2) + 1e-6)   # epsilon evita divisão por zero
        return H, H_hat
 
    @staticmethod
    def hog(f, orientations=9, pixels_per_cell=(8, 8), cells_per_block=(1, 1)):
        """(clássico) Descritor HOG via skimage.feature.hog."""
        feature = mm._get_skfeature()
        return feature.hog(f, orientations=orientations, pixels_per_cell=pixels_per_cell,
                            cells_per_block=cells_per_block, feature_vector=True)

    # ── DOMÍNIO DA FREQUÊNCIA (cap05) ──────────────────────────────────────
    # Espelham mm::distCenter / mm::freqFilter / mm::spectrumMag / mm::dct2 /
    # mm::idct2 da morph.hpp — mesmo resultado nas trilhas Python e C++.

    @staticmethod
    def distCenter(M, N):
        """distancia_centro: matriz M×N com a distância de (u,v) ao centro (M/2, N/2) do espectro centrado."""
        np = mm._get_np()
        u = np.arange(M) - M // 2
        v = np.arange(N) - N // 2
        V, U = np.meshgrid(v, u)
        return np.sqrt(U ** 2 + V ** 2)

    @staticmethod
    def freqFilter(img, H):
        """aplicar_filtro_freq: aplica o filtro centrado H (mesmo shape da imagem) via FFT; devolve uint8 [0,255]."""
        np = mm._get_np(); cv2 = mm._get_cv2()
        if getattr(img, "ndim", 2) == 3:
            img = mm.gray(img)
        F = np.fft.fftshift(np.fft.fft2(img.astype(np.float64)))
        g = np.real(np.fft.ifft2(np.fft.ifftshift(F * H)))
        return cv2.normalize(g, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)

    @staticmethod
    def spectrumMag(img):
        """Espectro de magnitude para visualização: log(1+|F|) centrado e normalizado [0,255]."""
        np = mm._get_np(); cv2 = mm._get_cv2()
        if getattr(img, "ndim", 2) == 3:
            img = mm.gray(img)
        F = np.fft.fftshift(np.fft.fft2(img.astype(np.float64)))
        return cv2.normalize(np.log1p(np.abs(F)), None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)

    @staticmethod
    def psnr(a, b):
        """PSNR (dB) entre duas imagens uint8 — espelha mm::psnr / cv2.PSNR."""
        cv2 = mm._get_cv2()
        return cv2.PSNR(a, b)

    @staticmethod
    def spatialKernel(H):
        """Resposta espacial de um filtro real centrado H: fftshift(real(ifft2(ifftshift(H)))),
        normalizada [0,255]. Espelha mm::spatialKernel."""
        np = mm._get_np(); cv2 = mm._get_cv2()
        sp = np.fft.fftshift(np.real(np.fft.ifft2(np.fft.ifftshift(np.asarray(H, np.float64)))))
        return cv2.normalize(sp, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)

    @staticmethod
    def wavefun(name, level=6):
        """(x, phi, psi) da wavelet `name`. Usa PyWavelets quando disponível;
        senão, algoritmo em cascata (espelha mm::wavefun)."""
        np = mm._get_np()
        try:
            import pywt
            phi, psi, x = pywt.Wavelet(name).wavefun(level=level)
            return np.asarray(x), np.asarray(phi), np.asarray(psi)
        except Exception:
            pass
        _tbl = {
            "haar": [0.7071067811865476, 0.7071067811865476],
            "db4": [0.2303778133088965, 0.7148465705529157, 0.6308807679298589,
                    -0.02798376941685985, -0.18703481171909309, 0.03084138183556076,
                    0.0328830116668852, -0.01059740178506903],
        }
        rl = np.asarray(_tbl.get(name, _tbl["haar"]))
        rh = rl[::-1] * (np.array([(-1) ** k for k in range(len(rl))]))
        p = np.array([1.0]); q = np.array([1.0])
        for _ in range(max(1, level)):
            pu = np.zeros(len(p) * 2 - 1); pu[::2] = p
            p, q = np.convolve(pu, rl) * np.sqrt(2), np.convolve(pu, rh) * np.sqrt(2)
        x = np.linspace(0, len(rl) - 1, len(p))
        return x, p, q

    @staticmethod
    def dct2(block):
        """DCT-II 2D ortonormal (scipy.fft.dct norm='ortho', separável) — == cv::dct do OpenCV."""
        from scipy.fft import dct
        return dct(dct(block.T, norm="ortho").T, norm="ortho")

    @staticmethod
    def idct2(coefs):
        """IDCT-II 2D ortonormal."""
        from scipy.fft import idct
        return idct(idct(coefs.T, norm="ortho").T, norm="ortho")

    # Construtores de filtro no domínio da frequência (H centrado, DC no meio).
    # highpass=True devolve o complemento (1 - H). Espelham mm::gaussFilter /
    # mm::idealFilter / mm::butterFilter da morph.hpp.

    @staticmethod
    def gaussFilter(M, N, D0, highpass=False):
        """Filtro Gaussiano passa-baixa H(u,v) = exp(-D²/(2·D0²)) (ou 1-H se highpass)."""
        np = mm._get_np()
        lp = np.exp(-(mm.distCenter(M, N) ** 2) / (2.0 * D0 ** 2))
        return (1.0 - lp) if highpass else lp

    @staticmethod
    def idealFilter(M, N, D0, highpass=False):
        """Filtro ideal (corte abrupto em D0) (ou seu complemento se highpass)."""
        np = mm._get_np()
        lp = (mm.distCenter(M, N) <= D0).astype(np.float64)
        return (1.0 - lp) if highpass else lp

    @staticmethod
    def butterFilter(M, N, D0, n=2, highpass=False):
        """Filtro Butterworth de ordem n: 1/(1+(D/D0)^(2n)) (ou seu complemento se highpass)."""
        D = mm.distCenter(M, N)
        lp = 1.0 / (1.0 + (D / D0) ** (2 * n))
        return (1.0 - lp) if highpass else lp

    @staticmethod
    def jpegCompress(img, quality):
        """Pipeline JPEG simplificado: DCT 8×8 -> quantização (tabela de luminância
        escalada por `quality` em 1..100) -> dequantização -> IDCT. Espelha mm::jpegCompress."""
        np = mm._get_np()
        QL = np.array([
            [16, 11, 10, 16, 24, 40, 51, 61], [12, 12, 14, 19, 26, 58, 60, 55],
            [14, 13, 16, 24, 40, 57, 69, 56], [14, 17, 22, 29, 51, 87, 80, 62],
            [18, 22, 37, 56, 68, 109, 103, 77], [24, 35, 55, 64, 81, 104, 113, 92],
            [49, 64, 78, 87, 103, 121, 120, 101], [72, 92, 95, 98, 112, 100, 103, 99],
        ], dtype=np.float64)
        quality = int(max(1, min(100, quality)))
        escala = 5000.0 / quality if quality < 50 else 200.0 - 2.0 * quality
        Q = np.clip(np.round(QL * escala / 100.0), 1.0, 255.0)
        if getattr(img, "ndim", 2) == 3:
            img = mm.gray(img)
        src = img.astype(np.float64)
        h, w = src.shape
        out = np.zeros((h, w), np.float64)
        for r in range(0, h - 7, 8):
            for c in range(0, w - 7, 8):
                C = mm.dct2(src[r:r+8, c:c+8] - 128.0)
                Cq = np.round(C / Q) * Q
                out[r:r+8, c:c+8] = mm.idct2(Cq) + 128.0
        return np.clip(out, 0, 255).astype(np.uint8)

    @staticmethod
    def lineChart(xs, ys, labels=None, colors=None, title="", xlabel="", ylabel="",
                  width=760, height=420, logx=False, logy=False):
        """Gráfico de linhas header-only (substitui matplotlib na trilha C++).
        `xs[k]`/`ys[k]` = k-ésima curva; `colors` em BGR. Espelha mm::lineChart."""
        np = mm._get_np(); cv2 = mm._get_cv2()
        ys = [np.asarray(y, dtype=np.float64) for y in ys]
        # `xs` pode ser um único eixo x compartilhado (sequência de números) ou
        # uma lista de eixos (um por curva). Detecta pelo 1º elemento.
        shared = len(xs) == 0 or np.isscalar(xs[0]) or np.ndim(xs[0]) == 0
        if shared:
            xs = [np.asarray(xs, dtype=np.float64)] * len(ys)
        else:
            xs = [np.asarray(x, dtype=np.float64) for x in xs]
        CYCLE = [(48, 90, 216), (117, 158, 29), (183, 74, 83), (40, 39, 214),
                 (148, 103, 189), (75, 119, 44), (33, 145, 237)]
        colors = colors or []
        labels = labels or []
        tx = (lambda v: np.log10(np.maximum(v, 1e-12))) if logx else (lambda v: v)
        ty = (lambda v: np.log10(np.maximum(v, 1e-12))) if logy else (lambda v: v)
        allx = np.concatenate([tx(x) for x in xs]); ally = np.concatenate([ty(y) for y in ys])
        allx = allx[np.isfinite(allx)]; ally = ally[np.isfinite(ally)]
        xmin, xmax = float(allx.min()), float(allx.max())
        ymin, ymax = float(ally.min()), float(ally.max())
        if xmax <= xmin: xmax = xmin + 1
        if ymax <= ymin: ymax = ymin + 1
        pad = 0.06 * (ymax - ymin); ynonneg = ymin >= 0.0
        ymin -= pad; ymax += pad
        if ynonneg and ymin < 0.0: ymin = 0.0
        L, Rm, Tm, Bm = 62, 18, (18 if not title else 40), 46
        cnv = np.full((height, width, 3), 255, np.uint8)
        px0, py0, pw, ph = L, Tm, width - L - Rm, height - Tm - Bm
        cv2.rectangle(cnv, (px0, py0), (px0 + pw, py0 + ph), (150, 150, 150), 1)
        PX = lambda X: int(round(px0 + (tx(X) - xmin) / (xmax - xmin) * pw))
        PY = lambda Y: int(round(py0 + ph - (ty(Y) - ymin) / (ymax - ymin) * ph))
        for i in range(6):
            gx = px0 + pw * i // 5
            cv2.line(cnv, (gx, py0), (gx, py0 + ph), (230, 230, 230), 1)
            X = xmin + (xmax - xmin) * i / 5.0
            cv2.putText(cnv, f"{(10**X if logx else X):.3g}", (gx - 14, py0 + ph + 16),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.38, (90, 90, 90), 1, cv2.LINE_AA)
        for j in range(5):
            gy = py0 + ph - ph * j // 4
            cv2.line(cnv, (px0, gy), (px0 + pw, gy), (230, 230, 230), 1)
            Y = ymin + (ymax - ymin) * j / 4.0
            cv2.putText(cnv, f"{(10**Y if logy else Y):.3g}", (6, gy + 4),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.38, (90, 90, 90), 1, cv2.LINE_AA)
        for k in range(len(xs)):
            col = colors[k] if k < len(colors) else CYCLE[k % len(CYCLE)]
            pts = [(PX(a), PY(b)) for a, b in zip(xs[k], ys[k])]
            for a, b in zip(pts[:-1], pts[1:]):
                cv2.line(cnv, a, b, col, 2, cv2.LINE_AA)
            for p in pts:
                cv2.circle(cnv, p, 2, col, -1, cv2.LINE_AA)
        if labels:
            maxlen = max(len(str(s)) for s in labels)
            boxw = min(pw - 20, 34 + maxlen * 7)
            lx = px0 + pw - boxw
            for k in range(len(labels)):
                col = colors[k] if k < len(colors) else CYCLE[k % len(CYCLE)]
                ly = py0 + 14 + k * 16
                cv2.line(cnv, (lx, ly), (lx + 20, ly), col, 2, cv2.LINE_AA)
                cv2.putText(cnv, str(labels[k]), (lx + 25, ly + 4),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.38, (60, 60, 60), 1, cv2.LINE_AA)
        if title:
            cv2.putText(cnv, title, (L, 26), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (30, 30, 30), 1, cv2.LINE_AA)
        if xlabel:
            cv2.putText(cnv, xlabel, (width // 2 - 40, height - 8),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, (60, 60, 60), 1, cv2.LINE_AA)
        if ylabel:
            cv2.putText(cnv, ylabel, (6, Tm - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (60, 60, 60), 1, cv2.LINE_AA)
        return cnv

    # ---- Aprendizado Profundo

import matplotlib.patches as mpatches
# % matplotlib inline
import matplotlib.pyplot as plt
import numpy as np
from flask import Flask
from flask import request
from flask_restful import Api
from guppy import hpy
from scipy import ndimage
from scipy import ndimage as ndi
from skimage import filters, morphology, color, exposure, img_as_float
from skimage import io
from skimage.color import label2rgb
from skimage.filters.rank import median, mean
from skimage.measure import regionprops
from skimage.morphology import dilation, opening, erosion
from skimage.morphology import disk
from skimage.morphology import remove_small_objects
from skimage.transform import rescale

# tracemalloc.start()
# s=None
# print(psutil.Process(os.getpid()).memory_info())


application = app = Flask(__name__)
api = Api(app)


# class GlassApp(Resource):
@app.route('/')
def get():
    # gc.collect()
    return form_labels()


def form_labels():
    global s
    trace = request.args.get('trace', None)

    h = hpy()
    # img_file = Image.open(request.files['file'])
    d1 = disk(1)  # (EROSION)Thickness improvement
    d2 = disk(10)  # opening radius
    d3 = disk(5)  # Noise reduction                     ###
    d4 = disk(5)  # smoothing
    d5 = disk(2)  # Dilation

    URL = 'test.jpg'  # 'A1.Bright.jpg'
    bimg1 = io.imread(URL)
    #YOU COULD ALSO RESIZE THE IMAGE TO 80% or 90%
    bimg=rescale(bimg1,0.8,anti_aliasing=True)
    # bimg = img_file
    cimg = bimg
    image = img_as_float(cimg)

    gamma_corrected = exposure.adjust_gamma(image, 1)
    gamma_corrected = exposure.equalize_hist(gamma_corrected)
    gamma_corrected = exposure.equalize_adapthist(gamma_corrected)
    gamma_corrected = exposure.rescale_intensity(gamma_corrected)

    img = gamma_corrected
    imgg = color.rgb2gray(img)
    imgg1 = mean(imgg, d4)
    imgg2 = median(imgg1, d3)
    dilated = dilation(imgg2, d5)
    eroded = erosion(dilated, d1)
    thresh = filters.threshold_adaptive(eroded, 253, method='gaussian')
    #thresh = filters.gaussian(eroded, 253, method='gaussian')

    BW = imgg >= thresh

    BW_smt = remove_small_objects(BW, 500)
    opened = opening(BW_smt, d2)

    distance = ndi.distance_transform_edt(~BW_smt)
    labels = morphology.label(~opened, background=-1)
    labels = morphology.remove_small_objects(labels, 500)
    plt.imshow(labels, cmap='jet', interpolation='nearest')
    a=np.unique(labels)
    ans = a.shape

    # Trying to delete the variables which are not used further

    # var_list=[gamma_corrected,img,imgg,imgg1,imgg2,dilated,eroded,thresh,BW,BW_smt,opened,distance]
    #
    # for i in var_list:
    #     del i
    #
    # del var_list
    del gamma_corrected
    del img
    del imgg
    del imgg1
    del imgg2
    del dilated
    del eroded
    del thresh
    #thresh = filters.gaussian(eroded, 253, method='gaussian')
    del BW
    del BW_smt
    del opened
    del distance
    #gc.collect()

    print(len(a))

    import warnings
    warnings.filterwarnings('ignore')
    #print(a)
    props = regionprops(labels)
    END = []
    for i in range(len(a) - 1):
        if (1 in props[i].coords.T[0]) or (labels.shape[0] - 1 in props[i].coords.T[0]) or (
                1 in props[i].coords.T[1]) or (labels.shape[1] - 1 in props[i].coords.T[1]):
            END.append(i)
        else:
            continue

    # print(len(END), 'End Pieces')
    # print(END)

    X = []
    Y = []
    for i in a[1:]:
        X.append(ndimage.measurements.center_of_mass(labels == i)[1])
        Y.append(ndimage.measurements.center_of_mass(labels == i)[0])

    label_overlay = label2rgb(labels, image=image)

    fig, ax = plt.subplots(ncols=1, nrows=1, figsize=(6, 6))
    ax.imshow(label_overlay)

    props = regionprops(labels)
    del a
    for i in range(len(regionprops(labels))):
        if props[i].area < 100:
            continue
        if i in END:
            minr, minc, maxr, maxc = props[i].bbox
            rect = mpatches.Rectangle((minc, minr), maxc - minc, maxr - minr,
                                      fill=False, edgecolor='white', linewidth=1)
        else:
            minr, minc, maxr, maxc = props[i].bbox
            rect = mpatches.Rectangle((minc, minr), maxc - minc, maxr - minr,
                                      fill=False, edgecolor='red', linewidth=1)

        ax.add_patch(rect)

    del props

    # s1 = tracemalloc.take_snapshot()
    # top_stats = s1.statistics('lineno')
    # for stat in top_stats[:10]:
    #     print(stat)
    #
    # print(s1)

    plt.savefig('final_test.jpg', box_inches='tight')
    plt.show()
    # filename = 'final_fig.jpg'
    # return send_file(filename, mimetype='image')
    print(h.heap())
    del h
    # print(psutil.Process(os.getpid()).memory_info())

    return "Success"


# url = "testing/test1.jpg"
# form_labels(url)
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)

#
# api.add_resource(GlassApp, '/')

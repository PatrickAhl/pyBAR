﻿import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from mpl_toolkits.axes_grid1 import make_axes_locatable
import pandas as pd
import itertools
import re
from matplotlib import colors, cm
from matplotlib.backends.backend_pdf import PdfPages

import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - [%(levelname)-8s] (%(threadName)-10s) %(message)s")


def plotOccupancy(occupancy_hist, median=False, max_occ=None, filename=None):
    plt.clf()
    H = occupancy_hist
    extent = [0.5, 80.5, 336.5, 0.5]
    #cmap = cm.get_cmap('copper_r')
    cmap = cm.get_cmap('PuBu', 10)
    if median:
        ceil_number = round_to_multiple(np.median(H[H > 0] * 2) if max_occ == None else max_occ, 10)
    else:
        ceil_number = round_to_multiple(H.max() if max_occ == None else max_occ, 10)
    #         ceil_number = round_to_multiple(int(H.max()) if max_occ == None else max_occ, 255)

    if(ceil_number < 10):
        ceil_number = 10
    bounds = range(0, ceil_number + 1, ceil_number / 10)
    norm = colors.BoundaryNorm(bounds, cmap.N)
    #     if (ceil_number<255):
    #         ceil_number = 255
    #     bounds = range(0, ceil_number+1, 255/ceil_number)
    #     norm = colors.BoundaryNorm(bounds, cmap.N)
    plt.imshow(H, interpolation='nearest', aspect="auto", cmap=cmap, norm=norm, extent=extent)  # for monitoring
    plt.title('Occupancy (' + str(np.sum(H)) + ' entries)')
    plt.xlabel('Column')
    plt.ylabel('Row')
    plt.colorbar(boundaries=bounds, cmap=cmap, norm=norm)
    if filename is None:
        plt.show()
    elif type(filename) == PdfPages:
        filename.savefig()
    else:
        plt.savefig(filename)


def make_occupancy(cols, rows, max_occ=None, ncols=80, nrows=336):
    plt.clf()
    H, xedges, yedges = np.histogram2d(rows, cols, bins=(nrows, ncols), range=[[1, nrows], [1, ncols]])
    #print xedges, yedges
    extent = [yedges[0] - 0.5, yedges[-1] + 0.5, xedges[-1] + 0.5, xedges[0] - 0.5]
    #plt.pcolor(H)
    cmap = cm.get_cmap('hot', 20)
    ceil_number = round_to_multiple(H.max() if max_occ == None else max_occ, 10)
    bounds = range(0, ceil_number + 1, ceil_number / 10)
    norm = colors.BoundaryNorm(bounds, cmap.N)
    plt.imshow(H, interpolation='nearest', aspect="auto", cmap=cmap, norm=norm, extent=extent)  # for monitoring
    plt.title('Occupancy')
    plt.xlabel('Column')
    plt.ylabel('Row')
#     for ypos in range(0,nrows,336):
#         plt.axhline(y=ypos, xmin=0, xmax=1)
#     for xpos in range(0,ncols,80):
#         plt.axvline(x=xpos, ymin=0, ymax=1)
    plt.colorbar(boundaries=bounds, cmap=cmap, norm=norm, ticks=bounds)


def plot_occupancy(cols, rows=None, max_occ=None, filename=None, title=None, ncols=80, nrows=336):
    if(rows == None):
        cols = 0
        rows = 0
    make_occupancy(cols, rows, max_occ, ncols, nrows)
    if(title != None):
        plt.title(title)
#     fig = plt.figure()
#     fig.patch.set_facecolor('white')
    if filename is None:
        plt.show()
    elif type(filename) == PdfPages:
        filename.savefig()
    else:
        plt.savefig(filename)


def round_to_multiple(number, multiple):
    '''Rounding up to the nearest multiple of any positive integer

    Parameters
    ----------
    number : int, float
        Input number.
    multiple : int
        Round up to multiple of multiple.
    Returns
    -------
    ceil_mod_number : int
        Rounded up number.
    '''
    ceil_mod_number = number - number % (-multiple)
    return ceil_mod_number


def plot_relative_bcid(relative_bcid_hist, filename=None):
    plt.clf()
    fig = plt.figure()
    fig.patch.set_facecolor('white')
    plt.bar(range(0, 16), relative_bcid_hist[:], color='r', align='center')  # bug: https://github.com/matplotlib/matplotlib/issues/1882, log = True
    plt.xlabel('relative BCID [25 ns]')
    plt.ylabel('#')
    plt.yscale('log')
    plt.title('Relative BCID (former LVL1ID)')
    plt.xlim((0, 16))
    plt.grid(True)
    if filename is None:
        plt.show()
    elif type(filename) == PdfPages:
        filename.savefig()
    else:
        plt.savefig(filename)


def plot_tot(tot_hist, filename=None):
    plt.clf()
    fig = plt.figure()
    fig.patch.set_facecolor('white')
    plt.bar(range(0, 16), tot_hist[:], color='b', align='center')
    plt.xlim((0, 15))
    plt.xlabel('TOT [25 ns]')
    plt.ylabel('#')
    plt.title('Time over threshold distribution (TOT code)')
    plt.grid(True)
    if filename is None:
        plt.show()
    elif type(filename) == PdfPages:
        filename.savefig()
    else:
        plt.savefig(filename)


def plot_event_errors(error_hist, filename=None):
    plt.clf()
    fig = plt.figure()
    fig.patch.set_facecolor('white')
    plt.bar(range(0, len(error_hist[:])), error_hist[:], color='r', align='center', label="Error code")
    plt.xlabel('')
    plt.ylabel('#')
    plt.title('Event errors')
    plt.grid(True)
    plt.xticks(range(0, 8), ('SR\noccured', 'No\ntrigger', 'LVL1ID\nnot const.', '#BCID\nwrong', 'unknown\nword', 'BCID\njump', 'trigger\nerror', 'truncated'))
    #plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
    if filename is None:
        plt.show()
    elif type(filename) == PdfPages:
        filename.savefig()
    else:
        plt.savefig(filename)


def plot_trigger_errors(trigger_error_hist, filename=None):
    plt.clf()
    fig = plt.figure()
    fig.patch.set_facecolor('white')
    plt.bar(range(0, 8), trigger_error_hist[:], color='r', align='center', label="Error code")
    plt.xlabel('')
    plt.ylabel('#')
    plt.title('Trigger errors')
    plt.grid(True)
    plt.xticks(range(0, 8), ('increase\nerror', 'more than\none trg.', 'TLU\naccept', 'TLU\ntime out', 'not\nused', 'not\nused', 'not\nused', 'not\nused'))
    #plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
    if filename is None:
        plt.show()
    elif type(filename) == PdfPages:
        filename.savefig()
    else:
        plt.savefig(filename)


def plot_service_records(service_record_hist, filename=None):
    plt.clf()
    fig = plt.figure()
    fig.patch.set_facecolor('white')
    plt.bar(range(0, 32), service_record_hist[:], color='r', align='center', label="Error code")
    plt.xlim((0, 31))
    plt.xlabel('service record code')
    plt.ylabel('#')
    plt.title('Service records (' + str(np.sum(service_record_hist)) + ' entries)')
    plt.grid(True)
    #plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
    if filename is None:
        plt.show()
    elif type(filename) == PdfPages:
        filename.savefig()
    else:
        plt.savefig(filename)


def plot_correlations(filenames, limit=None):
    plt.clf()
    DataFrame = pd.DataFrame()
    index = 0
    for fileName in filenames:
        print 'open ', fileName
        with pd.get_store(fileName, 'r') as store:
            tempDataFrame = pd.DataFrame({'Event': store.Hits.Event[:15000], 'Row' + str(index): store.Hits.Row[:15000]})
            tempDataFrame = tempDataFrame.set_index('Event')
            DataFrame = tempDataFrame.join(DataFrame)
            DataFrame = DataFrame.dropna()
            index += 1
            del tempDataFrame
    DataFrame["index"] = DataFrame.index
    DataFrame.drop_duplicates(take_last=True, inplace=True)
    del DataFrame["index"]
    print DataFrame.head(10)
    correlationNames = ('Row')
    index = 0
    for corName in correlationNames:
        for colName in itertools.permutations(DataFrame.filter(regex=corName), 2):
            if(corName == 'Col'):
                heatmap, xedges, yedges = np.histogram2d(DataFrame[colName[0]], DataFrame[colName[1]], bins=(80, 80), range=[[1, 80], [1, 80]])
            else:
                heatmap, xedges, yedges = np.histogram2d(DataFrame[colName[0]], DataFrame[colName[1]], bins=(336, 336), range=[[1, 336], [1, 336]])
            extent = [yedges[0] - 0.5, yedges[-1] + 0.5, xedges[-1] + 0.5, xedges[0] - 0.5]
#             extent = [xedges[0], xedges[-1], yedges[0], yedges[-1]]
            plt.clf()
            cmap = cm.get_cmap('hot', 40)
            plt.imshow(heatmap, extent=extent, cmap=cmap, interpolation='nearest')
            plt.gca().invert_yaxis()
            plt.xlabel(colName[0])
            plt.ylabel(colName[1])
            plt.title('Correlation plot(' + corName + ')')
            plt.savefig(colName[0] + '_' + colName[1] + '.pdf')
#             print 'store as ', fileNames[int(index/2)]
            index += 1


def plot_scurves(occupancy_hist, scan_parameters, max_occ=None, scan_paramter_name=None, filename=None):
    if max_occ is None:
        max_occ = 2 * np.median(np.amax(occupancy_hist, axis=2))
    if len(occupancy_hist.shape) < 3:
        raise ValueError('Found array with shape %s' % str(occupancy_hist.shape))
    y = occupancy_hist.reshape(-1)
    x = []
    n_pixel = len(y) / len(scan_parameters)
    for _ in range(0, n_pixel):
        x.extend(scan_parameters)
    cmap = cm.get_cmap('jet', 200)
    heatmap, xedges, yedges = np.histogram2d(y, x, range=[[0, max_occ], [scan_parameters[0], scan_parameters[-1]]], bins=(max_occ, len(scan_parameters)))
    plt.clf()
    fig = plt.figure()
    fig.patch.set_facecolor('white')
    extent = [yedges[0] - 0.5, yedges[-1] + 0.5, xedges[-1] + 0.5, xedges[0] - 0.5]
    norm = colors.LogNorm()
    plt.imshow(heatmap, interpolation='nearest', aspect="auto", cmap=cmap, extent=extent, norm=norm)
    plt.gca().invert_yaxis()
    plt.colorbar()
    plt.title('S-Curves for ' + str(n_pixel) + ' pixel(s)')
    if scan_paramter_name is None:
        plt.xlabel('Scan parameter')
    else:
        plt.xlabel(scan_paramter_name)
    plt.ylabel('Occupancy')
    if filename is None:
        plt.show()
    elif type(filename) == PdfPages:
        filename.savefig()
    else:
        plt.savefig(filename)


def plot_cluster_size(cluster_size_hist, filename=None):
    print 'plot_cluster_size'
    plt.clf()
    fig = plt.figure()
    fig.patch.set_facecolor('white')
    plt.bar(range(0, len(cluster_size_hist)), cluster_size_hist[:], color='r', align='center', label="Cluster size")
#     print cluster_size_hist[:].nonzero()
#     plt.xlim((0, 31))
    plt.yscale('log')
    plt.xlabel('cluster size')
    plt.ylabel('#')
    plt.title('Cluster size (' + str(np.sum(cluster_size_hist)) + ' entries)')
    plt.grid(True)
    if filename is None:
        plt.show()
    elif type(filename) == PdfPages:
        filename.savefig()
    else:
        plt.savefig(filename)


def plot_cluster_tot_size(hist, median=False, max_occ=None, filename=None):
    plt.clf()
    H = hist[0:50, 0:20]
    cmap = cm.get_cmap('jet')
    plt.imshow(H, aspect="auto", interpolation='nearest', cmap=cmap)  # , norm=norm)#, extent=extent) # for monitoring
    plt.title('Cluster size and cluster ToT (' + str(np.sum(H) / 2) + ' entries)')
    plt.xlabel('cluster size')
    plt.ylabel('cluster ToT')
    plt.colorbar(cmap=cmap)
    plt.gca().invert_yaxis()
    fig = plt.figure()
    fig.patch.set_facecolor('white')
    if filename is None:
        plt.show()
    elif type(filename) == PdfPages:
        filename.savefig()
    else:
        plt.savefig(filename)


def plot_cluster_tot(hist, median=False, max_occ=None, filename=None):
    plt.clf()
    fig = plt.figure()
    fig.patch.set_facecolor('white')
    plt.bar(range(0, len(hist[:, 0])), hist[:, 0], color='r', align='center', label="Error code")
    plt.xlabel('cluster ToT')
    plt.ylabel('#')
    plt.title('Cluster ToT (' + str(sum(hist[:, 0])) + ' entries)')
    plt.grid(True)
    if filename is None:
        plt.show()
    elif type(filename) == PdfPages:
        filename.savefig()
    else:
        plt.savefig(filename)


# def plot_pixel_mask(mask, maskname, filename=None):
#     plt.clf()
#     extent = [0.5, 80.5, 336.5, 0.5]
#     plt.imshow(mask, interpolation='nearest', aspect="auto", extent=extent) # for monitoring
#     plt.title(maskname+" mask")
#     plt.xlabel('Column')
#     plt.ylabel('Row')
#     plt.colorbar(boundaries = bounds, cmap = cmap, norm = norm)  # FIXME: missing paramters
#     if filename is None:
#         plt.show()
#     elif type(filename) == PdfPages:
#         filename.savefig()
#     else:
#         plt.savefig(filename)
#
#
# def plot_pixel_dac_config(dacconfig, dacname, filename = None):
#     plt.clf()
#     extent = [0.5, 80.5, 336.5, 0.5]
#     cmap = cm.get_cmap('hot')
#     ceil_number = dacconfig.max()  # TODO: get max value from register object
#     bounds = range(0, ceil_number+1, ceil_number/255)
#     norm = colors.BoundaryNorm(bounds, cmap.N)
#     plt.imshow(dacconfig, interpolation='nearest', aspect="auto", cmap = cmap, norm = norm, extent=extent)
#     plt.title(dacname+" distribution")
#     plt.xlabel('Column')
#     plt.ylabel('Row')
#     plt.colorbar(boundaries = bounds, cmap = cmap, norm = norm)
#     if filename is None:
#         plt.show()
#     elif type(filename) == PdfPages:
#         filename.savefig()
#     else:
#         plt.savefig(filename)


def create_2d_pixel_hist(hist2d, title=None, x_axis_title=None, y_axis_title=None, z_max=None):
    H = np.empty(shape=(336, 80), dtype=hist2d.dtype)
    H[:] = hist2d[:, :]
    extent = [0.5, 80.5, 336.5, 0.5]
    cmap = cm.get_cmap('hot', 200)
    #ceil_number = np.max(hist2d) if z_max == None else z_max
    ceil_number = round_to_multiple(H.max() if z_max == None else z_max, 10)
    #ceil_number = np.max(hist2d)
    bounds = range(0, ceil_number + 1, ceil_number / 10 if ceil_number > 0 else 1)
    norm = colors.BoundaryNorm(bounds, cmap.N)
    plt.imshow(H, interpolation='nearest', aspect="auto", cmap=cmap, norm=norm, extent=extent)  # for monitoring
    if title != None:
        plt.title(title)
    if x_axis_title != None:
        plt.xlabel(x_axis_title)
    if y_axis_title != None:
        plt.ylabel(y_axis_title)
    ax = plt.subplot(311)
#     ax = plt.plot()
    divider = make_axes_locatable(ax)
#     ax = plt.plot()
    ax = plt.subplot(311)
    cax = divider.append_axes("right", size="5%", pad=0.05)
    try:
        plt.colorbar(boundaries=bounds, cmap=cmap, norm=norm, ticks=bounds, cax=cax)
    except:
        logging.info('plotting.py create_2d_pixel_hist: error printing color bar')


def create_1d_hist(hist, title=None, x_axis_title=None, y_axis_title=None, bins=None, x_min=None, x_max=None):
    median = np.median(hist)
    mean = np.mean(hist)
    rms = np.std(hist, dtype=np.float64)
    hist_bins = 100 if bins == None else bins
    hist_range = (x_min, x_max) if x_min is not None and x_max is not None else None
    _, _, _ = plt.hist(x=hist.ravel(), bins=hist_bins, range=hist_range)  # rebin to 1 d hist
    # create hist without masked elements, higher precision while calculating gauss
    h_1d, h_bins = np.histogram(np.ma.compressed(hist), bins=hist_bins, range=hist_range)
    if title != None:
        plt.title(title)
    if x_axis_title != None:
        plt.xlabel(x_axis_title)
    if y_axis_title != None:
        plt.ylabel(y_axis_title)
    bin_centres = (h_bins[:-1] + h_bins[1:]) / 2
    amplitude = np.amax(h_1d)
    # defining gauss fit function

    def gauss(x, *p):
        A, mu, sigma = p
        return A * np.exp(-(x - mu) ** 2 / (2.0 * sigma ** 2))

    p0 = np.array([amplitude, mean, rms])  # p0 is the initial guess for the fitting coefficients (A, mu and sigma above)
    ax = plt.subplot(312)
    try:
        coeff, _ = curve_fit(gauss, bin_centres, h_1d, p0=p0)
        hist_fit = gauss(bin_centres, *coeff)
        plt.plot(bin_centres, hist_fit, "r--", label='Gaus fit')
        chi2 = 0
        for i in range(0, len(h_1d)):
            chi2 += (h_1d[i] - gauss(h_bins[i], *coeff)) ** 2
        textright = '$\mu=%.2f$\n$\sigma=%.2f$\n$\chi2=%.2f$' % (coeff[1], coeff[2], chi2)
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        ax.text(0.85, 0.9, textright, transform=ax.transAxes, fontsize=8,
        verticalalignment='top', bbox=props)
    except RuntimeError:
        logging.info('create_1d_hist: Fit failed, do not plot fit')
    plt.ylim([0, plt.ylim()[1] * 1.05])
#     plt.xlim([np.amin(hist_bins) if x_min == None else x_min, np.amax(hist_bins) if x_max == None else x_max])
    textleft = '$\mathrm{mean}=%.2f$\n$\mathrm{RMS}=%.2f$\n$\mathrm{median}=%.2f$' % (mean, rms, median)
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
    ax.text(0.1, 0.9, textleft, transform=ax.transAxes, fontsize=8, verticalalignment='top', bbox=props)


def create_pixel_scatter_plot(hist, title=None, x_axis_title=None, y_axis_title=None, y_min=None, y_max=None):
#     scatter_y = np.empty(shape=(336*80),dtype=hist.dtype)
    scatter_y_mean = np.zeros(shape=(80), dtype=np.float32)
    for col in range(80):
        scatter_y_mean[col] = np.mean(hist[:, col])
    scatter_y = hist.flatten('F')
    plt.scatter(range(80 * 336), scatter_y, marker='o', s=0.8)
    p1, = plt.plot(range(336 / 2, 80 * 336 + 336 / 2, 336), scatter_y_mean, 'o')
    plt.plot(range(336 / 2, 80 * 336 + 336 / 2, 336), scatter_y_mean, linewidth=2.0)
    plt.legend([p1], ["column mean"], prop={'size': 6})
    plt.xlim(0, 26880)
    plt.ylim(1.1 * min(scatter_y) if y_min == None else y_min, 1.1 * max(scatter_y) if y_max == None else y_max)
    if title != None:
        plt.title(title)
    if x_axis_title != None:
        plt.xlabel(x_axis_title)
    if y_axis_title != None:
        plt.ylabel(y_axis_title)


def plotThreeWay(hist, title, filename=None, x_axis_title=None, minimum=None, maximum=None, bins=None):  # the famous 3 way plot (enhanced)
    minimum = 0 if minimum is None else minimum
    maximum = 2 * np.median(hist) if maximum is None else maximum
    x_axis_title = '' if x_axis_title is None else x_axis_title
    fig = plt.figure()
    fig.patch.set_facecolor('white')
    plt.subplot(311)
    create_2d_pixel_hist(hist, title=title, x_axis_title="column", y_axis_title="row", z_max=maximum)
    plt.subplot(312)
    create_1d_hist(hist, bins=bins, x_axis_title=x_axis_title, y_axis_title="#", x_min=minimum, x_max=maximum)
    plt.subplot(313)
    create_pixel_scatter_plot(hist, x_axis_title="channel=row + column*336", y_axis_title=x_axis_title, y_min=minimum, y_max=maximum)
    plt.tight_layout()
    if filename is None:
        plt.show()
    elif type(filename) == PdfPages:
        filename.savefig()
    else:
        plt.savefig(filename)

if __name__ == "__main__":
    filename = "HitMap.txt"
    with open(filename, 'r') as f:
        H = np.empty(shape=(80, 336))
        for line in f.readlines():
            values = re.split("\s", line)
            col = int(values[0])
            row = int(values[1])
            hits = int(values[2])
            #print str(col)
            H[col, row] = hits
    plotThreeWay(H.transpose(), title='Occupancy', x_axis_title='occupancy', filename='SourceScanOccupancy.pdf')

#     with tb.openFile('out.h5', 'r') as in_file:
#         H=np.empty(shape=(336,80),dtype=in_file.root.HistOcc.dtype)
#         H[:]=in_file.root.HistThreshold[:,:]
#         plotThreeWay(hist = in_file.root.HistThreshold[:,:], title = "Threshold", filename = "Threshold.pdf", label = "noise[e]")

# TODO: set color for bad pixels
# set nan to special value
# masked_array = np.ma.array (a, mask=np.isnan(a))
# cmap = matplotlib.cm.jet
# cmap.set_bad('w',1.)
# ax.imshow(masked_array, interpolation='nearest', cmap=cmap)

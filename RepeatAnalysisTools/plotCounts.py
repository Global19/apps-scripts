#! /usr/bin/python

import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import seaborn as sns
import sys
from pbcore.io import FastaReader,FastqReader

YLABEL     = 'CCS Reads'
DEFAULTBIN = 1
DEFAULTBW  = 3

def main(parser):
    args = parser.parse_args()
    
    fx            = args.inFastx if args.inFastx else sys.stdin
    #sortedRecs    = sorted(pysam.FastxFile(fx),key=lambda r:-len(r.sequence))
    try:
        recs = list(FastqReader(fx))
    except ValueError:
        #this will fail if fasta is streamed 
        recs = list(FastaReader(fx))

    counts = [rec.sequence.count(args.motif) for rec in recs]
    xlabel = '%s Repeat Copies (exclusive)' % args.motif
    f,c,b  = countPlot(counts,args.name,xlabel,
                       binsize=args.binsize,bandwidth=args.bandwidth)
    f.savefig('{p}.{n}.{e}'.format(p=args.out,
                                   n='motifCount',
                                   e=args.format),
              format=args.format,
              dpi=args.dpi)
    counts = map(len,recs)
    xlabel = 'Target Insert Length (bp)'
    f,c,b  = countPlot(counts,args.name,xlabel,
                       binsize=args.binsize,bandwidth=args.bandwidth)
    f.savefig('{p}.{n}.{e}'.format(p=args.out,
                                   n='insertSize',
                                   e=args.format),
              format=args.format,
              dpi=args.dpi)
    if args.exportBincounts:
        oname = '{p}.{n}.csv'.format(p=args.out,
                                n='histogramBins')
        with open(oname,'w') as ofile:
            ofile.write('Length,Reads\n')
            for bn,cnt in zip(b,c):
                ofile.write('%i,%i\n' % (bn,cnt))

    print 'Done'
    return f

def countPlot(counts,title,xlabel,binsize=1,bandwidth=1):
    f,ax = plt.subplots()
    ax2 = ax.twinx()
    sns.kdeplot(counts,ax=ax2,color='k',bw=bandwidth,alpha=0.25)
    bincnts,bins,patches = ax.hist(counts,
                                   bins=xrange(min(counts)-1,
                                               max(counts)+1,
                                               binsize),
                                   align='left',
                                   alpha=0.5)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(YLABEL)
    ax.set_title(title)
    ax.spines['right'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax2.spines['top'].set_visible(False)
    ax2.get_yaxis().set_visible(False)
    return f,bincnts,bins

class CountPlot_Exception(Exception):
    pass

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(prog='plotCounts.py', description='generate histograms of motif counts and expansion size')
    parser.add_argument('-i,--inFastx', dest='inFastx', type=str, default=None, 
                    help='Input Fastx file. Default stdin')
    parser.add_argument('-o,--out', dest='out', type=str, default='hist',
                    help='Output prefix. default \'hist\'')
    parser.add_argument('-m,--motif', dest='motif', type=str, default=None, required=True,
                    help='Search motif')
    parser.add_argument('-b,--binsize', dest='binsize', type=int, default=DEFAULTBIN,
                    help='binsize for histogram. default %i' % DEFAULTBIN)
    parser.add_argument('-w,--bandwidth', dest='bandwidth', type=float, default=DEFAULTBW,
                    help='bandwidth for kde plot. default %f' % DEFAULTBW)
    parser.add_argument('-n,--name', dest='name', type=str, default='', required=False,
                    help='Title/name for figure')
    parser.add_argument('-f,--format', dest='format', type=str, default='png',
                    help='Image format.  Default png')
    parser.add_argument('-d,--dpi', dest='dpi', type=int, default=400,
                    help='Image resolution.  Default 400')
    parser.add_argument('-e,--exportBins', dest='exportBincounts', action='store_true', default=False,
                    help='Export CSV of bin counts.  Default False')

    try:
        main(parser)
    except CountPlot_Exception,e:
        print 'ERROR: %s' % e
        sys.exit(1) 


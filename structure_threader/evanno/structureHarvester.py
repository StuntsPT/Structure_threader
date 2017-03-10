#!/usr/bin/env python3
""" structureHarvester
2007-2014
dent earl, dearl (a) soe ucsc edu
2015 Francisco Pina Martins <f.pinamartins@gmail.com>


http://www.structureharvester.com/
https://github.com/dentearl/structureHarvester/
http://taylor0.biology.ucla.edu/structureHarvester/
http://users.soe.ucsc.edu/~dearl/software/structureHarvester/

##############################
CITATION
Earl, Dent A. and vonHoldt, Bridgett M. (2012)
STRUCTURE HARVESTER: a website and program for visualizing
STRUCTURE output and implementing the Evanno method.
Conservation Genetics Resources 4(2) 359-361. DOI: 10.1007/s12686-011-9548-7

##############################
REFERENCES

Evanno et al., 2005.  Detecting the number of clusters of individuals using
  the software STRUCTURE: a simulation study. Molecular Ecology 14, 2611-2620.

Jakobsson M., Rosenberg N. 2007. CLUMPP: a cluster matching and permutation
  program for dealing with label switching and multimodality in analysis
  of population structure. Bioinformatics 23(14): 1801-1806.

Pritchard J., Stephens M., Donnelly. P. 2000. Genetics 155:945-959.


##############################
LICENSE

Copyright (C) 2007-2014 by
Dent Earl (dearl (a) soe ucsc edu, dentearl (a) gmail com)
Copyright (C) 2015 by Francisco Pina Martins <f.pinamartins@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

"""
import glob
import os
import time
try:
    import evanno.harvesterCore as hc
except ImportError:
    import structure_threader.evanno.harvesterCore as hc


__version__ = 'v0.6.94 July 2014'
EPSILON = 0.0000001 # for determining if a stdev ~ 0


class Exception(Exception):
  pass

def unexpectedValue(filename, valuename, value, data):
  raise Exception('Error: %s contains an unexpected value:\n'
                   '    %s = %s\n'
                   'Generally these problems can be resolved by discarding the '
                   'file and re-running STRUCTURE for this value of K.\n'
                   % (filename, valuename, value))


def harvestFiles(data, resultsdir):
  files = glob.glob(os.path.join(resultsdir, '*_f'))
  if len(files) < 1:
    raise Exception('Error, unable to locate any _f files in '
                    'the results directory %s' % resultsdir)
  data.records = {} # key is K, value is an array
  for f in files:
    try:
      run, errorString = hc.readFile(f, data)
    except hc.UnexpectedValue as e:
      unexpectedValue(e.filename, e.valuename, e.value, e.data)
    if run is not None:
      data.records.setdefault(run.k, []).append(run)
    else:
      raise Exception('Error, unable to extract results from file %s.\n%s\n'
                      % (f, errorString))
  data.sortedKs = list(data.records.keys())
  data.sortedKs.sort()


def evannoMethod(data, outdir):
  value = hc.evannoTests(data)
  if value is not None:
    raise Exception('Unable to perform Evanno method for '
                     'the following reason(s):\n' + value)
  hc.calculatePrimesDoublePrimesDeltaK(data)
  writeEvannoTableToFile(data, outdir)


def writeEvannoTableToFile(data, outdir):
  file = open(os.path.join(outdir, 'evanno.txt'), 'w')
  file.write('# This document produced by structureHarvester.py %s core %s\n'
             % (__version__, hc.__version__))
  file.write('# http://www.structureharvester.com/\n')
  file.write('# https://github.com/dentearl/structureHarvester/\n')
  file.write('# http://taylor0.biology.ucla.edu/structureHarvester\n')
  file.write('# http://users.soe.ucsc.edu/~dearl/software/structureHarvester\n')
  file.write('# Written by Dent Earl, dearl (a) soe ucsc edu.\n')
  file.write('# CITATION:\n# Earl, Dent A. and vonHoldt, Bridgett M. (2012)\n'
             '# STRUCTURE HARVESTER: a website and program for visualizing\n'
             '# STRUCTURE output and implementing the Evanno method.\n'
             '# Conservation Genetics Resources 4(2) 359-361. '
             'DOI: 10.1007/s12686-011-9548-7\n'
             '# Stand-alone version: %s\n'
             '# Core version: %s\n'
             % (__version__, hc.__version__))
  file.write('# File generated at %s\n'
             % (time.strftime('%Y-%b-%d %H:%M:%S %Z', time.localtime())))
  file.write('#\n')
  file.write('\n##########\n')
  file.write('# K\tReps\t'
             'Mean LnP(K)\tStdev LnP(K)\t'
             'Ln\'(K)\t|Ln\'\'(K)|\tDelta K\n')
  for i in range(0, len(data.sortedKs)):
    k = data.sortedKs[i]
    if k in data.LnPK:
      LnPKstr = '%f' % data.LnPK[k]
    else:
      LnPKstr = 'NA'
    if k in data.LnPPK:
      LnPPKstr = '%f' % data.LnPPK[k]
    else:
      LnPPKstr = 'NA'
    if k in data.deltaK:
      deltaKstr = '%f' % data.deltaK[k]
    else:
      deltaKstr = 'NA'
    file.write('%d\t'
               '%d\t%.4f\t'
               '%.4f\t%s\t%s\t%s\n'
               % (k,
                  len(data.records[k]), data.estLnProbMeans[k],
                  data.estLnProbStdevs[k], LnPKstr, LnPPKstr, deltaKstr))
  file.close()
  # Retrieve the top 3 k values
  bk = [x[0] for x in sorted(data.deltaK.items(),
                             key=lambda j: j[1],
                             reverse=True)][:3]
  return bk

def failHandler(message):
  raise Exception(message)


def main(resultsdir, outdir):
  data = hc.Data()
  harvestFiles(data, resultsdir)
  hc.calculateMeansAndSds(data)
  evannoMethod(data, outdir)
  bestk = hc.writeRawOutputToFile(os.path.join(outdir, 'summary.txt'), data)

  return bestk

if __name__ == '__main__':
  #Usage: python3 structureHarvester.py resultsdir outdir
  from sys import argv
  main(argv[1], argv[2])

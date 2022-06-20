# A script for reading (nano)DQMIO files from DAS 
# and harvesting a selected monitoring element.
#
# Very similar to harvest_nanodqmio_to_csv.py,
# but store the dataframe as a parquet file instead of a csv file.

### imports
import sys
import os
import json
import numpy as np
sys.path.append('src')
from DQMIOReader import DQMIOReader

if __name__=='__main__':

  # definitions
  filemode = 'das'
  # (choose from 'das' or 'local';
  #  in case of 'das', will read all files belonging to the specified dataset from DAS;
  #  in case of 'local', will read all files in the specified folder on the local filesystem.)
  datasetname = '/MinimumBias/Commissioning2021-900GeVmkFit-v2/DQMIO'
  # (name of the data set on DAS (or filemode 'das') 
  #  OR name of the folder holding input files (for filemode 'local'))
  redirector = 'root://cms-xrd-global.cern.ch/'
  # (redirector used to access remote files (ignored in filemode 'local'))
  mename = 'PixelPhase1/Tracks/PXBarrel/chargeInner_PXLayer_1'
  # (name of the monitoring element to store)
  outputfile = 'test.parquet'
  # (path to output file)
  istest = False 
  # (if set to true, only one file will be read for speed)

  # overwrite the above default arguments with command line args
  # (mainly for use in jobs submission script)
  if len(sys.argv)>1:
    runfilesearch = False
    inputfiles = sys.argv[1].split(',')
    mename = sys.argv[2]
    outputfile = sys.argv[3]
  else: runfilesearch = True

  if runfilesearch:
    # make a list of input files,
    # details depend on the chosen filemode
    if filemode=='das':
      # make and execute the DAS client command
      print('running DAS client to find files in dataset {}...'.format(datasetname))
      dascmd = "dasgoclient -query 'file dataset={}' --limit 0".format(datasetname)
      dasstdout = os.popen(dascmd).read()
      dasfiles = [el.strip(' \t') for el in dasstdout.strip('\n').split('\n')]
      if istest: 
        dasfiles = [dasfiles[0]] 
      print('DAS client ready; found following files ({}):'.format(len(dasfiles)))
      for f in dasfiles: print('  - {}'.format(f))
      redirector = redirector.rstrip('/')+'/'
      inputfiles = [redirector+f for f in dasfiles]
    elif filemode=='local':
      # read all root files in the given directory
      inputfiles = ([os.path.join(datasetname,f) for f in os.listdir(datasetname)
                      if f[-5:]=='.root'])
      if istest: inputfiles = [inputfiles[0]]

  # print configuration parameters
  print('running with following parameters:')
  print('input files:')
  for inputfile in inputfiles: print('  - {}'.format(inputfile))
  print('monitoring element: {}'.format(mename))
  print('outputfile: {}'.format(outputfile))

  # make a DQMIOReader instance and initialize it with the DAS files
  print('initializing DQMIOReader...')
  sys.stdout.flush()
  sys.stderr.flush()
  reader = DQMIOReader(*inputfiles)
  reader.sortIndex()
  print('initialized DQMIOReader with following properties')
  print('number of lumisections: {}'.format(len(reader.listLumis())))
  print('number of monitoring elements per lumisection: {}'.format(len(reader.listMEs())))

  # select the monitoring element and make a pandas dataframe
  df = reader.getSingleMEsToDataFrame(mename)
  
  # write to a csv file
  df.to_parquet(outputfile)

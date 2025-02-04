#!/usr/bin/env python

# **Plot the available monitoring elements in a file**  
# 
# Run with `python plot_mes.py -h` for a list of available options.
# Note: only very rough plotting for quick checks.

### imports
import sys
import os
import numpy as np
import json
import argparse
from fnmatch import fnmatch
import matplotlib.pyplot as plt
sys.path.append('../src')
from DQMIOReader import DQMIOReader
import tools
import metools
sys.path.append('../../utils')
import plot_utils as pu

def makeplot( me ):
  ### make a plot of a monitoring element
  # input arguments:
  # - me: instance of MonitorElement
  if me.type in [3,4,5]: return make1dplot(me)
  elif me.type in [6,7,8]: return make2dplot(me)
  elif me.type in [9]: return make3dplot(me)
  elif me.type in [10]: return makeprofileplot(me)
  elif me.type in [0,1,2]: return make0dplot(me)
  else:
    msg = 'WARNING in makeplot: me.type {} not recognized'.format(me.type)
    msg += ' for me.name {}, skipping this plot.'.format(me.name)
    print(msg)
    return (None,None)

def maketitle( me ):
  ### get a suitable title
  title = pu.make_text_latex_safe(me.name)
  title += '\nRun: {} / LS: {}'.format(me.run, me.lumi)
  return title

def make1dplot( me ):
  ### make a plot of a 1D monitoring element
  # input arguments:
  # - me: instance of MonitorElement with type TH1F, TH1S or TH1D
  hist = metools.me_to_nparray( me, integer_values=True )
  fig,ax = pu.plot_hists([hist], title=maketitle(me))
  return (fig,ax)

def make2dplot( me ):
  ### make a plot of a 2D monitoring element
  # input arguments:
  # - me: instance of MonitorElement with type TH2F, TH2S or TH2D
  hist = metools.me_to_nparray( me, integer_values=True )
  fig,ax = pu.plot_hist_2d(hist, title=maketitle(me))
  return (fig,ax)

def make3dplot( me ):
  raise Exception('3D plotting not yet implemented.')

def makeprofileplot( me ):
  ### make a plot of a Profile monitoring element
  # input arguments:
  # - me: instance of MonitorElement with type TProfile
  hinfo = metools.me_to_nparray( me, integer_values=False )
  values = hinfo['values']
  errors = hinfo['errors']
  xax = hinfo['xax']
  xlims = (xax[0], xax[-1])
  # todo: implement better plotting (as scatter plot with errors)
  fig,ax = pu.plot_hists([values], xlims=xlims, title=maketitle(me))
  return (fig,ax)

def make0dplot( me ):
  ### make a plot of a 0D monitoring element (i.e. print a value)
  fig,ax = plt.subplots()
  text = str(me.data)
  pu.add_text(ax, text, (0.5, 0.5), 
              fontsize=15,
              horizontalalignment='center',
              verticalalignment='center')
  ax.set_title( maketitle(me) )
  return (fig,ax)
  
if __name__=='__main__':

  # read arguments
  parser = argparse.ArgumentParser(description='Plot available monitoring elements')
  parser.add_argument('--filemode', choices=['das','local'], default='das',
                        help='Choose from "das" or "local"')
  parser.add_argument('--filename', required=True,
                        help='Full name of the file on DAS (for filemode "das")'
                             +' OR path to the local file (for filemode "local")')
  parser.add_argument('--run', default=None,
                        help='Run number for which to make the plot (default: first in file).'
                            +' Use "all" to make a plot for all available runs in the file.')
  parser.add_argument('--ls', default=None,
                        help='Lumisection number for which to make the plot (default: first in file).'
                            +' Use "all" to make a plot for all available lumisections in the file.')
  parser.add_argument('--redirector', default='root://cms-xrd-global.cern.ch/',
                        help='Redirector used to access remote files'
                             +' (ignored in filemode "local").')
  parser.add_argument('--proxy', default=None,
                        help='Set the location of a valid proxy created with'
                             +' "--voms-proxy-init --voms cms";'
                             +' needed for DAS client;'
                             +' ignored if filemode is "local".')
  parser.add_argument('--searchkey', default=None,
                       help='Provide a search key to filter the results;'
                            +' only results matching the searchkey will be plotted;'
                            +' may contain unix-style wildcards.')
  parser.add_argument('--outputdir', default=None,
                       help='Directory where to store the figures'
                            +' (default: show each figure but do not save)')
  args = parser.parse_args()
  filemode = args.filemode
  filename = args.filename
  run = args.run
  ls = args.ls
  redirector = args.redirector
  searchkey = args.searchkey
  proxy = None if args.proxy is None else os.path.abspath(args.proxy)
  outputdir = None if args.outputdir is None else os.path.abspath(args.outputdir)

  # print arguments
  print('Running with following configuration:')
  for arg in vars(args):
    print('  - {}: {}'.format(arg,getattr(args,arg)))

  # export the proxy
  if( filemode=='das' and proxy is not None ): tools.export_proxy( proxy )

  # format input file
  if filemode=='das':
    redirector = redirector.rstrip('/')+'/'
    filename = redirector+filename

  # make output dir
  if( outputdir is not None and not os.path.exists(outputdir) ): 
    os.makedirs(outputdir)
  
  # make a DQMIOReader instance and initialize it with the file
  print('initializing DQMIOReader...')
  sys.stdout.flush()
  sys.stderr.flush()
  reader = DQMIOReader(*[filename])

  # filter histogram names
  print('filtering ME names...')
  menames = reader.listMEs()
  if searchkey is not None:
    res = []
    for mename in menames:
      if fnmatch(mename,searchkey): res.append(mename)
    menames = res
  nmes = len(menames)
  print('number of selected ME names: {}'.format(nmes))
  if nmes==0: raise Exception('ERROR: list of ME names to plot is empty.')

  # filter run and lumisection number
  print('filtering lumisections...')
  runsls = sorted(reader.listLumis()[:])
  if run is None:
    runsls = [el for el in runsls if el[0]==runsls[0][0]]
  elif run=='all': pass
  else:
    try:
      run = int(run)
      runsls = [el for el in runsls if el[0]==run]
    except:
      raise Exception('ERROR: unrecognized value for --run: {}'.format(run))
  if ls is None:
    runsls = [runsls[0]]
  elif ls=='all': pass
  else:
    try:
      ls = int(ls)
      runsls = [el for el in runsls if el[1]==ls]
    except:
      raise Exception('ERROR: unrecognized value for --ls: {}'.format(ls))
  nlumis = len(runsls)
  print('number of selected lumisections: {}'.format(nlumis))
  if nlumis==0: raise Exception('ERROR: list of lumisections to plot is empty.')

  # check number of selected histograms
  nplots = nmes*nlumis
  print('{} plots will be made; continue with plotting? (y/n)'.format(nplots))
  go = raw_input()
  if go!='y': sys.exit()

  # make plots
  counter = -1
  for mename in menames:
    for runls in runsls:
      counter += 1
      me = reader.getSingleMEForLumi(runls, mename)
      fig,ax = makeplot(me)
      if fig is None: continue
      if outputdir is None:
        block=False
        if counter==nplots-1: block=True 
        plt.show(block=block)
      else:
        figname = mename.replace('/','_').replace(' ','_')+'.png'
        fig.savefig(os.path.join(outputdir,figname))

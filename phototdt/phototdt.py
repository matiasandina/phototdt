"""Main module."""
import tdt
import numpy as np
import pandas as pd
import datetime
import scipy.signal
from scipy.sparse import csc_matrix, eye, diags
from scipy.sparse.linalg import spsolve

def get_tdt_data(folder, decimate=True, decimate_factor = 10, remove_start=False, verbose=False):
  '''
  get_tdt_data is a function to retrieve the data streams as saved by TDT system
  it uses tdt package and will retrieve the complete duration
  returns a data frame with UTC timestamp, time in seconds, and signal values for each channel
  '''
  if verbose:
    print(f"Reading data from {folder}")
  data = tdt.read_block(folder)
  total_samples = len(data.streams._405A.data)
  fs = data.streams._405A.fs
  # inverse sampling frequency in Hz
  total_seconds = len(data.streams._405A.data)/fs
  start_date = data.info.start_date
  end_date = data.info.stop_date
  sampling_interval = 1 / fs
  
  _405A_data = data.streams._405A.data
  _465A_data = data.streams._465A.data
  
  if decimate:
    sampling_interval = sampling_interval * decimate_factor
    total_samples = np.ceil(total_samples / decimate_factor)
    # Decimate
    _405A_data = scipy.signal.decimate(_405A_data, decimate_factor, ftype="fir")
    _465A_data = scipy.signal.decimate(_465A_data, decimate_factor, ftype="fir")
  # UTC datetime
  # TODO: this doesn't create a real timestamp
  # we should work with block['info']['start_date']
  # we could re-construct a real timestamp by using the sampling frequency block['streams']['_465A'] 
  # we can also argue that datetime is not relevant to keep if anyway has to be reconstructed...
  datetime = pd.date_range(start_date, end_date, periods=total_samples)
  # time_delta = datetime - start_date
  # time_delta = time_delta / np.timedelta64(1, 's')
  # using np works for a seconds range
  time_np = np.arange(0, total_seconds, sampling_interval)

  df = pd.DataFrame({
    "utc_datetime" : datetime,
    "time_seconds" : time_np,
    "_405" : _405A_data,
    "_465" : _465A_data
  })
  
  # TODO: improve the check for third channel
  
  if remove_start:
    # this will have the times when each laser was turned on
    laser_on_times = data.scalars.Fi1i.ts
    # remove from the max moment when leds are on plus 5 seconds
    remove_before = np.ceil(max(laser_on_times) * fs) + 5 * fs
    # we only care about the max here 
    # because we end up removing everything before this
    df = df.iloc[:remove_before]
  
  return df


def get_cam_timestamps(folder, cam_name="Cam1", verbose=False):
  '''
  get_cam_timestamps is a function to retrieve timestamps from a camera 
  using the data streams as saved by TDT system.
  it uses tdt package and will retrieve the complete duration
  cam_name: string with the camera name as saved configured in Synapse software
  returns the timestamp onset
  '''
  if verbose:
    print(f"Reading data from {folder}")
  data = tdt.read_block(folder)
  return data.epocs[cam_name].onset

def calculate_zdFF(photo_data, smooth_win=None, n_remove=5000):
  photo_subset = photo_data.loc[n_remove:].copy()
  if smooth_win is None:
      # try to estimate the sampling rate and smooth one second
      # one second might be too much smoothing!
      smooth_win = int(1 / photo_subset["time_seconds"].diff().values[-1])
  # we might need to fix the issues here with size errors
  photo_subset["zdFF"] = get_zdFF(
    photo_subset._405, 
    photo_subset._465, 
    smooth_win=smooth_win, 
    # do not remove, since we remove a large chunk at the start
    remove=0)
  
  final_data =  pd.merge(photo_data, photo_subset["zdFF"], 
                         how="left", 
                         left_index=True, right_index=True)
  # make them zero
  final_data["zdFF"].fillna(0, inplace=True)
  return final_data

'''
get_zdFF.py calculates standardized dF/F signal based on calcium-idependent 
and calcium-dependent signals commonly recorded using fiber photometry calcium imaging

Ocober 2019 Ekaterina Martianova ekaterina.martianova.1@ulaval.ca 

Reference:
  (1) Martianova, E., Aronson, S., Proulx, C.D. Multi-Fiber Photometry 
      to Record Neural Activity in Freely Moving Animal. J. Vis. Exp. 
      (152), e60278, doi:10.3791/60278 (2019)
      https://www.jove.com/video/60278/multi-fiber-photometry-to-record-neural-activity-freely-moving

'''

def get_zdFF(reference,signal,smooth_win=10,remove=200,lambd=5e4,porder=1,itermax=50): 
  '''
  Calculates z-score dF/F signal based on fiber photometry calcium-idependent 
  and calcium-dependent signals
  
  Input
      reference: calcium-independent signal (usually 405-420 nm excitation), 1D array
      signal: calcium-dependent signal (usually 465-490 nm excitation for 
                   green fluorescent proteins, or ~560 nm for red), 1D array
      smooth_win: window for moving average smooth, integer
      remove: the beginning of the traces with a big slope one would like to remove, integer
      Inputs for airPLS:
      lambd: parameter that can be adjusted by user. The larger lambda is,  
              the smoother the resulting background, z
      porder: adaptive iteratively reweighted penalized least squares for baseline fitting
      itermax: maximum iteration times
  Output
      zdFF - z-score dF/F, 1D numpy array
  '''
  
  import numpy as np
  from sklearn.linear_model import Lasso

 # Smooth signal
  reference = smooth_signal(reference, smooth_win)
  signal = smooth_signal(signal, smooth_win)
  
 # Remove slope using airPLS algorithm
  r_base=airPLS(reference,lambda_=lambd,porder=porder,itermax=itermax)
  s_base=airPLS(signal,lambda_=lambd,porder=porder,itermax=itermax) 

 # Remove baseline and the begining of recording
  reference = (reference[remove:] - r_base[remove:])
  signal = (signal[remove:] - s_base[remove:])   

 # Standardize signals    
  reference = (reference - np.median(reference)) / np.std(reference)
  signal = (signal - np.median(signal)) / np.std(signal)
  
 # Align reference signal to calcium signal using non-negative robust linear regression
  lin = Lasso(alpha=0.0001,precompute=True,max_iter=1000,
              positive=True, random_state=9999, selection='random')
  n = len(reference)
  lin.fit(reference.reshape(n,1), signal.reshape(n,1))
  reference = lin.predict(reference.reshape(n,1)).reshape(n,)

 # z dFF    
  zdFF = (signal - reference)
 
  return zdFF


def smooth_signal(x,window_len=10,window='flat'):

    """smooth the data using a window with requested size.
    
    This method is based on the convolution of a scaled window with the signal.
    The signal is prepared by introducing reflected copies of the signal 
    (with the window size) in both ends so that transient parts are minimized
    in the begining and end part of the output signal.
    The code taken from: https://scipy-cookbook.readthedocs.io/items/SignalSmooth.html
    
    input:
        x: the input signal 
        window_len: the dimension of the smoothing window; should be an odd integer
        window: the type of window from 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'
                'flat' window will produce a moving average smoothing.

    output:
        the smoothed signal        
    """
    
    import numpy as np

    if x.ndim != 1:
        raise(ValueError, "smooth only accepts 1 dimension arrays.")

    if x.size < window_len:
        raise(ValueError, "Input vector needs to be bigger than window size.")

    if window_len<3:
        return x

    if not window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
        raise(ValueError, "Window is one of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'")

    s=np.r_[x[window_len-1:0:-1],x,x[-2:-window_len-1:-1]]

    if window == 'flat': # Moving average
        w=np.ones(window_len,'d')
    else:
        w=eval('np.'+window+'(window_len)')

    y=np.convolve(w/w.sum(),s,mode='valid')

    return y[(int(window_len/2)-1):-int(window_len/2)]


'''
airPLS.py Copyright 2014 Renato Lombardo - renato.lombardo@unipa.it
Baseline correction using adaptive iteratively reweighted penalized least squares

This program is a translation in python of the R source code of airPLS version 2.0
by Yizeng Liang and Zhang Zhimin - https://code.google.com/p/airpls

Reference:
Z.-M. Zhang, S. Chen, and Y.-Z. Liang, Baseline correction using adaptive iteratively 
reweighted penalized least squares. Analyst 135 (5), 1138-1146 (2010).

Description from the original documentation:
Baseline drift always blurs or even swamps signals and deteriorates analytical 
results, particularly in multivariate analysis.  It is necessary to correct baseline 
drift to perform further data analysis. Simple or modified polynomial fitting has 
been found to be effective in some extent. However, this method requires user 
intervention and prone to variability especially in low signal-to-noise ratio 
environments. The proposed adaptive iteratively reweighted Penalized Least Squares
(airPLS) algorithm doesn't require any user intervention and prior information, 
such as detected peaks. It iteratively changes weights of sum squares errors (SSE) 
between the fitted baseline and original signals, and the weights of SSE are obtained 
adaptively using between previously fitted baseline and original signals. This 
baseline estimator is general, fast and flexible in fitting baseline.


LICENCE
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>
'''

def WhittakerSmooth(x,w,lambda_,differences=1):
    '''
    Penalized least squares algorithm for background fitting
    
    input
        x: input data (i.e. chromatogram of spectrum)
        w: binary masks (value of the mask is zero if a point belongs to peaks and one otherwise)
        lambda_: parameter that can be adjusted by user. The larger lambda is, 
                 the smoother the resulting background
        differences: integer indicating the order of the difference of penalties
    
    output
        the fitted background vector
    '''
    X=np.matrix(x)
    m=X.size
    i=np.arange(0,m)
    E=eye(m,format='csc')
    D=E[1:]-E[:-1] # numpy.diff() does not work with sparse matrix. This is a workaround.
    W=diags(w,0,shape=(m,m))
    A=csc_matrix(W+(lambda_*D.T*D))
    B=csc_matrix(W*X.T)
    background=spsolve(A,B)
    return np.array(background)

def airPLS(x, lambda_=100, porder=1, itermax=15):
    '''
    Adaptive iteratively reweighted penalized least squares for baseline fitting
    
    input
        x: input data (i.e. chromatogram of spectrum)
        lambda_: parameter that can be adjusted by user. The larger lambda is,
                 the smoother the resulting background, z
        porder: adaptive iteratively reweighted penalized least squares for baseline fitting
    
    output
        the fitted background vector
    '''
    m=x.shape[0]
    w=np.ones(m)
    for i in range(1,itermax+1):
        z=WhittakerSmooth(x,w,lambda_, porder)
        d=x-z
        dssn=np.abs(d[d<0].sum())
        if(dssn<0.001*(abs(x)).sum() or i==itermax):
            if(i==itermax): print('WARING max iteration reached!')
            break
        w[d>=0]=0 # d>0 means that this point is part of a peak, so its weight is set to 0 in order to ignore it
        w[d<0]=np.exp(i*np.abs(d[d<0])/dssn)
        w[0]=np.exp(i*(d[d<0]).max()/dssn) 
        w[-1]=w[0]
    return z


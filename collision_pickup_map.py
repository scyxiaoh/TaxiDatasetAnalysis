# data analysis and wrangling
import pandas as pd
import numpy as np
import random as rnd
import datetime as dt
import time
# visualization
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.image as mpimg

def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days*24)):
        yield start_date + dt.timedelta(minutes = n*60)

def _blit_draw(self, artists, bg_cache):
    # Handles blitted drawing, which renders only the artists given instead
    # of the entire figure.
    updated_ax = []
    for a in artists:
        # If we haven't cached the background for this axes object, do
        # so now. This might not always be reliable, but it's an attempt
        # to automate the process.
        if a.axes not in bg_cache:
           bg_cache[a.axes] = a.figure.canvas.copy_from_bbox(a.axes.figure.bbox)
        a.axes.draw_artist(a)
        updated_ax.append(a.axes)
    
    # After rendering all the needed artists, blit each axes individually.
    for ax in set(updated_ax):
            ax.figure.canvas.blit(ax.figure.bbox)

#load csv

taxi_df = pd.read_csv('yellow_tripdata_2016-05.csv')
coll_df = pd.read_csv('NYC-vehicle-collisions.csv')

#taxi data elimination and sorting
df = taxi_df.set_index("tpep_pickup_datetime")
df = df[['pickup_longitude','pickup_latitude']]
df = df[((df['pickup_longitude'] < -73.7) & (df['pickup_longitude'] > -74.26)) & ((df['pickup_latitude'] > 40.49) & (df['pickup_latitude'] < 40.92))]
df = df.sort_index(ascending=True)

#collisions data elimination and sorting
coll_data = coll_df[['LATITUDE','LONGITUDE','DATE','TIME']]
coll_data = coll_data[((coll_data['LONGITUDE'] < -73.7) & (coll_data['LONGITUDE'] > -74.26)) & ((coll_data['LATITUDE'] > 40.49) & (coll_data['LATITUDE'] < 40.92))]

matrix = []
for single_time in daterange(pd.to_datetime(df.index.min()),pd.to_datetime(df.index.max())):
    selected = df.truncate(before = single_time.strftime("%Y-%m-%d %X"), after = (single_time + dt.timedelta(seconds = 3599)).strftime("%Y-%m-%d %X"))
    matrix += [selected]

# first set up the figure, the axis, and the plot element we want to animate
img = mpimg.imread("nyc.png")
matplotlib.animation.Animation._blit_draw = _blit_draw
fig = plt.figure(figsize = (10,10))
ax = plt.axes(xlim=(-74.15, -73.7004),ylim=(40.5774, 40.9176))
im = plt.imshow(img, extent = [-74.15,-73.7004,40.5774,40.9176])
line, = ax.plot([],[],'bo',markersize = 0.5)
coll_line, = ax.plot([],[],'ro',markersize = 4)
ttl = ax.set_title('',animated = True, fontsize = 20)

# initialization function: plot the background of each frame
def init():
    ttl.set_text('')
    im.set_extent([0.0,0.0,0.0,0.0])
    line.set_data([], [])
    coll_line.set_data([], [])
    return im, line, coll_line, ttl,

def data_stream_coll(s):
    datetime = pd.to_datetime(s)
    date = datetime.strftime("%m/%d/%Y")
    time  = datetime.strftime("%-H:%M")
    time_end  = (datetime+dt.timedelta(minutes=59)).strftime("%-H:%M")
    temp = coll_data[(coll_data['DATE'] == date)&(coll_data['TIME'] >= time)&(coll_data['TIME'] <= time_end)]
    return temp

# animation function.  this is called sequentially
def animate(i):
    im.set_extent([-74.15,-73.7004,40.5774,40.9176])
    #plot collisions
    data_coll = data_stream_coll(matrix[i].index.min())
    coll_line.set_data(data_coll["LONGITUDE"],data_coll["LATITUDE"])

    #plot taxis
    ttl.set_text(pd.to_datetime(matrix[i].index.min()).strftime("%a") + " "+ matrix[i].index.min())
    x = matrix[i]["pickup_longitude"]
    y = matrix[i]["pickup_latitude"]
    line.set_data(x, y)
    
    return im, line, coll_line, ttl,
	
# call the animator.  blit=true means only re-draw the parts that have changed.
anim = animation.FuncAnimation(fig, animate, init_func=init,
frames = len(matrix), interval=750, blit=True)
plt.show()

anim.save('collision_taxi_may_2016.mp4', fps=2)

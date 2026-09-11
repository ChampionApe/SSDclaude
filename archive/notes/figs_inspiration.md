### Function that plots things as function of epsilon and theta:
```python
fig, axes = plt.subplots(2,2, figsize = (14,8));
# PEE RATES
ax = plt.subplot(2,2,1); 
seaborn.lineplot(data = dfτ, linewidth = .25, dashes=False, palette = palette, ax = ax, alpha = .75, legend = False);
for i in range(dfτ.shape[1]-1):
    ax.fill_between(dfτ.index, dfτ.iloc[:,i], dfτ.iloc[:,i+1], alpha = mapAlpha, color = ax.get_lines()[i].get_color())
dfAx(ax, .25, ylabel = 'Tax rate', xlabel = '$\\epsilon$');

pltKwargs = {'ms': 10, 'fontsize': 18, 'arrWidth': 1.5, 'arrHeadWidth': 7, 'arrHeadLen': 7}
# Add baseline marker:
addMarker(ax, dfτ, epsBase, θBase, -0.11, -0.05, 0, -.0325, offsetArrowHead_x = 0, name = 'Pre reform', **pltKwargs)
# Add post-reform marker:
addMarker(ax, dfτ, epsUniversal, θBase, -0.25, -0.05, -.075, -.0325, offsetArrowHead_x = -0.02, name = 'Post reform',**pltKwargs)


# Savings rates:
ax = plt.subplot(2,2,2); 
seaborn.lineplot(data = dfs, linewidth = .25, dashes=False, palette = palette, ax = ax, alpha = .75, legend = False);
for i in range(dfτ.shape[1]-1):
    ax.fill_between(dfs.index, dfs.iloc[:,i], dfs.iloc[:,i+1], alpha = mapAlpha, color = ax.get_lines()[i].get_color())
dfAx(ax, .21, .15, ylabel = 'Savings rate', xlabel = '$\\epsilon$');

# Add baseline marker:
addMarker(ax, dfs, epsBase, θBase, -0.11, 0.01, 0, .009, offsetArrowHead_x = 0, name = 'Pre reform',**pltKwargs)
# Add post-reform marker:
addMarker(ax, dfs, epsUniversal, θBase, -0.25, 0.0085, -.075, .007, offsetArrowHead_x = -0.015, name = 'Post reform',**pltKwargs)

# # Labor supply
ax = plt.subplot(2,2,3); 
seaborn.lineplot(data = dfh, linewidth = .25, dashes=False, palette = palette, ax = ax, alpha = .75, legend = False);
for i in range(dfτ.shape[1]-1):
    ax.fill_between(dfh.index, dfh.iloc[:,i], dfh.iloc[:,i+1], alpha = mapAlpha, color = ax.get_lines()[i].get_color())
dfAx(ax, 43.5, 40.5, ylabel = 'Avg. workweek', xlabel = '$\\epsilon$');

# Add baseline marker:
addMarker(ax, dfh, epsBase, θBase, -0.11, 0.55, 0, 0.45,  offsetArrowHead_x = 0, name = 'Pre reform',**pltKwargs)
# Add post-reform marker:
addMarker(ax, dfh, epsUniversal, θBase, -0.25, 0.5, -.075, .4,  offsetArrowHead_x = -0.015, name = 'Post reform',**pltKwargs)

# Informal savings
ax = plt.subplot(2,2,4);
seaborn.lineplot(data = dfs0, linewidth = .25, dashes=False, palette = palette, ax = ax, alpha = .75, legend = False);
for i in range(dfs0.shape[1]-1):
    ax.fill_between(dfs0.index, dfs0.iloc[:,i], dfs0.iloc[:,i+1], alpha = mapAlpha, color = ax.get_lines()[i].get_color())
dfAx(ax, .5, 0.25, ylabel = 'Informal-to-formal savings', xlabel = '$\\epsilon$');

# Add baseline marker:
addMarker(ax, dfs0, epsBase, θBase, -0.11, -0.055, 0, -0.0375, offsetArrowHead_x = 0, name = 'Pre reform',**pltKwargs)
# Add post-reform marker:
addMarker(ax, dfs0, epsUniversal, θBase, -0.25, -0.04, -.075, -0.02, offsetArrowHead_x = -0.01, name = 'Post reform',**pltKwargs)

fig.subplots_adjust(wspace=0.25, hspace=0.25)  # Adjust spacing
sm = plt.cm.ScalarMappable(cmap = colormap, norm = plt.Normalize(min(dfτ.columns), max(dfτ.columns)))
cb_ax = fig.add_axes([0.25, 0.89, 0.5, 0.03])
cbar = fig.colorbar(sm, cax=cb_ax, location = 'top', shrink = .75);
cbar.set_label('$\\theta$');
```

### Helper functions:


```python
def add_alpha_to_colormap(cmap, alpha=0.5):
    colors = cmap(np.arange(cmap.N))    
    # Add alpha to the RGB array
    RGBA = np.hstack([colors[:, :3], np.full((cmap.N, 1), alpha)])
    # Create new colormap
    new_cmap = mcolors.ListedColormap(RGBA)
    return new_cmap
```

```python
def addMarker(ax, df, eps, theta, offsetText_x, offsetText_y, offsetArrow_x, offsetArrow_y = 0, offsetArrowHead_x = 0,
              ms = 10, name = 'Baseline', fontsize = None, arrWidth = 1.5, arrHeadWidth = 7.5, arrHeadLen = 7.5):
    val = df.loc[eps, theta]
    ax.plot(eps, val, 'o', color = 'k', ms = ms)
    plt.text(eps+offsetText_x, val+offsetText_y, name, fontsize = fontsize)
    plt.annotate("", xy = (eps+offsetArrowHead_x, val+offsetText_y/5), xytext = (eps+offsetArrow_x, val+offsetArrow_y), arrowprops = dict(width = arrWidth, color ='k', headwidth = arrHeadWidth, headlength = arrHeadLen));
```


```python
def dfAx(ax, max_ = 1, min_ = 0, ylabel = None, xlabel = None):
    limx, limy = ax.get_xlim(), ax.get_ylim();
    ax.hlines(0,limx[0],limx[1],colors='k',linewidth=1, alpha = .5)
    ax.set_xlim(limx);
    if ylabel:
        ax.set_ylabel(ylabel);
    if xlabel:
        ax.set_xlabel(xlabel);
    ax.set_ylim([min(limy[0], min_-.001), max(max_, limy[1])]);
    return ax
```
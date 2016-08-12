from scipy.ndimage.measurements import label


def floodfill_scipy(data, start_coords, threshold):

    # Determine value at the starting coordinates
    value = data[start_coords]

    # Determine all pixels that match
    mask = (data > value / threshold) & (data < value * threshold)

    # Determine all individual chunks
    labels, num_features = label(mask)

    mask = labels == labels[start_coords]

    return mask

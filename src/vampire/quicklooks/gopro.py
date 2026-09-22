from PIL import Image
import matplotlib as mpl
import matplotlib.pyplot as plt

from vampire.io.readers.gopro import get_gopro_rescaled_file_data_campaigns


def gopro_image(date, campaign_name="PS144"):
    
    gopro_file = get_gopro_rescaled_file_data_campaigns(date, 
                                                        campaign_name=campaign_name)
    img = Image.open(gopro_file)
    f1 = plt.figure(figsize=(8,6))
    a1 = plt.axes()
    a1.imshow(img)
    plt.show()
    plt.close()
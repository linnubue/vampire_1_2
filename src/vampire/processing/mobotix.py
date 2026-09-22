"""
Moves empty or incomplete images from Mobotix data directory to another
folder. The images are either "no image" or "ir only". This is done by checking 
the image dimension:

240 x 180: no image
320 x 240: no image
640 x 480: only IR image
1280 x 480: IR+VIS image

The images are moved to "no_image" and "ir_only" folders.
"""

import os
import shutil

import numpy as np
import tqdm
from PIL import Image

from vampire.io.readers.mobotix import get_mobotix_files


def main():
    """
    Move empty or incomplete Mobotix images to another directory.
    """

    image_sizes = []
    files = get_mobotix_files()
    for file in tqdm.tqdm(files):
        size = get_image_size(file)
        image_sizes.append(size)

    image_sizes = np.array(image_sizes)

    is_no_image = np.isin(image_sizes[:, 0], [240, 320]) & np.isin(
        image_sizes[:, 1], [180, 240]
    )
    is_ir_only = (image_sizes[:, 0] == 640) & (image_sizes[:, 1] == 480)
    is_vis_ir = (image_sizes[:, 0] == 1280) & (image_sizes[:, 1] == 480)

    assert np.sum(is_no_image | is_ir_only | is_vis_ir) == len(image_sizes)

    print(f"Fraction of good images: {is_vis_ir.sum()/len(image_sizes)}")

    # move no image images to another directory
    for i, file in enumerate(files):
        if is_no_image[i]:

            src_file = file
            dst_file = os.path.join(
                os.environ["VAMPIRE_DATA"],
                "mobotix/no_image",
                os.path.basename(file),
            )

            print(f"Moving {src_file} to {dst_file}")

            shutil.move(src_file, dst_file)

    # move ir only images to another directory
    for i, file in enumerate(files):
        if is_ir_only[i]:

            src_file = file
            dst_file = os.path.join(
                os.environ["VAMPIRE_DATA"],
                "mobotix/ir_only",
                os.path.basename(file),
            )

            print(f"Moving {src_file} to {dst_file}")

            shutil.move(src_file, dst_file)


def get_image_size(file):
    with Image.open(file) as img:
        return img.size


if __name__ == "__main__":
    main()

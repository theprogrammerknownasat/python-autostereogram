import numpy, argparse
from PIL import Image


def gen_pattern(width, height):
    width, height = int(width), int(height)
    return numpy.random.randint(0, 256, (width, height))


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Autostereogram (MagicEye) generator")
    parser.add_argument("depthmap", type=str,
                        help="Path to grayscale depth-map (white = close)")

    parser.add_argument("-o", "--output", type=str, default="output.png",
                        help="Path to write output image")

    parser.add_argument("-p", "--pattern-div", type=int, default=8,
                        help="Width of generated pattern (width n means 1/n of depth-map width)")

    parser.add_argument("-i", "--invert", action="store_true", help="Invert depthmap (white = far)")

    args = parser.parse_args()
    invert = -1 if args.invert else 1

    depth_map = Image.open(args.depthmap).convert("RGB")
    if args.invert:
        depth_map = Image.eval(depth_map, lambda x: 255 - x)
    depth_data = depth_map.load()

    out_img = Image.new("L", depth_map.size)
    out_data = out_img.load()

    pattern_width = depth_map.size[0] / args.pattern_div
    pattern = gen_pattern(pattern_width, depth_map.size[1])

    # Create stereogram
    for x in range(0, depth_map.size[0]):
        for y in range(0, depth_map.size[1]):

            if x < pattern_width:
                out_data[x, y] = int(pattern[x, y])  # Use generated pattern
            else:
                shift = int(depth_data[x, y][0] / args.pattern_div)  # 255 is closest
                out_data[x, y] = out_data[x - pattern_width + shift, y]

    out_img.save(args.output)

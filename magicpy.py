import numpy
import argparse
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
                        help="Base pattern width divisor")
    parser.add_argument("-d", "--depth-factor", type=float, default=0.3,
                        help="Depth effect strength (0.0-1.0)")
    parser.add_argument("-i", "--invert", action="store_true", 
                        help="Invert depthmap (white = far)")

    args = parser.parse_args()

    depth_map = Image.open(args.depthmap).convert("L")  # Grayscale
    if args.invert:
        depth_map = Image.eval(depth_map, lambda x: 255 - x)
    depth_data = depth_map.load()

    width, height = depth_map.size
    out_img = Image.new("L", (width, height))
    out_data = out_img.load()

    pattern_width = width // args.pattern_div
    pattern = gen_pattern(pattern_width, height)
    
    # Constraint linking array to track same-pixel relationships
    constraint = numpy.zeros((width, height), dtype=int)
    for x in range(width):
        for y in range(height):
            constraint[x, y] = x  # Initially points to itself

    # Create stereogram
    for y in range(height):
        for x in range(width):
            # Calculate separation based on depth
            # depth_factor controls how much depth affects separation
            depth = depth_data[x, y] / 255.0  # Normalize to 0-1
            separation = int(pattern_width * (1.0 - args.depth_factor * depth))
            
            link = x - separation
            
            if link < 0:
                # Initial pattern region
                out_data[x, y] = int(pattern[x % pattern_width, y])
            else:
                # Follow constraint chain to find the actual source pixel
                while constraint[link, y] != link and link >= 0:
                    link = constraint[link, y]
                
                out_data[x, y] = out_data[link, y]
                constraint[x, y] = link

    out_img.save(args.output)
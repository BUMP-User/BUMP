import argparse

def parse_args():
    parser = argparse.ArgumentParser(description="BUMP Image - display and/or export BUMP files into Tiffs")
    # parser.add_argument(
    #    'video_path',
    #    type=str,
    #    help="Path to output video.",
    # )
    parser.add_argument(
        '--export',
        default=None,
        help="Skip GUI and export data from bin file(s)"
    )
    parser.add_argument(
        '--output_dir',
        type=str,
        default=None,
        help="Output directory to use instead of location of bin files"
    )
    return parser.parse_args()

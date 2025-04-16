import argparse

from mm.modern_messiah import ModernMessiah


def main(config_path):
    modern_messiah = ModernMessiah(config_path)
    modern_messiah.write_book()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate a book using the specified configuration file."
    )
    parser.add_argument(
        "--config-path",
        help="Path to the configuration file",
        dest="config_path"
    )

    args = parser.parse_args()
    main(args.config_path)


from mm.modern_messiah import ModernMessiah


def main():
    config_file = "examples/config_meta_llama_local.yaml"
    modern_messiah = ModernMessiah(config_file)
    modern_messiah.write_book()
    del modern_messiah


if __name__ == "__main__":
    main()

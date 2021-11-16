import argparse
import sys
import markovify


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file')
    parser.add_argument('-n', dest='sentences', type=int)
    parser.add_argument('-l', dest='length', type=int)
    args = parser.parse_args()
    return args


def read_text_for_model(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f'File "{filename}" not found.')
        return None


def main():
    args = parse_args()
    if not args.input_file:
        sys.exit(0)

    text = read_text_for_model(args.input_file)
    if text:
        text_model = markovify.Text(text, well_formed=False, state_size=2)

        sentences = args.sentences if args.sentences else 1
        length = args.length if args.length else 140

        for i in range(sentences):
            print(text_model.make_short_sentence(length, tries=1000))


if __name__ == '__main__':
    main()

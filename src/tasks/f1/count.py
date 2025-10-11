from pathlib import Path
import json

def main():
    difficultyFile = 'easy.json'
    json_path = Path(__file__).parent.parent / "stack" / difficultyFile
    with open(json_path, "r") as f:
        data = json.load(f)
        count = len(data)
    print(f"Number of tasks in {difficultyFile}: {count}")


if __name__ == "__main__":
    main()

    
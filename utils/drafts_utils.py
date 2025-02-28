from pathlib import Path
import pickle

drafts_directory = (
    str(Path(__file__).parent.parent.resolve()).replace("\\", "/")
    + "/assets/drafts/drafts.df"
)


def init_load_drafts():
    try:
        with open(drafts_directory, "rb") as f:
            drafts = pickle.load(f)
    except (FileNotFoundError, pickle.UnpicklingError) as e:
        print(f"Error loading drafts: {e}")
        drafts = []
    return drafts


def save_drafts(drafts):
    try:
        with open(drafts_directory, "wb") as f:
            pickle.dump(drafts, f)
    except (FileNotFoundError, pickle.PicklingError) as e:
        print(f"Error saving drafts: {e}")

from pathlib import Path

from company_inquiry.config import load_sites


def read_companys_json():
    path = Path(__file__).resolve().parent.parent / "Companys.json"
    return path.read_text(encoding="utf-8-sig")


def initial_company_array(json_str=None):
    path = Path(__file__).resolve().parent.parent / "Companys.json"
    return load_sites(path)


if __name__ == "__main__":
    company_array = initial_company_array()
    print("array:", company_array[0].company_name if company_array else "empty")

